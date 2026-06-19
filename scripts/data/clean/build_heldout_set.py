#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from official_mono_common import (
    INTERIM,
    MANIFESTS,
    ensure_dirs,
    iter_heldout_texts,
    load_yaml,
    normalize_key,
    refuse_overwrite,
    sha1_normalized,
)

FILE_MAP = MANIFESTS / "cpt_v1_official_mono_file_map.yaml"
OUT_HASHES = INTERIM / "heldout_hashes.jsonl"
OUT_REPORT = INTERIM / "heldout_report.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    ensure_dirs()
    data = load_yaml(FILE_MAP)
    rows = []
    seen = set()
    by_lang = Counter()
    by_source = Counter()
    scanned_files = 0

    for item in data.get("heldout_candidates", []):
        path = Path(item["absolute_path"])
        lang = item.get("lang") or "unknown"
        scanned_files += 1
        for member, line_no, text in iter_heldout_texts(path, lang):
            norm = normalize_key(text)
            if not norm:
                continue
            h = sha1_normalized(text)
            if h in seen:
                continue
            seen.add(h)
            rec = {
                "hash": h,
                "lang": lang if lang in {"hsb", "dsb"} else "unknown",
                "source_path": item["relative_path"],
                "member": member,
                "line_no": line_no,
                "text_preview": text.strip()[:200],
            }
            rows.append(rec)
            by_lang[rec["lang"]] += 1
            by_source[item["relative_path"]] += 1
            if args.limit and len(rows) >= args.limit:
                break
        if args.limit and len(rows) >= args.limit:
            break

    report = {
        "scanned_files": scanned_files,
        "heldout_hash_count": len(rows),
        "by_lang": dict(sorted(by_lang.items())),
        "by_source_path": dict(sorted(by_source.items())),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    refuse_overwrite([OUT_HASHES, OUT_REPORT], args.overwrite)
    with OUT_HASHES.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
