#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from official_mono_common import (
    INTERIM,
    MANIFESTS,
    ensure_dirs,
    extension,
    load_yaml,
    open_text,
    refuse_overwrite,
    source_short,
    stable_id,
)

FILE_MAP = MANIFESTS / "cpt_v1_official_mono_file_map.yaml"
OUT_HSB = INTERIM / "candidate_mono_hsb.jsonl"
OUT_DSB = INTERIM / "candidate_mono_dsb.jsonl"
OUT_ALL = INTERIM / "candidate_mono_all.jsonl"
OUT_REPORT = INTERIM / "extraction_report.json"
OUT_ERRORS = INTERIM / "parse_errors.jsonl"


def emit_record(item: dict, source_kind: str, lang: str, line_no: int, text: str) -> dict:
    return {
        "id": stable_id(item["repo_name"], item["relative_path"], source_kind, lang, line_no, text),
        "source": source_short(item["repo_name"]),
        "source_path": item["relative_path"],
        "source_kind": source_kind,
        "lang": lang,
        "line_no": line_no,
        "text": text.rstrip("\n\r"),
    }


def extract_plain_lines(item: dict, source_kind: str, lang: str):
    path = Path(item["absolute_path"])
    for line_no, line in enumerate(open_text(path), 1):
        text = line.rstrip("\n\r")
        if text:
            yield emit_record(item, source_kind, lang, line_no, text)


def extract_delimited(item: dict, source_kind: str, allowed_langs: set[str], errors: list[dict]):
    path = Path(item["absolute_path"])
    ext = extension(path)
    delimiter = "\t" if ".tsv" in ext or path.name.endswith(".tsv.gz") else ","
    try:
        lines = open_text(path)
        reader = csv.DictReader(lines, delimiter=delimiter)
        if not reader.fieldnames:
            errors.append({"source_path": item["relative_path"], "error": "missing_header"})
            return
        fields = [f.strip() for f in reader.fieldnames]
        target_fields = [f for f in fields if f in allowed_langs]
        if not target_fields:
            errors.append({"source_path": item["relative_path"], "error": "no_hsb_dsb_column", "fields": fields})
            return
        for row_idx, row in enumerate(reader, 2):
            for field in target_fields:
                value = row.get(field)
                if value:
                    yield emit_record(item, source_kind, field, row_idx, value)
    except Exception as exc:
        errors.append({"source_path": item["relative_path"], "error": type(exc).__name__, "message": str(exc)})


def extract_item(item: dict, source_kind: str, errors: list[dict]):
    path = Path(item["absolute_path"])
    lang = item.get("lang")
    ext = extension(path)
    if ext.endswith(".csv") or ext.endswith(".tsv"):
        allowed = {"hsb", "dsb"} if source_kind == "mono" else {lang}
        yield from extract_delimited(item, source_kind, allowed, errors)
    elif lang in {"hsb", "dsb"}:
        yield from extract_plain_lines(item, source_kind, lang)
    else:
        errors.append({"source_path": item["relative_path"], "error": "unknown_lang_for_plain_text"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    ensure_dirs()
    data = load_yaml(FILE_MAP)
    rows = []
    errors: list[dict] = []
    by_lang = Counter()
    by_source_kind = Counter()
    by_source = Counter()

    for source_kind, key in (("mono", "train_mono_candidates"), ("parallel_target", "train_parallel_candidates")):
        for item in data.get(key, []):
            for rec in extract_item(item, source_kind, errors):
                rows.append(rec)
                by_lang[rec["lang"]] += 1
                by_source_kind[rec["source_kind"]] += 1
                by_source[rec["source"]] += 1
                if args.limit and len(rows) >= args.limit:
                    break
            if args.limit and len(rows) >= args.limit:
                break
        if args.limit and len(rows) >= args.limit:
            break

    report = {
        "candidate_count": len(rows),
        "by_lang": dict(sorted(by_lang.items())),
        "by_source_kind": dict(sorted(by_source_kind.items())),
        "by_source": dict(sorted(by_source.items())),
        "parse_error_count": len(errors),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    refuse_overwrite([OUT_HSB, OUT_DSB, OUT_ALL, OUT_REPORT, OUT_ERRORS], args.overwrite)
    with OUT_ALL.open("w", encoding="utf-8") as all_f, OUT_HSB.open("w", encoding="utf-8") as hsb_f, OUT_DSB.open("w", encoding="utf-8") as dsb_f:
        for row in rows:
            line = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            all_f.write(line)
            if row["lang"] == "hsb":
                hsb_f.write(line)
            elif row["lang"] == "dsb":
                dsb_f.write(line)
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUT_ERRORS.open("w", encoding="utf-8") as f:
        for err in errors:
            f.write(json.dumps(err, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
