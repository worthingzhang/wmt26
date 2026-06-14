#!/usr/bin/env python3
"""Build SFT data from raw task-specific sources.

Outputs ShareGPT messages jsonl: {"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}
Also writes dataset_info.json for LlamaFactory and a manifest JSON.
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
        description="Build SFT data in ShareGPT messages format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory containing raw SFT source files or subdirectories.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/home/zc/wmt26/data/processed/sft",
        help="Output directory for processed SFT jsonl.",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="sft_mix_v1.jsonl",
        help="Output jsonl filename.",
    )
    parser.add_argument(
        "--dataset-info-path",
        type=str,
        default="/home/zc/wmt26/data/processed/sft/dataset_info.json",
        help="Path to write dataset_info.json for LlamaFactory.",
    )
    parser.add_argument(
        "--manifest-path",
        type=str,
        default="/home/zc/wmt26/data/manifests/sft_mix_v1.json",
        help="Path to write the data manifest.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="/home/zc/wmt26/configs/data/sft_mix_v1.yaml",
        help="Path to data mix config YAML.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="If set, limit total output samples.",
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


def build_sft_data(input_dir: Path, output_path: Path, max_samples: int | None) -> int:
    """TODO: implement real SFT data building logic.

    Skeleton: creates placeholder ShareGPT messages if no input found.
    """
    count = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    source_files = sorted(input_dir.rglob("*.jsonl")) + sorted(input_dir.rglob("*.json"))

    with output_path.open("w", encoding="utf-8") as out_f:
        if source_files:
            for file_path in source_files:
                logger.info(f"Processing {file_path}")
                # TODO: parse raw format, convert to ShareGPT messages
                sample = {
                    "messages": [
                        {"role": "user", "content": f"Placeholder instruction from {file_path.name}"},
                        {"role": "assistant", "content": "Placeholder response."},
                    ]
                }
                out_f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                count += 1
                if max_samples and count >= max_samples:
                    break
        else:
            logger.warning("No source files found; writing placeholder sample.")
            sample = {
                "messages": [
                    {"role": "user", "content": "Translate to German: Hello world."},
                    {"role": "assistant", "content": "Hallo Welt."},
                ]
            }
            out_f.write(json.dumps(sample, ensure_ascii=False) + "\n")
            count = 1

    return count


def write_dataset_info(args: argparse.Namespace) -> None:
    dataset_info = {
        Path(args.output_name).stem: {
            "file_name": args.output_name,
            "formatting": "sharegpt",
            "columns": {
                "messages": "messages",
            },
        }
    }
    info_path = Path(args.dataset_info_path)
    info_path.parent.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        with info_path.open("w", encoding="utf-8") as f:
            json.dump(dataset_info, f, indent=2, ensure_ascii=False)
    logger.info(f"dataset_info.json written to {info_path}")


def write_manifest(args: argparse.Namespace, num_samples: int) -> None:
    manifest = {
        "manifest_version": "1.0",
        "dataset_id": Path(args.output_name).stem,
        "dataset_type": "sft",
        "output_dir": args.output_dir,
        "files": [args.output_name, "dataset_info.json"],
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
    logger.info(f"Dataset info: {args.dataset_info_path}")
    logger.info(f"Manifest  : {args.manifest_path}")

    if args.dry_run:
        logger.info("Dry run mode. Exiting without writing files.")
        return 0

    num_samples = build_sft_data(Path(args.input_dir), output_path, args.max_samples)
    write_dataset_info(args)
    write_manifest(args, num_samples)

    logger.info(f"Done. Wrote {num_samples} samples to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
