#!/usr/bin/env python3
"""Build LlamaFactory stage=pt plaintext CPT data for cpt_v1_official_plaintext_dsb4x."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import random
import re
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/zc/wmt26")
TOKENIZER_PATH = PROJECT_ROOT / "models/base/Qwen3.5-2B"

URL_RE = re.compile(r"^(?:https?://|www\.)\S+$", re.IGNORECASE)
PATH_RE = re.compile(r"^(?:/[\w.\-]+)+/?$")
TAG_RE = re.compile(r"</?[A-Za-z][^>]{0,200}>")
SPACE_RE = re.compile(r"\s+")
SYMBOL_RE = re.compile(r"^[\W_]+$", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hsb-input", required=True, type=Path)
    parser.add_argument("--dsb-input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--dsb-repeat", type=int, default=4)
    parser.add_argument("--seed", type=int, default=202606)
    parser.add_argument("--shuffle", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit-hsb", type=int)
    parser.add_argument("--limit-dsb", type=int)
    parser.add_argument("--shuffle-buckets", type=int, default=256)
    parser.add_argument("--token-sample-size", type=int, default=20000)
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def ensure_can_write(path: Path, overwrite: bool, dry_run: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} exists; pass --overwrite to replace it.")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> tuple[str, str | None]:
    text = html.unescape(text)
    text = "".join(" " if (ord(ch) < 32 and ch not in "\t\n\r") else ch for ch in text)
    text = SPACE_RE.sub(" ", text.replace("\n", " ").replace("\r", " ").replace("\t", " ")).strip()

    if not text:
        return "", "empty"
    if "\ufffd" in text:
        return text, "replacement_char"
    if URL_RE.match(text):
        return text, "pure_url"
    if PATH_RE.match(text):
        return text, "pure_path"
    if SYMBOL_RE.match(text):
        return text, "symbols_only"

    tag_chars = sum(len(m.group(0)) for m in TAG_RE.finditer(text))
    if tag_chars and tag_chars / max(len(text), 1) > 0.25:
        return text, "html_xml_heavy"

    return text, None


def iter_records(path: Path, lang: str, limit: int | None) -> tuple[Any, Counter]:
    stats: Counter = Counter()
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if limit is not None and stats["input_rows"] >= limit:
                break
            stats["input_rows"] += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                stats["json_errors"] += 1
                continue
            text, reason = clean_text(str(obj.get("text", "")))
            if reason:
                stats[f"filtered_{reason}"] += 1
                continue
            yield {
                "text": text,
                "lang": lang,
                "source_id": obj.get("id", f"{path.name}:{line_no}"),
                "line_no": line_no,
            }
            stats["kept_rows"] += 1
            stats["kept_chars"] += len(text)
    return stats


def stable_key(seed: int, lang: str, source_id: str, repeat_idx: int) -> str:
    raw = f"{seed}\t{lang}\t{source_id}\t{repeat_idx}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


def write_bucketed(args: argparse.Namespace, temp_dir: Path) -> tuple[Counter, list[Path], list[str]]:
    warnings: list[str] = []
    stats: Counter = Counter()
    bucket_paths = [temp_dir / f"bucket_{i:04d}.jsonl" for i in range(args.shuffle_buckets)]
    bucket_files = [p.open("w", encoding="utf-8") for p in bucket_paths]
    try:
        sources = [
            ("hsb", args.hsb_input, 1, args.limit_hsb),
            ("dsb", args.dsb_input, args.dsb_repeat, args.limit_dsb),
        ]
        for lang, path, repeat, limit in sources:
            lang_iter = iter_records(path, lang, limit)
            try:
                while True:
                    rec = next(lang_iter)
                    stats[f"{lang}_kept_unique"] += 1
                    for repeat_idx in range(repeat):
                        key = stable_key(args.seed, lang, str(rec["source_id"]), repeat_idx)
                        bucket = int(key[:8], 16) % args.shuffle_buckets if args.shuffle else 0
                        bucket_files[bucket].write(json.dumps({"key": key, "text": rec["text"], "lang": lang}, ensure_ascii=False) + "\n")
                        stats[f"{lang}_output_rows"] += 1
                        stats[f"{lang}_output_chars"] += len(rec["text"])
            except StopIteration as stop:
                if isinstance(stop.value, Counter):
                    stats.update({f"{lang}_{k}": v for k, v in stop.value.items()})
    finally:
        for f in bucket_files:
            f.close()

    return stats, bucket_paths, warnings


def load_tokenizer(warnings: list[str]):
    try:
        from transformers import AutoTokenizer

        return AutoTokenizer.from_pretrained(str(TOKENIZER_PATH), trust_remote_code=True, local_files_only=True)
    except Exception as err:  # pragma: no cover - environment dependent
        warnings.append(f"tokenizer_stats_skipped: {err}")
        return None


def estimate_tokens(output_path: Path, sample_size: int, seed: int, warnings: list[str]) -> dict[str, Any]:
    tokenizer = load_tokenizer(warnings)
    if tokenizer is None:
        return {"token_stats_skipped": True, "tokenizer_path": str(TOKENIZER_PATH), "tokenizer_error": warnings[-1] if warnings else "unknown"}

    rng = random.Random(seed)
    sample: list[str] = []
    total_rows = 0
    by_lang_rows: Counter = Counter()
    by_lang_chars: Counter = Counter()
    by_lang_sample_tokens: Counter = Counter()
    by_lang_sample_rows: Counter = Counter()

    with output_path.open(encoding="utf-8") as f:
        for line in f:
            total_rows += 1
            obj = json.loads(line)
            text = obj["text"]
            # During output we intentionally omit lang; infer sample reservoir globally only.
            if len(sample) < sample_size:
                sample.append(text)
            else:
                j = rng.randint(1, total_rows)
                if j <= sample_size:
                    sample[j - 1] = text

    token_lengths = [len(tokenizer.encode(text, add_special_tokens=False)) for text in sample]
    avg_tokens = sum(token_lengths) / len(token_lengths) if token_lengths else 0.0
    return {
        "token_stats_skipped": False,
        "tokenizer_path": str(TOKENIZER_PATH),
        "token_estimation": "global reservoir sample",
        "token_sample_size": len(sample),
        "estimated_total_tokens": int(round(avg_tokens * total_rows)),
        "sample_avg_tokens_per_row": avg_tokens,
        "sample_token_lengths": percentile_summary(token_lengths),
    }


def load_interim_token_estimate(args: argparse.Namespace, warnings: list[str]) -> dict[str, Any]:
    token_stats_path = args.hsb_input.parent / "token_stats.json"
    try:
        stats = json.loads(token_stats_path.read_text(encoding="utf-8"))
        hsb_tokens = int(stats["by_lang"]["hsb"]["token_count"])
        dsb_tokens = int(stats["by_lang"]["dsb"]["token_count"]) * args.dsb_repeat
        total = hsb_tokens + dsb_tokens
        return {
            "source": rel(token_stats_path),
            "method": "interim exact token stats scaled by processed repeat",
            "hsb_tokens": hsb_tokens,
            "dsb_tokens": dsb_tokens,
            "total_tokens": total,
            "hsb_token_ratio": hsb_tokens / total if total else None,
            "dsb_token_ratio": dsb_tokens / total if total else None,
        }
    except Exception as err:
        warnings.append(f"interim_token_ratio_skipped: {err}")
        return {"method": "unavailable", "error": str(err)}


def percentile_summary(values: list[int]) -> dict[str, int | None]:
    if not values:
        return {k: None for k in ["p50", "p90", "p95", "p99", "max"]}
    vals = sorted(values)
    def pct(p: float) -> int:
        idx = min(len(vals) - 1, int(round((len(vals) - 1) * p)))
        return vals[idx]
    return {"p50": pct(0.50), "p90": pct(0.90), "p95": pct(0.95), "p99": pct(0.99), "max": vals[-1]}


def finalize_output(args: argparse.Namespace, bucket_paths: list[Path]) -> Counter:
    stats: Counter = Counter()
    rng = random.Random(args.seed)
    ordered_buckets = list(bucket_paths)
    if args.shuffle:
        rng.shuffle(ordered_buckets)

    with args.output.open("w", encoding="utf-8") as out:
        for bucket_path in ordered_buckets:
            if not bucket_path.exists() or bucket_path.stat().st_size == 0:
                continue
            rows = [json.loads(line) for line in bucket_path.open(encoding="utf-8")]
            if args.shuffle:
                rows.sort(key=lambda x: x["key"])
            for row in rows:
                out.write(json.dumps({"text": row["text"]}, ensure_ascii=False) + "\n")
                stats["output_rows"] += 1
    return stats


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    def scalar(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        return json.dumps(str(value), ensure_ascii=False)

    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for k2, v2 in value.items():
                lines.append(f"  {k2}: {scalar(v2)}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {scalar(item)}")
        else:
            lines.append(f"{key}: {scalar(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(path: Path, manifest: dict[str, Any], token_stats: dict[str, Any]) -> None:
    scaled = manifest.get("scaled_interim_token_estimate", {})
    lines = [
        "# CPT V1 Official Plaintext DSB4X Processed Data",
        "",
        f"- created_at: {manifest['created_at']}",
        f"- output: `{manifest['output']}`",
        f"- hsb_input: `{manifest['inputs']['hsb']}`",
        f"- dsb_input: `{manifest['inputs']['dsb']}`",
        f"- hsb_repeat: {manifest['repeat']['hsb']}",
        f"- dsb_repeat: {manifest['repeat']['dsb']}",
        f"- shuffle: {str(manifest['shuffle']).lower()}",
        f"- seed: {manifest['seed']}",
        "",
        "## Counts",
        "",
        f"- hsb unique kept: {manifest['counts']['hsb_kept_unique']}",
        f"- dsb unique kept: {manifest['counts']['dsb_kept_unique']}",
        f"- hsb output rows: {manifest['counts']['hsb_output_rows']}",
        f"- dsb output rows: {manifest['counts']['dsb_output_rows']}",
        f"- total output rows: {manifest['counts']['output_rows']}",
        "",
        "## Token Estimate",
        "",
    ]
    if token_stats.get("token_stats_skipped"):
        lines.append(f"- token stats skipped: {token_stats.get('tokenizer_error')}")
    else:
        lines.extend([
            f"- tokenizer: `{token_stats['tokenizer_path']}`",
            f"- method: {token_stats['token_estimation']}",
            f"- sample size: {token_stats['token_sample_size']}",
            f"- estimated total tokens: {token_stats['estimated_total_tokens']}",
            f"- sample avg tokens / row: {token_stats['sample_avg_tokens_per_row']:.2f}",
            f"- sample token length distribution: `{token_stats['sample_token_lengths']}`",
        ])
    if scaled.get("total_tokens") is not None:
        lines.extend([
            f"- scaled interim exact tokens: {scaled['total_tokens']}",
            f"- scaled hsb tokens: {scaled['hsb_tokens']} ({scaled['hsb_token_ratio']:.2%})",
            f"- scaled dsb tokens: {scaled['dsb_tokens']} ({scaled['dsb_token_ratio']:.2%})",
        ])
    lines.extend([
        "",
        "## Filtering",
        "",
        "Light filtering was applied during processed-data construction: empty text, replacement character rows, HTML/XML-heavy rows, pure URL/path rows, and symbol-only rows were removed.",
        "",
        "Filtered counts are recorded in the manifest. Final training JSONL contains only the `text` field for LlamaFactory `stage=pt`.",
        "",
        "## Notes",
        "",
        "- Input interim data had already been exact-deduplicated before this stage.",
        "- DSB repeat is intentional sampling, so no repeat-after-dedup was run.",
        "- This dataset uses only official Sorbian plaintext CPT data: hsb/dsb monolingual train plus hsb/dsb target-side parallel train text.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.dsb_repeat < 1:
        raise ValueError("--dsb-repeat must be >= 1")
    if args.shuffle_buckets < 1:
        raise ValueError("--shuffle-buckets must be >= 1")

    for path in [args.hsb_input, args.dsb_input]:
        if not path.exists():
            raise FileNotFoundError(path)

    for path in [args.output, args.manifest, args.report]:
        ensure_can_write(path, args.overwrite, args.dry_run)

    if args.dry_run:
        print("DRY RUN")
        print(f"hsb_input={args.hsb_input}")
        print(f"dsb_input={args.dsb_input}")
        print(f"output={args.output}")
        print(f"manifest={args.manifest}")
        print(f"report={args.report}")
        print(f"dsb_repeat={args.dsb_repeat} shuffle={args.shuffle} seed={args.seed}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    tmp_root = Path(tempfile.mkdtemp(prefix="cpt_dsb4x_build_", dir=str(args.output.parent)))
    tmp_output = args.output.with_suffix(args.output.suffix + ".tmp")
    try:
        bucket_stats, bucket_paths, bucket_warnings = write_bucketed(args, tmp_root)
        warnings.extend(bucket_warnings)
        args.output = tmp_output
        output_stats = finalize_output(args, bucket_paths)
        token_stats = estimate_tokens(tmp_output, args.token_sample_size, args.seed, warnings)
        scaled_token_estimate = load_interim_token_estimate(args, warnings)

        manifest = {
            "dataset_name": "cpt_v1_official_plaintext_dsb4x",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "output": rel(tmp_output.with_suffix("")),
            "actual_output": rel(tmp_output),
            "inputs": {"hsb": rel(args.hsb_input), "dsb": rel(args.dsb_input)},
            "repeat": {"hsb": 1, "dsb": args.dsb_repeat},
            "shuffle": bool(args.shuffle),
            "seed": args.seed,
            "light_filtering": True,
            "counts": dict(bucket_stats | output_stats),
            "token_stats": token_stats,
            "scaled_interim_token_estimate": scaled_token_estimate,
            "warnings": warnings,
            "notes": "DSB repeat is intentional processed-stage sampling. Do not deduplicate after repeat.",
        }

        final_output = Path(str(tmp_output).removesuffix(".tmp"))
        os.replace(tmp_output, final_output)
        manifest["output"] = rel(final_output)
        manifest.pop("actual_output", None)
        write_yaml(args.manifest, manifest)
        write_report(args.report, manifest, token_stats)
        print(f"Wrote {final_output}")
        print(f"Wrote {args.manifest}")
        print(f"Wrote {args.report}")
        return 0
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
        if tmp_output.exists():
            tmp_output.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
