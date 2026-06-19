#!/usr/bin/env python3
"""Aggregate lm-eval result directories into a standard eval entry point."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_MODEL_PATH = "/home/zc/wmt26/models/base/Qwen3.5-2B"
GROUP_ORDER = ["MT", "QA", "SC", "GC", "MR", "Other"]
META_METRICS = {"alias", "name", "sample_len"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate lm-eval results into RESULTS.md, scores.csv, and run.yaml."
    )
    parser.add_argument(
        "--source-run-dir",
        required=True,
        action="append",
        type=Path,
        help="Source run directory. May be repeated for split QA/generative runs.",
    )
    parser.add_argument("--standard-run-dir", required=True, type=Path)
    parser.add_argument("--model-tag", required=True)
    parser.add_argument("--eval-setting", required=True)
    parser.add_argument("--shot-setting", required=True)
    parser.add_argument("--parallel-setting", required=True)
    parser.add_argument("--model-path", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--status", default="aggregated")
    parser.add_argument("--notes", default="")
    parser.add_argument("--index-path", default="reports/eval/eval_index.csv", type=Path)
    parser.add_argument(
        "--no-symlink-artifacts",
        action="store_true",
        help="Write raw/log README references instead of symlinks. Use for tracked reports.",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def rel_from(path: Path, base: Path) -> tuple[str, ...]:
    try:
        return path.relative_to(base).parts
    except ValueError:
        return ()


def shard_name(path: Path, source_run_dirs: list[Path]) -> str:
    for source_run_dir in source_run_dirs:
        parts = rel_from(path, source_run_dir)
        if not parts:
            continue
        if len(parts) >= 2 and parts[0] == "shards":
            return parts[1]
        for part in parts:
            if part.startswith("gpu"):
                return part
        if len(source_run_dirs) > 1:
            return source_run_dir.name
    return ""


def source_for_path(path: Path, source_run_dirs: list[Path]) -> str:
    for source_run_dir in source_run_dirs:
        if rel_from(path, source_run_dir):
            return rel(source_run_dir)
    return ""


def task_group(task: str) -> str:
    base = task.split("_devsplit", 1)[0]
    if "-" in base:
        pieces = base.split("-")
        if len(pieces) == 2 and set(pieces) <= {"deu", "hsb", "dsb"}:
            return "MT"
    if "qa" in base:
        return "QA"
    if base.endswith("sc"):
        return "SC"
    if base.endswith("gc"):
        return "GC"
    if base.endswith("mr"):
        return "MR"
    return "Other"


def metric_is_scalar(value: Any) -> bool:
    return isinstance(value, (int, float, str, bool)) or value is None


def is_core_metric(metric: str) -> bool:
    if metric in META_METRICS or "_stderr" in metric or metric.endswith("_stderr"):
        return False
    metric_base = metric.split(",", 1)[0]
    return metric_base in {
        "acc",
        "exact_match",
        "exact_match_wrong",
        "exact_match_corrected",
        "bleu",
        "chrf",
        "chrf_pp",
    }


def discover_result_files(source_run_dirs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for source_run_dir in source_run_dirs:
        files.extend(
            p
            for p in source_run_dir.rglob("results_*.json")
            if p.name != "results_aggregate.json"
        )
    return sorted(files)


def parse_results(
    result_files: list[Path], source_run_dirs: list[Path]
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    parsed_files: list[str] = []

    for result_path in result_files:
        try:
            obj = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - record and continue by design.
            warnings.append(f"Could not parse JSON {rel(result_path)}: {exc}")
            continue

        results = obj.get("results")
        if not isinstance(results, dict):
            warnings.append(f"No top-level results dict in {rel(result_path)}")
            continue

        parsed_files.append(rel(result_path))
        shard = shard_name(result_path, source_run_dirs)
        source_dir = source_for_path(result_path, source_run_dirs)
        for task, metrics in sorted(results.items()):
            if not isinstance(metrics, dict):
                warnings.append(f"Task {task} in {rel(result_path)} is not a metrics dict")
                continue
            for metric, value in sorted(metrics.items()):
                if not metric_is_scalar(value):
                    continue
                rows.append(
                    {
                        "task": task,
                        "metric": metric,
                        "value": value,
                        "source_json": rel(result_path),
                        "source_run_dir": source_dir,
                        "shard": shard,
                        "group": task_group(task),
                    }
                )

    return rows, warnings, parsed_files


def count_lines(path: Path) -> int:
    n = 0
    with path.open("rb") as handle:
        for _ in handle:
            n += 1
    return n


def collect_sample_files(source_run_dirs: list[Path]) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    sample_paths: list[Path] = []
    for source_run_dir in source_run_dirs:
        sample_paths.extend(
            p
            for p in source_run_dir.rglob("*.jsonl")
            if p.name.startswith("samples_") or p.suffix == ".jsonl"
        )
    samples: list[dict[str, Any]] = []
    for path in sorted(sample_paths):
        try:
            line_count = count_lines(path)
            size_bytes = path.stat().st_size
        except Exception as exc:  # noqa: BLE001 - record and continue by design.
            warnings.append(f"Could not stat/count sample file {rel(path)}: {exc}")
            continue
        samples.append(
            {
                "path": rel(path),
                "lines": line_count,
                "size_bytes": size_bytes,
                "source_run_dir": source_for_path(path, source_run_dirs),
                "shard": shard_name(path, source_run_dirs),
            }
        )
    return samples, warnings


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return "null"
    text = str(value)
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    lines: list[str] = []

    def emit(key: str, value: Any, indent: int = 0) -> None:
        prefix = " " * indent
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            for sub_key, sub_value in value.items():
                emit(str(sub_key), sub_value, indent + 2)
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            if not value:
                lines[-1] += " []"
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{prefix}  -")
                    for sub_key, sub_value in item.items():
                        emit(str(sub_key), sub_value, indent + 4)
                else:
                    lines.append(f"{prefix}  - {yaml_scalar(item)}")
        else:
            lines.append(f"{prefix}{key}: {yaml_scalar(value)}")

    for key, value in data.items():
        emit(key, value)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_scores_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["task", "metric", "value", "source_json", "shard"],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r["group"], r["task"], r["metric"], r["shard"])):
            writer.writerow(
                {
                    "task": row["task"],
                    "metric": row["metric"],
                    "value": row["value"],
                    "source_json": row["source_json"],
                    "shard": row["shard"],
                }
            )


def format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def append_score_table(lines: list[str], rows: list[dict[str, Any]], include_source: bool = False) -> None:
    if include_source:
        lines.extend(["| task | metric | value | shard | source_json |", "|---|---|---:|---|---|"])
    else:
        lines.extend(["| task | metric | value | shard |", "|---|---|---:|---|"])
    for row in sorted(rows, key=lambda r: (r["group"], r["task"], r["metric"], r["shard"])):
        if include_source:
            lines.append(
                f"| `{row['task']}` | `{row['metric']}` | {format_value(row['value'])} | "
                f"`{row['shard']}` | `{row['source_json']}` |"
            )
        else:
            lines.append(
                f"| `{row['task']}` | `{row['metric']}` | {format_value(row['value'])} | `{row['shard']}` |"
            )


def write_results_md(
    path: Path,
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    parsed_files: list[str],
    samples: list[dict[str, Any]],
    warnings: list[str],
) -> None:
    source_dirs = [rel(p) for p in args.source_run_dir]
    score_rows = [row for row in rows if row["metric"] not in META_METRICS]
    main_rows = [row for row in score_rows if is_core_metric(row["metric"])]

    lines = [
        f"# {args.model_tag} {args.eval_setting}",
        "",
        "## Quick Summary",
        "",
        f"- model_tag: `{args.model_tag}`",
        f"- model_path: `{args.model_path}`",
        f"- eval_setting: `{args.eval_setting}`",
        f"- shot_setting: `{args.shot_setting}`",
        f"- parallel_setting: `{args.parallel_setting}`",
        f"- status: `{args.status}`",
        f"- generated_at: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- parsed_result_files: `{len(parsed_files)}`",
        f"- sample_files: `{len(samples)}`",
        "- source_run_dir(s):",
    ]
    lines.extend(f"  - `{item}`" for item in source_dirs)
    if args.notes:
        lines.append(f"- notes: {args.notes}")

    lines.extend(["", "## Main Scores", ""])
    for group in GROUP_ORDER:
        group_rows = [row for row in main_rows if row["group"] == group]
        if not group_rows:
            continue
        lines.extend([f"### {group}", ""])
        append_score_table(lines, group_rows, include_source=False)
        lines.append("")

    lines.extend(["## All Scalar Metrics", ""])
    append_score_table(lines, score_rows, include_source=True)
    lines.append("")

    lines.extend(["## Parsed Files", ""])
    for item in parsed_files:
        lines.append(f"- `{item}`")
    lines.append("")

    lines.extend(
        [
            "## Sample Files",
            "",
            "| path | lines | size_bytes | shard |",
            "|---|---:|---:|---|",
        ]
    )
    for sample in samples:
        lines.append(
            f"| `{sample['path']}` | {sample['lines']} | {sample['size_bytes']} | `{sample['shard']}` |"
        )
    lines.append("")

    lines.extend(["## Warnings / Limitations", ""])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def ensure_can_write(standard_run_dir: Path, overwrite: bool) -> None:
    outputs = [
        standard_run_dir / "RESULTS.md",
        standard_run_dir / "scores.csv",
        standard_run_dir / "run.yaml",
    ]
    existing = [p for p in outputs if p.exists()]
    if existing and not overwrite:
        listed = "\n".join(f"- {rel(p)}" for p in existing)
        raise SystemExit(f"Output exists; pass --overwrite to replace:\n{listed}")


def link_or_note(link: Path, target: Path, overwrite: bool, warnings: list[str]) -> bool:
    if link.exists() or link.is_symlink():
        if overwrite:
            link.unlink()
        else:
            warnings.append(f"{rel(link)} already exists; left unchanged")
            return False
    try:
        link.symlink_to(os.path.relpath(target.resolve(), link.parent.resolve()))
        return True
    except OSError as exc:
        warnings.append(f"Could not create symlink {rel(link)} -> {rel(target)}: {exc}")
        return False


def create_links(
    source_run_dirs: list[Path],
    standard_run_dir: Path,
    overwrite: bool,
    warnings: list[str],
    no_symlink_artifacts: bool,
) -> None:
    raw_dir = standard_run_dir / "raw"
    logs_dir = standard_run_dir / "logs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    raw_notes: list[str] = []
    log_notes: list[str] = []
    multi = len(source_run_dirs) > 1

    for idx, source_run_dir in enumerate(source_run_dirs, 1):
        raw_name = f"source_run_{idx}" if multi else "source_run"
        raw_link = raw_dir / raw_name
        if no_symlink_artifacts:
            raw_notes.append(f"- `{raw_name}`: `{rel(source_run_dir)}`")
        elif not link_or_note(raw_link, source_run_dir, overwrite, warnings):
            raw_notes.append(f"- `{raw_name}`: `{rel(source_run_dir)}`")

        source_logs_dir = source_run_dir / "logs"
        log_name = f"source_logs_{idx}" if multi else "source_logs"
        log_link = logs_dir / log_name
        if source_logs_dir.exists():
            if no_symlink_artifacts:
                log_notes.append(f"- `{log_name}`: `{rel(source_logs_dir)}`")
            elif not link_or_note(log_link, source_logs_dir, overwrite, warnings):
                log_notes.append(f"- `{log_name}`: `{rel(source_logs_dir)}`")
        else:
            log_files = sorted(source_run_dir.rglob("*.log"))
            if log_files:
                log_notes.append(f"- `{rel(source_run_dir)}` has log files:")
                log_notes.extend(f"  - `{rel(item)}`" for item in log_files)
            else:
                log_notes.append(f"- No standalone logs found under `{rel(source_run_dir)}`")

    if raw_notes:
        (raw_dir / "README.md").write_text("# Raw Sources\n\n" + "\n".join(raw_notes) + "\n", encoding="utf-8")
    if log_notes:
        (logs_dir / "README.md").write_text("# Logs\n\n" + "\n".join(log_notes) + "\n", encoding="utf-8")


def update_eval_index(
    index_path: Path,
    args: argparse.Namespace,
    overwrite: bool,
    warnings: list[str],
) -> None:
    fieldnames = [
        "standard_run_dir",
        "model_tag",
        "eval_setting",
        "shot_setting",
        "parallel_setting",
        "source_run_dir",
        "results_md",
        "scores_csv",
        "run_yaml",
        "status",
        "notes",
    ]
    source_dirs = ";".join(rel(path) for path in args.source_run_dir)
    row = {
        "standard_run_dir": rel(args.standard_run_dir),
        "model_tag": args.model_tag,
        "eval_setting": args.eval_setting,
        "shot_setting": args.shot_setting,
        "parallel_setting": args.parallel_setting,
        "source_run_dir": source_dirs,
        "results_md": rel(args.standard_run_dir / "RESULTS.md"),
        "scores_csv": rel(args.standard_run_dir / "scores.csv"),
        "run_yaml": rel(args.standard_run_dir / "run.yaml"),
        "status": args.status,
        "notes": args.notes,
    }

    rows: list[dict[str, str]] = []
    if index_path.exists():
        with index_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != fieldnames:
                warnings.append(f"Existing {rel(index_path)} has unexpected header; preserving rows best-effort")
            for existing in reader:
                if existing.get("standard_run_dir") == row["standard_run_dir"]:
                    if overwrite:
                        continue
                    warnings.append(f"Index already has {row['standard_run_dir']}; left existing row")
                    rows.append(existing)
                    row = {}
                    continue
                rows.append(existing)
    if row:
        rows.append(row)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for item in rows:
            writer.writerow({key: item.get(key, "") for key in fieldnames})


def normalize_source_dirs(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    resolved: list[Path] = []
    for path in paths:
        item = path.resolve()
        if item in seen:
            continue
        if not item.exists():
            raise SystemExit(f"Source run directory does not exist: {item}")
        if not item.is_dir():
            raise SystemExit(f"Source run path is not a directory: {item}")
        seen.add(item)
        resolved.append(item)
    return resolved


def main() -> int:
    args = parse_args()
    args.source_run_dir = normalize_source_dirs(args.source_run_dir)
    args.standard_run_dir = args.standard_run_dir.resolve()

    result_files = discover_result_files(args.source_run_dir)
    if not result_files:
        listed = ", ".join(rel(path) for path in args.source_run_dir)
        raise SystemExit(f"No results_*.json files found under: {listed}")

    rows, warnings, parsed_files = parse_results(result_files, args.source_run_dir)
    samples, sample_warnings = collect_sample_files(args.source_run_dir)
    warnings.extend(sample_warnings)

    if not rows:
        raise SystemExit("No scalar task metrics were parsed from result files")

    if args.dry_run:
        print("DRY RUN")
        print("source_run_dirs:")
        for item in args.source_run_dir:
            print(f"  - {rel(item)}")
        print(f"standard_run_dir: {rel(args.standard_run_dir)}")
        print(f"status: {args.status}")
        print(f"result_files: {len(result_files)}")
        for item in result_files:
            print(f"  - {rel(item)}")
        print(f"sample_files: {len(samples)}")
        print("would_write:")
        for name in ["RESULTS.md", "scores.csv", "run.yaml", "raw/", "logs/"]:
            print(f"  - {rel(args.standard_run_dir / name)}")
        print(f"index_path: {rel(args.index_path)}")
        return 0

    ensure_can_write(args.standard_run_dir, args.overwrite)
    args.standard_run_dir.mkdir(parents=True, exist_ok=True)

    create_links(
        args.source_run_dir,
        args.standard_run_dir,
        args.overwrite,
        warnings,
        args.no_symlink_artifacts,
    )

    detected_tasks = sorted({row["task"] for row in rows})
    source_dirs = [rel(path) for path in args.source_run_dir]
    run_data = {
        "model_tag": args.model_tag,
        "model_path": args.model_path,
        "eval_setting": args.eval_setting,
        "shot_setting": args.shot_setting,
        "parallel_setting": args.parallel_setting,
        "status": args.status,
        "source_run_dir": source_dirs[0] if len(source_dirs) == 1 else None,
        "source_run_dirs": source_dirs,
        "standard_run_dir": rel(args.standard_run_dir),
        "created_by": "scripts/eval/aggregate_eval_results.py",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "parsed_result_files": parsed_files,
        "detected_tasks": detected_tasks,
        "sample_files": samples,
        "outputs": {
            "results_md": rel(args.standard_run_dir / "RESULTS.md"),
            "scores_csv": rel(args.standard_run_dir / "scores.csv"),
            "run_yaml": rel(args.standard_run_dir / "run.yaml"),
        },
        "warnings": warnings,
        "notes": args.notes,
    }

    write_scores_csv(args.standard_run_dir / "scores.csv", rows)
    write_results_md(args.standard_run_dir / "RESULTS.md", args, rows, parsed_files, samples, warnings)
    write_yaml(args.standard_run_dir / "run.yaml", run_data)
    update_eval_index(args.index_path, args, args.overwrite, warnings)

    print(f"Wrote {rel(args.standard_run_dir / 'RESULTS.md')}")
    print(f"Wrote {rel(args.standard_run_dir / 'scores.csv')}")
    print(f"Wrote {rel(args.standard_run_dir / 'run.yaml')}")
    print(f"Updated {rel(args.index_path)}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
