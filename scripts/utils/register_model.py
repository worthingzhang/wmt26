#!/usr/bin/env python3
"""Register a model in models/registry/models.jsonl.

Appends one JSON line describing the model and its provenance.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("/home/zc/wmt26/models/registry/models.jsonl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Register a model in the model registry.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--model-id", type=str, required=True)
    parser.add_argument("--model-path", type=str, required=True)
    parser.add_argument(
        "--training-type",
        type=str,
        required=True,
        choices=["base", "cpt", "sft", "opd", "mixed"],
    )
    parser.add_argument("--input-model", type=str, default=None)
    parser.add_argument("--teacher-model", type=str, default=None)
    parser.add_argument("--data-config", type=str, default=None)
    parser.add_argument("--train-config", type=str, default=None)
    parser.add_argument("--notes", type=str, default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        logger.error(f"Model path does not exist: {model_path}")
        return 1

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "model_id": args.model_id,
        "model_path": str(model_path.resolve()),
        "training_type": args.training_type,
        "input_model": args.input_model,
        "teacher_model": args.teacher_model,
        "data_config": args.data_config,
        "train_config": args.train_config,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": args.notes,
    }

    with REGISTRY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    logger.info(f"Registered model '{args.model_id}' in {REGISTRY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
