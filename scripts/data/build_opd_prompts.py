#!/usr/bin/env python3
"""Build OPD prompt pool from SFT data or other prompt sources.

Outputs jsonl lines with fields: task, prompt, source, lang
No reference answer is required.
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build OPD prompt pool from SFT data or prompt sources.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-path",
        type=str,
        required=True,
        help="Input SFT jsonl or directory containing prompt sources.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/home/zc/wmt26/data/processed/opd_prompts",
        help="Output directory for processed OPD prompts.",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="opd_prompt_mix_v1.jsonl",
        help="Output filename (jsonl or parquet).",
    )
    parser.add_argument(
        "--manifest-path",
        type=str,
        default="/home/zc/wmt26/data/manifests/opd_prompt_mix_v1.json",
        help="Path to write the data manifest.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="/home/zc/wmt26/configs/data/opd_prompt_mix_v1.yaml",
        help="Path to prompt mix config YAML.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="If set, limit total output prompts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, only print plan without writing files.",
    )
    return parser.parse_args()


def validate_paths(args: argparse.Namespace) -> None:
    input_path = Path(args.input_path)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)

    config_path = Path(args.config)
    if not config_path.exists():
        logger.warning(f"Config file not found (optional): {config_path}")


def extract_prompts(input_path: Path, output_path: Path, max_samples: int | None) -> int:
    """TODO: implement real prompt extraction logic.

    Skeleton: if input is a jsonl, try to read first user message as prompt.
    Otherwise write placeholder prompt.
    """
    count = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if input_path.is_file() and input_path.suffix == ".jsonl":
        with input_path.open("r", encoding="utf-8") as in_f, output_path.open("w", encoding="utf-8") as out_f:
            for line in in_f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping bad json line: {e}")
                    continue

                # TODO: robust extraction based on format
                prompt_text = ""
                messages = obj.get("messages", [])
                if messages and messages[0].get("role") == "user":
                    prompt_text = messages[0].get("content", "")

                if not prompt_text:
                    prompt_text = obj.get("prompt", "")

                if not prompt_text:
                    prompt_text = "Placeholder prompt."

                sample = {
                    "task": obj.get("task", "unknown"),
                    "prompt": prompt_text,
                    "source": obj.get("source", input_path.name),
                    "lang": obj.get("lang", "unknown"),
                }
                out_f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                count += 1
                if max_samples and count >= max_samples:
                    break
    else:
        logger.warning("Input is not a single jsonl; writing placeholder prompt.")
        with output_path.open("w", encoding="utf-8") as out_f:
            out_f.write(json.dumps({
                "task": "mt",
                "prompt": "Translate to German: Hello world.",
                "source": input_path.name,
                "lang": "en-de",
            }, ensure_ascii=False) + "\n")
            count = 1

    return count


def write_manifest(args: argparse.Namespace, num_samples: int) -> None:
    manifest = {
        "manifest_version": "1.0",
        "dataset_id": Path(args.output_name).stem,
        "dataset_type": "opd_prompts",
        "output_dir": args.output_dir,
        "files": [args.output_name],
        "num_samples": num_samples,
        "sources": [args.input_path],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Skeleton manifest. Update after implementing real extractor.",
    }
    manifest_path = Path(args.manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    logger.info(f"Manifest written to {manifest_path}")


def main() -> int:
    args = parse_args()
    validate_paths(args)

    output_path = Path(args.output_dir) / args.output_name
    logger.info(f"Input     : {args.input_path}")
    logger.info(f"Output    : {output_path}")
    logger.info(f"Manifest  : {args.manifest_path}")

    if args.dry_run:
        logger.info("Dry run mode. Exiting without writing files.")
        return 0

    num_samples = extract_prompts(Path(args.input_path), output_path, args.max_samples)
    write_manifest(args, num_samples)

    logger.info(f"Done. Wrote {num_samples} prompts to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
