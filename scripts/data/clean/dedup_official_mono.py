#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict

from official_mono_common import INTERIM, ensure_dirs, read_jsonl, refuse_overwrite, sha1_normalized, stable_id

IN_PATH = INTERIM / "cleaned_after_leakage.jsonl"
OUT_HSB = INTERIM / "mono_hsb_clean.jsonl"
OUT_DSB = INTERIM / "mono_dsb_clean.jsonl"
OUT_ALL = INTERIM / "mono_all_clean.jsonl"
OUT_REPORT = INTERIM / "dedup_report.json"
OUT_DUPS = INTERIM / "duplicate_groups_sample.jsonl"

SOURCE_PRIORITY = {"wmt26": 0, "wmt25": 1, "wmt22": 2}
KIND_PRIORITY = {"mono": 0, "parallel_target": 1}


def rank(row: dict) -> tuple:
    return (
        SOURCE_PRIORITY.get(row.get("source"), 99),
        KIND_PRIORITY.get(row.get("source_kind"), 99),
        -len(row.get("text", "")),
        int(row.get("line_no") or 10**12),
        row.get("id", ""),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    ensure_dirs()
    groups: dict[str, list[dict]] = defaultdict(list)
    input_count = 0
    for row in read_jsonl(IN_PATH):
        input_count += 1
        if args.limit and input_count > args.limit:
            break
        h = sha1_normalized(row["text"])
        groups[h].append(row)

    kept = []
    duplicate_groups_sample = []
    duplicate_removed = 0
    duplicate_dist = Counter()
    for h, rows in groups.items():
        rows_sorted = sorted(rows, key=rank)
        winner = dict(rows_sorted[0])
        winner["normalized_sha1"] = h
        winner["duplicate_count"] = len(rows_sorted) - 1
        winner["id"] = stable_id(winner["source"], winner["source_path"], winner["source_kind"], winner["lang"], h)
        kept.append(winner)
        if len(rows_sorted) > 1:
            duplicate_removed += len(rows_sorted) - 1
            duplicate_dist[(winner.get("lang"), winner.get("source"), winner.get("source_kind"))] += len(rows_sorted) - 1
            if len(duplicate_groups_sample) < 200:
                duplicate_groups_sample.append(
                    {
                        "normalized_sha1": h,
                        "duplicate_count": len(rows_sorted) - 1,
                        "kept": {
                            "source": winner.get("source"),
                            "source_path": winner.get("source_path"),
                            "source_kind": winner.get("source_kind"),
                            "lang": winner.get("lang"),
                            "line_no": winner.get("line_no"),
                            "text_preview": winner.get("text", "")[:200],
                        },
                        "duplicates": [
                            {
                                "source": row.get("source"),
                                "source_path": row.get("source_path"),
                                "source_kind": row.get("source_kind"),
                                "lang": row.get("lang"),
                                "line_no": row.get("line_no"),
                            }
                            for row in rows_sorted[1:6]
                        ],
                    }
                )

    kept.sort(key=lambda r: (r["lang"], r["source"], r["source_kind"], r["source_path"], r["line_no"]))
    by_lang = Counter(row["lang"] for row in kept)
    by_source = Counter(row["source"] for row in kept)
    by_kind = Counter(row["source_kind"] for row in kept)
    report = {
        "input_count": input_count if not args.limit else min(input_count, args.limit),
        "unique_count": len(kept),
        "duplicate_removed_count": duplicate_removed,
        "by_lang": dict(sorted(by_lang.items())),
        "by_source": dict(sorted(by_source.items())),
        "by_source_kind": dict(sorted(by_kind.items())),
        "duplicate_removed_by_kept_lang_source_kind": {
            "|".join(map(str, key)): value for key, value in sorted(duplicate_dist.items())
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    refuse_overwrite([OUT_HSB, OUT_DSB, OUT_ALL, OUT_REPORT, OUT_DUPS], args.overwrite)
    with OUT_ALL.open("w", encoding="utf-8") as all_f, OUT_HSB.open("w", encoding="utf-8") as hsb_f, OUT_DSB.open("w", encoding="utf-8") as dsb_f:
        for row in kept:
            line = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            all_f.write(line)
            if row["lang"] == "hsb":
                hsb_f.write(line)
            elif row["lang"] == "dsb":
                dsb_f.write(line)
    with OUT_DUPS.open("w", encoding="utf-8") as f:
        for row in duplicate_groups_sample:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
