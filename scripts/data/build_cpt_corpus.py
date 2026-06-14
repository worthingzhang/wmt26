#!/usr/bin/env python3
"""Build CPT corpus from raw monolingual/parallel data.

Outputs standard jsonl lines: {"text": "..."}
Also writes a manifest JSON to data/manifests/.
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
        description="Build CPT corpus from raw text sources.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory containing raw text files or subdirectories.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/home/zc/wmt26/data/processed/cpt",
        help="Output directory for processed CPT jsonl.",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="cpt_mix_v1.jsonl",
        help="Output jsonl filename.",
    )
    parser.add_argument(
        "--manifest-path",
        type=str,
        default="/home/zc/wmt26/data/manifests/cpt_mix_v1.json",
        help="Path to write the data manifest.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="/home/zc/wmt26/configs/data/cpt_mix_v1.yaml",
        help="Path to data mix config YAML.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="If set, limit total output samples (useful for smoke test).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, only print plan without writing files.",
    )
    return parser.parse_args()


def validate_paths(args: argparse.Namespace) -> None:
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)
    if not input_dir.is_dir():
        logger.error(f"Input path is not a directory: {input_dir}")
        sys.exit(1)

    config_path = Path(args.config)
    if not config_path.exists():
        logger.warning(f"Config file not found (optional): {config_path}")


def build_corpus(input_dir: Path, output_path: Path, max_samples: int | None) -> int:
    """TODO: implement real corpus building logic.

    For now this is a skeleton that creates a tiny dummy jsonl if no input
    is found, so downstream smoke tests can proceed.
    """
    count = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    text_files = sorted(input_dir.rglob("*.txt")) + sorted(input_dir.rglob("*.jsonl"))

    with output_path.open("w", encoding="utf-8") as out_f:
        if text_files:
            for file_path in text_files:
                logger.info(f"Processing {file_path}")
                # TODO: read, clean, dedup, tokenize, pack
                # Placeholder:
                sample = {"text": f"Placeholder text from {file_path.name}"}
                out_f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                count += 1
                if max_samples and count >= max_samples:
                    break
        else:
            logger.warning("No .txt or .jsonl files found; writing placeholder sample.")
            out_f.write(json.dumps({"text": "Placeholder CPT sentence."}, ensure_ascii=False) + "\n")
            count = 1

    return count


def write_manifest(args: argparse.Namespace, num_samples: int) -> None:
    manifest = {
        "manifest_version": "1.0",
        "dataset_id": Path(args.output_name).stem,
        "dataset_type": "cpt",
        "output_dir": args.output_dir,
        "files": [args.output_name],
        "num_samples": num_samples,
        "sources": [args.input_dir],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Skeleton manifest. Update after implementing real builder.",
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
    logger.info(f"Input dir : {args.input_dir}")
    logger.info(f"Output    : {output_path}")
    logger.info(f"Manifest  : {args.manifest_path}")

    if args.dry_run:
        logger.info("Dry run mode. Exiting without writing files.")
        return 0

    num_samples = build_corpus(Path(args.input_dir), output_path, args.max_samples)
    write_manifest(args, num_samples)

    logger.info(f"Done. Wrote {num_samples} samples to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
