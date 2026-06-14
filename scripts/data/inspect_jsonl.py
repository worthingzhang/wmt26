#!/usr/bin/env python3
"""Inspect a jsonl file: detect bad lines, count samples, print examples, stats."""

import argparse
import json
import logging
import sys
from collections import Counter
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a jsonl file for quality and content.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-path",
        type=str,
        required=True,
        help="Path to jsonl file to inspect.",
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=3,
        help="Number of sample lines to print.",
    )
    parser.add_argument(
        "--stat-field",
        type=str,
        default=None,
        help="If set, print distribution of this top-level field.",
    )
    parser.add_argument(
        "--max-print-len",
        type=int,
        default=500,
        help="Max characters to print per sample.",
    )
    return parser.parse_args()


def inspect_jsonl(input_path: Path, num_samples: int, stat_field: str | None, max_print_len: int) -> int:
    if not input_path.exists():
        logger.error(f"File does not exist: {input_path}")
        return 1
    if not input_path.is_file():
        logger.error(f"Path is not a file: {input_path}")
        return 1

    total_lines = 0
    valid_lines = 0
    bad_lines = 0
    samples_printed = 0
    field_counter = Counter()

    with input_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            total_lines += 1
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                bad_lines += 1
                logger.warning(f"Bad JSON at line {line_no}: {e}")
                continue

            valid_lines += 1

            if stat_field is not None:
                value = obj.get(stat_field, "__MISSING__")
                field_counter[value] += 1

            if samples_printed < num_samples:
                text = json.dumps(obj, ensure_ascii=False, indent=2)
                if len(text) > max_print_len:
                    text = text[:max_print_len] + "... [truncated]"
                print(f"\n--- Sample {samples_printed + 1} (line {line_no}) ---")
                print(text)
                samples_printed += 1

    print(f"\n=== Inspection Summary ===")
    print(f"Total lines  : {total_lines}")
    print(f"Valid samples: {valid_lines}")
    print(f"Bad lines    : {bad_lines}")

    if stat_field:
        print(f"\nDistribution of field '{stat_field}':")
        for value, count in field_counter.most_common():
            print(f"  {value}: {count}")

    return 0


def main() -> int:
    args = parse_args()
    return inspect_jsonl(
        Path(args.input_path),
        args.num_samples,
        args.stat_field,
        args.max_print_len,
    )


if __name__ == "__main__":
    sys.exit(main())
