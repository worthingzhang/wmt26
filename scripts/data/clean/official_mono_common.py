#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import re
import statistics
import tarfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator

ROOT = Path("/home/zc/wmt26")
RAW_ROOT = ROOT / "data" / "raw" / "official"
INTERIM = ROOT / "data" / "interim" / "sorbian" / "cpt_v1_official_mono"
MANIFESTS = ROOT / "data" / "manifests"
DOCS = ROOT / "docs" / "data"
LOGS = ROOT / "logs" / "data_clean"

RAW_REPOS = {
    "llms-limited-resources2026": RAW_ROOT / "llms-limited-resources2026",
    "llms-limited-resources2025": RAW_ROOT / "llms-limited-resources2025",
    "WMT22_UnsupVeryLowResMT_Data": RAW_ROOT / "WMT22_UnsupVeryLowResMT_Data",
}

TASK_MARKERS = {"qa", "sc", "gc", "mr"}
HELDOUT_MARKERS = {"dev", "devel", "valid", "validation", "test", "eval", "sample"}
TEXT_SUFFIXES = {
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".md",
    ".de",
    ".hsb",
    ".dsb",
    ".uk",
    ".en",
    ".cs",
    ".licence",
    ".license",
}


def ensure_dirs() -> None:
    for path in (INTERIM, MANIFESTS, DOCS, LOGS):
        path.mkdir(parents=True, exist_ok=True)


def refuse_overwrite(paths: Iterable[Path], overwrite: bool) -> None:
    existing = [str(p) for p in paths if p.exists()]
    if existing and not overwrite:
        raise SystemExit("Refusing to overwrite existing files; pass --overwrite:\n" + "\n".join(existing))


def repo_for_path(path: Path) -> str:
    for name, root in RAW_REPOS.items():
        try:
            path.relative_to(root)
            return name
        except ValueError:
            continue
    return "unknown"


def rel_to_repo(path: Path) -> str:
    repo = repo_for_path(path)
    if repo in RAW_REPOS:
        return str(path.relative_to(RAW_REPOS[repo]))
    return str(path)


def source_short(repo: str) -> str:
    if repo == "llms-limited-resources2026":
        return "wmt26"
    if repo == "llms-limited-resources2025":
        return "wmt25"
    if repo == "WMT22_UnsupVeryLowResMT_Data":
        return "wmt22"
    return "unknown"


def path_tokens(path: Path) -> list[str]:
    text = str(path).lower()
    return [tok for tok in re.split(r"[^a-z0-9]+", text) if tok]


def filename_signals(path: Path) -> list[str]:
    toks = set(path_tokens(path))
    signals = sorted(toks & (TASK_MARKERS | HELDOUT_MARKERS | {"train", "mono", "monolingual", "parallel", "mt", "baseline", "dummy", "readme", "licence", "license"}))
    name = path.name.lower()
    if "monolingual" in name and "monolingual" not in signals:
        signals.append("monolingual")
    return signals


def inner_suffixes(path: Path) -> list[str]:
    suffixes = list(path.suffixes)
    if suffixes and suffixes[-1] == ".gz" and len(suffixes) > 1:
        return suffixes[:-1]
    return suffixes


def extension(path: Path) -> str:
    suffixes = path.suffixes
    if suffixes[-2:] == [".tar", ".gz"]:
        return ".tar.gz"
    if suffixes and suffixes[-1] == ".tgz":
        return ".tgz"
    if suffixes and suffixes[-1] == ".gz" and len(suffixes) > 1:
        return "".join(suffixes[-2:])
    return suffixes[-1].lower() if suffixes else ""


def is_textish(path: Path) -> bool:
    ext = extension(path)
    if ext in {".tar.gz", ".tgz"}:
        return False
    if ext.endswith(".gz"):
        ext = Path(path.stem).suffix.lower()
    return ext.lower() in TEXT_SUFFIXES or path.name.upper() in {"LICENCE", "LICENSE"}


def open_text(path: Path) -> Iterator[str]:
    if path.suffix == ".gz" and not str(path).endswith((".tar.gz", ".tgz")):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as f:
            yield from f
    else:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            yield from f


