#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter

from official_mono_common import INTERIM, ensure_dirs, read_jsonl, refuse_overwrite, sha1_normalized

IN_CLEAN = INTERIM / "cleaned_before_leakage.jsonl"
IN_HELDOUT = INTERIM / "heldout_hashes.jsonl"
OUT_CLEAN = INTERIM / "cleaned_after_leakage.jsonl"
OUT_REPORT = INTERIM / "leakage_report.json"
OUT_REMOVED = INTERIM / "leakage_removed_examples.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    ensure_dirs()
    heldout = {row["hash"] for row in read_jsonl(IN_HELDOUT)}
    kept = []
    removed = []
    removed_dist = Counter()
    candidate_count = 0
    for row in read_jsonl(IN_CLEAN):
        candidate_count += 1
        if args.limit and candidate_count > args.limit:
            break
        h = sha1_normalized(row["text"])
        if h in heldout:
            item = dict(row)
            item["normalized_sha1"] = h
            removed.append(item)
            removed_dist[(row.get("source"), row.get("lang"), row.get("source_kind"))] += 1
        else:
            kept.append(row)

    report = {
        "heldout_hash_count": len(heldout),
        "candidate_count": candidate_count if not args.limit else min(candidate_count, args.limit),
        "removed_by_heldout_count": len(removed),
        "remaining_count": len(kept),
        "removed_examples_by_source_lang_source_kind": {
            "|".join(map(str, key)): value for key, value in sorted(removed_dist.items())
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    refuse_overwrite([OUT_CLEAN, OUT_REPORT, OUT_REMOVED], args.overwrite)
    with OUT_CLEAN.open("w", encoding="utf-8") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with OUT_REMOVED.open("w", encoding="utf-8") as f:
        for row in removed[:1000]:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
