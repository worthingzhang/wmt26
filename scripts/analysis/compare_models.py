#!/usr/bin/env python3
"""Compare models across evaluation results.

Reads runs/eval_registry.csv and result JSON files, then outputs a summary
CSV and Markdown table with MT/QA/SC/GC/MR scores.

This is a skeleton; result parsing will be updated once official result
format is confirmed.
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# Load mirror/env configuration
def _load_env():
    env_path = Path(__file__).resolve().parents[2] / "configs" / "env" / "mirrors.env"
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)

_load_env()

TASKS = ["mt", "qa", "sc", "gc", "mr"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize evaluation results across models.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--eval-registry",
        type=str,
        default="/home/zc/wmt26/runs/eval_registry.csv",
        help="Path to eval_registry.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/home/zc/wmt26/runs/analysis",
        help="Directory to write comparison outputs.",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="comparison_v1",
        help="Base name for output files.",
    )
    return parser.parse_args()


def load_eval_registry(path: Path) -> list[dict]:
    if not path.exists():
        logger.error(f"Eval registry not found: {path}")
        sys.exit(1)

    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("status") != "completed":
                continue
            rows.append(row)
    return rows


def parse_result(result_path: Path) -> dict:
    """TODO: update parsing once official result format is known."""
    if not result_path.exists():
        return {task: None for task in TASKS}

    try:
        with result_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Could not parse {result_path}: {e}")
        return {task: None for task in TASKS}

    scores = {}
    for task in TASKS:
        # Try common key patterns
        for key in [task, task.upper(), f"{task}_score", f"{task}_avg"]:
            if key in data:
                scores[task] = data[key]
                break
        else:
            scores[task] = None
    return scores


def build_table(rows: list[dict]) -> list[dict]:
    table = []
    for row in rows:
        result_path = Path(row["result_path"])
        scores = parse_result(result_path)
        table.append({
            "model_id": row["model_id"],
            "eval_id": row["eval_id"],
            "model_path": row["model_path"],
            **scores,
        })
    return table


def write_csv(table: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["model_id", "eval_id", "model_path"] + TASKS
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table)
    logger.info(f"CSV summary written to {output_path}")


def write_markdown(table: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("| model_id | eval_id | MT | QA | SC | GC | MR |")
    lines.append("|----------|---------|----|----|----|----|----|")
    for row in table:
        scores = [str(row.get(task, "") or "-") for task in TASKS]
        lines.append(f"| {row['model_id']} | {row['eval_id']} | {' | '.join(scores)} |")
    lines.append("")
    lines.append("_Scores are placeholders until official result format is confirmed._")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Markdown summary written to {output_path}")


def main() -> int:
    args = parse_args()
    registry_path = Path(args.eval_registry)
    output_dir = Path(args.output_dir)

    rows = load_eval_registry(registry_path)
    if not rows:
        logger.warning("No completed evaluations found.")
        return 0

    table = build_table(rows)
    write_csv(table, output_dir / f"{args.output_name}.csv")
    write_markdown(table, output_dir / f"{args.output_name}.md")

    logger.info("Comparison complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
