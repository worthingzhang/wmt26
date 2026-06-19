#!/usr/bin/env python3
"""Template for controlled instruction-data sampling.

Do not use this for full downloads. It exists so future runs have an explicit
sampling interface and default to dry-run behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT_DIR = Path("/home/zc/wmt26")
OUT_DIR = ROOT_DIR / "data" / "raw" / "instruction"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Exact HuggingFace dataset id.")
    parser.add_argument("--max-samples", type=int, default=1000)
    parser.add_argument("--split", default="train")
    parser.add_argument("--streaming", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    print(
        json.dumps(
            {
                "source": args.source,
                "split": args.split,
                "streaming": args.streaming,
                "max_samples": args.max_samples,
                "dry_run": args.dry_run,
                "status": "dry_run" if args.dry_run else "not_implemented_for_full_download",
                "notes": "Verify dataset id, license, language fields, and sampling plan before export.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    if args.dry_run:
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raise SystemExit("Refusing non-dry-run export until a source-specific schema review is implemented.")


if __name__ == "__main__":
    raise SystemExit(main())