def read_text_sample(path: Path, max_bytes: int = 65536) -> str:
    if path.suffix == ".gz" and not str(path).endswith((".tar.gz", ".tgz")):
        with gzip.open(path, "rb") as f:
            data = f.read(max_bytes)
    else:
        with path.open("rb") as f:
            data = f.read(max_bytes)
    return data.decode("utf-8", errors="replace")


def count_lines(path: Path, limit: int | None = None) -> int | None:
    if not is_textish(path):
        return None
    n = 0
    try:
        for n, _ in enumerate(open_text(path), 1):
            if limit and n >= limit:
                break
        return n
    except Exception:
        return None


def detected_encoding(path: Path) -> str:
    if not is_textish(path):
        return ""
    try:
        sample = read_text_sample(path, 8192)
    except Exception:
        return "unreadable"
    return "utf-8" if "\ufffd" not in sample else "utf-8-with-replacement"


def guess_lang(path: Path) -> str:
    toks = set(path_tokens(path))
    name = path.name.lower()
    suffixes = inner_suffixes(path)
    if suffixes:
        last = suffixes[-1].lower()
        if last == ".hsb":
            return "hsb"
        if last == ".dsb":
            return "dsb"
        if last == ".de":
            return "deu"
    if re.search(r"(^|[-_.])hsb($|[-_.])", name) or "hsb" in toks:
        return "hsb"
    if re.search(r"(^|[-_.])dsb($|[-_.])", name) or "dsb" in toks:
        return "dsb"
    if "deu" in toks or "de" in toks or name.endswith(".de") or "-de." in name:
        return "deu"
    return "unknown"


def infer_parallel_target_lang(path: Path) -> str | None:
    name = path.name.lower()
    stem = name
    changed = True
    removable = (".gz", ".csv", ".tsv", ".txt", ".hsb", ".dsb", ".de")
    while changed:
        changed = False
        for suffix in removable:
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                changed = True
                break
    patterns = [
        (("de-hsb", "de_hsb", "deu-hsb", "deu_hsb"), "hsb"),
        (("de-dsb", "de_dsb", "deu-dsb", "deu_dsb"), "dsb"),
        (("hsb-dsb", "hsb_dsb"), "dsb"),
        (("dsb-hsb", "dsb_hsb"), "hsb"),
        (("hsb-de", "hsb_de", "hsb-deu", "hsb_deu"), "deu"),
        (("dsb-de", "dsb_de", "dsb-deu", "dsb_deu"), "deu"),
    ]
    for needles, target in patterns:
        if any(needle in stem for needle in needles):
            return target
    return None


def classify_file(path: Path) -> dict[str, Any]:
    rel = rel_to_repo(path)
    rel_lower = rel.lower()
    name = path.name.lower()
    toks = set(path_tokens(path))
    signals = filename_signals(path)
    lang = guess_lang(path)
    ext = extension(path)
    target_lang = infer_parallel_target_lang(path)

    data_type = "unknown"
    include = False
    reason = "needs review"

    if "/.git/" in str(path) or ".git/" in rel_lower:
        data_type = "metadata"
        reason = "git internals skipped"
    elif name in {"readme.md", "licence", "license"} or ext in {".md"}:
        data_type = "metadata"
        reason = "readme/license/metadata"
    elif "dummy_submission" in rel_lower or "baseline_dev" in rel_lower or name.endswith("_preds.jsonl"):
        data_type = "metadata"
        reason = "baseline or dummy submission output"
    elif "ukrainian/" in rel_lower or rel_lower.startswith("ukrainian/"):
        data_type = "task_data"
        reason = "Ukrainian data excluded from Sorbian CPT v1"
    elif any(marker in toks for marker in HELDOUT_MARKERS) or any(marker in name for marker in ("devtest", "validation")):
        data_type = "heldout"
        reason = "path/name contains heldout signal"
    elif any(marker in toks for marker in TASK_MARKERS) or "/qa/" in rel_lower or "/sc/" in rel_lower or "/gc/" in rel_lower or "/mr/" in rel_lower:
        data_type = "task_data"
        reason = "QA/SC/GC/MR task data excluded from CPT v1"
    elif "sorbian" not in rel_lower and "hsb" not in rel_lower and "dsb" not in rel_lower and "wmt22" not in source_short(repo_for_path(path)):
        data_type = "unknown"
        reason = "not clearly Sorbian hsb/dsb"
    elif ("monolingual" in name or "mono" in name or "wikipedia" in name or name.startswith(("witaj_", "wiki_", "web_", "sorbian_institute_")) or name in {"hsb_monolingual.txt.gz", "mono.dsb.gz"}) and lang in {"hsb", "dsb"}:
        data_type = "train_mono"
        include = True
        reason = "explicit hsb/dsb monolingual train source"
    elif ("train" in toks or name.startswith("train")) and ext in {".csv", ".csv.gz", ".tsv", ".tsv.gz"} and target_lang in {"hsb", "dsb"}:
        data_type = "train_parallel"
        include = True
        lang = target_lang
        reason = "explicit train parallel table with hsb/dsb target column"
    elif ("train" in toks or name.startswith("train")) and target_lang in {"hsb", "dsb"} and lang == target_lang and ext not in {".tar.gz", ".tgz", ".csv", ".csv.gz", ".tsv", ".tsv.gz"}:
        data_type = "train_parallel"
        include = True
        reason = "explicit train parallel hsb/dsb target side"
    else:
        data_type = "unknown"
        reason = "not confidently classifiable for CPT v1"

    return {
        "absolute_path": str(path),
        "relative_path": rel,
        "repo_name": repo_for_path(path),
        "extension": ext,
        "filename_signals": ",".join(signals),
        "guessed_lang": lang,
        "guessed_data_type": data_type,
        "include_in_cpt_v1_candidate": include,
        "reason": reason,
    }


