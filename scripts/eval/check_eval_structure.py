#!/usr/bin/env python3
"""Read-only structure checker for WMT26 evaluation results.

Reads reports/eval/eval_index.csv and verifies that each entry conforms to the
EVAL_RESULT_STANDARD.md rules. This script does not modify files, run models,
or invoke lm_eval.

Usage:
    source .venv/bin/activate
    python scripts/eval/check_eval_structure.py
    python scripts/eval/check_eval_structure.py --strict
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "standard_run_dir",
    "model_tag",
    "checkpoint_type",
    "eval_setting",
    "shot_setting",
    "parallel_setting",
    "backend",
    "backend_role",
    "official",
    "eval_code_commit",
    "data_commit",
    "source_run_dir",
    "results_md",
    "scores_csv",
    "run_yaml",
    "status",
    "notes",
]

REQUIRED_OFFICIAL_FIELDS = [
    "model_tag",
    "checkpoint_type",
    "eval_setting",
    "shot_setting",
    "backend",
    "backend_role",
    "eval_code_commit",
    "data_commit",
    "source_run_dir",
    "results_md",
    "scores_csv",
    "run_yaml",
]

REQUIRED_FILE_FIELDS = ["results_md", "scores_csv", "run_yaml"]

NON_OFFICIAL_MARKERS = [
    "PRE-OFFICIAL-ALIGN",
    "EXPERIMENTAL",
    "REGRESSED",
    "INVALID",
    "SMOKE",
    "DEBUG",
    "CANDIDATE",
    "ARCHIVE",
]


def is_known(value: str) -> bool:
    """Return False for empty or explicitly unknown values."""
    return bool(value and value.strip().lower() not in {"", "unknown"})


def check_row(row: dict[str, str], row_num: int, project_root: Path) -> list[str]:
    issues: list[str] = []
    standard_dir = row.get("standard_run_dir", "").strip()
    official_raw = row.get("official", "").strip().lower()
    notes = row.get("notes", "")

    # 1. Header field presence.
    for field in REQUIRED_FIELDS:
        if field not in row:
            issues.append(f"missing column '{field}' in CSV header")

    # 2. standard_run_dir must exist and be a directory.
    if standard_dir:
        standard_path = project_root / standard_dir
        if not standard_path.exists():
            issues.append(f"standard_run_dir does not exist: {standard_dir}")
        elif not standard_path.is_dir():
            issues.append(f"standard_run_dir is not a directory: {standard_dir}")
    else:
        issues.append("standard_run_dir is empty")

    # 3. official flag validation.
    if official_raw == "true":
        if "reports/eval_official/" not in standard_dir.replace("\\", "/"):
            issues.append(
                "official=true but standard_run_dir is not under reports/eval_official/"
            )

        for field in REQUIRED_OFFICIAL_FIELDS:
            if not is_known(row.get(field, "")):
                issues.append(
                    f"official=true but required field '{field}' is missing or unknown"
                )

        for field in REQUIRED_FILE_FIELDS:
            rel_path = row.get(field, "").strip()
            if is_known(rel_path):
                file_path = project_root / rel_path
                if not file_path.exists():
                    issues.append(
                        f"official=true but {field} file does not exist: {rel_path}"
                    )

    elif official_raw == "false":
        if not any(marker in notes for marker in NON_OFFICIAL_MARKERS):
            issues.append(
                f"official=false but notes lacks one of the required markers: "
                f"{NON_OFFICIAL_MARKERS}"
            )
        if "reports/eval_official/" in standard_dir.replace("\\", "/"):
            issues.append(
                "official=false but standard_run_dir is under reports/eval_official/"
            )
    else:
        issues.append(
            f"'official' must be 'true' or 'false', got '{row.get('official', '')}'"
        )

    # 4. model_tag sanity.
    model_tag = row.get("model_tag", "").strip()
    if not model_tag:
        issues.append("model_tag is empty")
    elif model_tag in {"Qwen3.5-2B"}:
        issues.append(
            f"model_tag '{model_tag}' is a display name, not a registered model_tag"
        )

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check WMT26 eval result structure against EVAL_RESULT_STANDARD.md"
    )
    parser.add_argument(
        "--index",
        default="reports/eval/eval_index.csv",
        help="Path to eval_index.csv, relative to --project-root",
    )
    parser.add_argument(
        "--project-root",
        default="/home/zc/wmt26",
        help="Project root used to resolve relative paths",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if any issue is found",
    )
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    index_path = project_root / args.index

    if not index_path.exists():
        print(f"ERROR: index file not found: {index_path}", file=sys.stderr)
        return 1

    rows: list[dict[str, str]] = []
    with index_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    all_issues: list[tuple[int, str, list[str]]] = []
    for row_num, row in enumerate(rows, start=2):  # CSV rows are 1-indexed; row 1 is header
        issues = check_row(row, row_num, project_root)
        if issues:
            all_issues.append((row_num, row.get("standard_run_dir", ""), issues))

    print(f"Checked {len(rows)} row(s) in {index_path}")
    print(f"Found {len(all_issues)} row(s) with issues")
    print()

    for row_num, standard_dir, issues in all_issues:
        print(f"Row {row_num}: {standard_dir}")
        for issue in issues:
            print(f"  - {issue}")
        print()

    if not all_issues:
        print("OK: all checked rows conform to EVAL_RESULT_STANDARD.md")
        return 0

    if args.strict:
        print("FAIL: structure check found issues (--strict)", file=sys.stderr)
        return 1

    print("WARN: structure check found issues (exits 0 because --strict was not set)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
