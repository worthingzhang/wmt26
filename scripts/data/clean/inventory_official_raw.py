#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from official_mono_common import (
    DOCS,
    MANIFESTS,
    RAW_REPOS,
    classify_file,
    count_lines,
    detected_encoding,
    dump_yaml,
    ensure_dirs,
    refuse_overwrite,
)


OUT_TSV = MANIFESTS / "raw_file_inventory.tsv"
OUT_MD = DOCS / "RAW_DATA_INVENTORY.md"
OUT_MAP = MANIFESTS / "cpt_v1_official_mono_file_map.yaml"


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root in RAW_REPOS.values():
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if ".git" in path.parts:
                continue
            files.append(path)
    return sorted(files)


def build_inventory(line_limit: int | None = None) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in iter_files():
        row = classify_file(path)
        row["file_size_bytes"] = path.stat().st_size
        row["line_count"] = count_lines(path, line_limit)
        row["detected_encoding"] = detected_encoding(path)
        rows.append(row)
    return rows


def build_map(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    mapping = {
        "train_mono_candidates": [],
        "train_parallel_candidates": [],
        "heldout_candidates": [],
        "excluded_task_or_metadata": [],
        "unknown_needs_review": [],
    }
    for row in rows:
        item = {
            "repo_name": row["repo_name"],
            "relative_path": row["relative_path"],
            "absolute_path": row["absolute_path"],
            "lang": row["guessed_lang"],
            "data_type": row["guessed_data_type"],
            "reason": row["reason"],
        }
        data_type = row["guessed_data_type"]
        if data_type == "train_mono" and row["include_in_cpt_v1_candidate"]:
            mapping["train_mono_candidates"].append(item)
        elif data_type == "train_parallel" and row["include_in_cpt_v1_candidate"]:
            mapping["train_parallel_candidates"].append(item)
        elif data_type == "heldout":
            mapping["heldout_candidates"].append(item)
        elif data_type in {"task_data", "metadata"}:
            mapping["excluded_task_or_metadata"].append(item)
        else:
            mapping["unknown_needs_review"].append(item)
    return mapping


def write_outputs(rows: list[dict[str, object]], mapping: dict[str, object]) -> None:
    fields = [
        "absolute_path",
        "relative_path",
        "repo_name",
        "file_size_bytes",
        "extension",
        "line_count",
        "detected_encoding",
        "filename_signals",
        "guessed_lang",
        "guessed_data_type",
        "include_in_cpt_v1_candidate",
        "reason",
    ]
    with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})
    dump_yaml(OUT_MAP, mapping)

    counts = Counter(row["guessed_data_type"] for row in rows)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# Raw Data Inventory\n\n")
        f.write("Scope: official raw repositories only. `.git` internals are skipped.\n\n")
        f.write(f"Total inventoried files: {len(rows)}\n\n")
        f.write("## Counts By Type\n\n")
        for key, value in sorted(counts.items()):
            f.write(f"- {key}: {value}\n")
        f.write("\n## CPT V1 File Map Counts\n\n")
        for key, value in mapping.items():
            f.write(f"- {key}: {len(value)}\n")
        f.write("\nUnknown files are not included in CPT V1 and require manual review before use.\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="Limit line counting per file for fast inspection.")
    args = parser.parse_args()

    ensure_dirs()
    rows = build_inventory(args.limit)
    mapping = build_map(rows)
    print(f"files={len(rows)}")
    for key, value in mapping.items():
        print(f"{key}={len(value)}")

    if args.dry_run:
        return 0

    refuse_overwrite([OUT_TSV, OUT_MD, OUT_MAP], args.overwrite)
    write_outputs(rows, mapping)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