def normalize_key(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def sha1_normalized(text: str) -> str:
    return hashlib.sha1(normalize_key(text).encode("utf-8")).hexdigest()


def stable_id(*parts: object) -> str:
    raw = "\t".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            n += 1
    return n


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    import yaml

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def extract_json_strings(obj: Any) -> Iterator[tuple[str, str]]:
    if isinstance(obj, str):
        yield "", obj
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            for key, value in extract_json_strings(item):
                yield f"{i}.{key}".strip("."), value
    elif isinstance(obj, dict):
        for k, v in obj.items():
            for key, value in extract_json_strings(v):
                yield f"{k}.{key}".strip("."), value


def iter_heldout_texts(path: Path, lang_hint: str) -> Iterator[tuple[str, int, str]]:
    ext = extension(path)
    if ext in {".tar.gz", ".tgz"}:
        try:
            with tarfile.open(path, "r:*") as tar:
                for member in tar.getmembers():
                    if not member.isfile():
                        continue
                    member_name = member.name
                    if Path(member_name).suffix.lower() not in TEXT_SUFFIXES and not member_name.endswith((".txt", ".tsv", ".csv", ".jsonl", ".json", ".de", ".hsb", ".dsb")):
                        continue
                    fh = tar.extractfile(member)
                    if fh is None:
                        continue
                    text = io.TextIOWrapper(fh, encoding="utf-8", errors="replace")
                    for i, line in enumerate(text, 1):
                        for value in split_possible_structured_text(line, member_name):
                            yield member_name, i, value
        except Exception:
            return
        return

    try:
        for i, line in enumerate(open_text(path), 1):
            for value in split_possible_structured_text(line, path.name):
                yield str(path), i, value
    except Exception:
        return


def split_possible_structured_text(line: str, name: str) -> Iterator[str]:
    stripped = line.strip()
    if not stripped:
        return
    if name.endswith(".jsonl") or name.endswith(".json"):
        try:
            obj = json.loads(stripped)
            for _key, value in extract_json_strings(obj):
                if value.strip():
                    yield value
            return
        except Exception:
            pass
    if "\t" in stripped:
        for part in stripped.split("\t"):
            if part.strip():
                yield part
        return
    yield stripped


def percentile(values: list[int], pct: float) -> int | None:
    if not values:
        return None
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round((pct / 100) * (len(values) - 1))))
    return values[idx]


def distribution(values: list[int]) -> dict[str, int | None]:
    return {
        "p50": percentile(values, 50),
        "p90": percentile(values, 90),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "max": max(values) if values else None,
    }


def counter_to_dict(counter: Counter) -> dict[str, int]:
    return {str(k): int(v) for k, v in sorted(counter.items())}


def nested_counter_to_dict(counter: Counter) -> dict[str, int]:
    return counter_to_dict(counter)
