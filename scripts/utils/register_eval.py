#!/usr/bin/env python3
"""Register an evaluation result in runs/eval_registry.csv.

Appends one CSV line describing the evaluation run.
"""

import argparse
import csv
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("/home/zc/wmt26/runs/eval_registry.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Register an evaluation result in the eval registry.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--eval-id", type=str, required=True)
    parser.add_argument("--model-id", type=str, required=True)
    parser.add_argument("--model-path", type=str, required=True)
    parser.add_argument("--eval-config", type=str, required=True)
    parser.add_argument("--result-path", type=str, required=True)
    parser.add_argument("--status", type=str, default="completed")
    parser.add_argument("--notes", type=str, default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not REGISTRY_PATH.exists():
        with REGISTRY_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "eval_id", "model_id", "model_path", "eval_config",
                "result_path", "status", "notes",
            ])

    row = [
        args.eval_id,
        args.model_id,
        args.model_path,
        args.eval_config,
        args.result_path,
        args.status,
        f"{args.notes} (registered at {datetime.now(timezone.utc).isoformat()})",
    ]

    with REGISTRY_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    logger.info(f"Registered eval '{args.eval_id}' in {REGISTRY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
