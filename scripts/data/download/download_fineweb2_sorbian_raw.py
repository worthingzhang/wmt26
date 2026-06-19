#!/usr/bin/env python3
"""Discover and optionally stream Sorbian FineWeb-2 raw records.

This script intentionally avoids full dataset downloads. By default it runs in
dry-run mode and writes only candidate config names for manual review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path("/home/zc/wmt26")
DATASET_ID = "HuggingFaceFW/fineweb-2"
MANIFEST_DIR = ROOT_DIR / "data" / "manifests"
OUT_DIR = ROOT_DIR / "data" / "raw" / "external" / "fineweb2"
CANDIDATES_FILE = MANIFEST_DIR / "fineweb2_config_candidates.txt"


def classify_config(config: str) -> str | None:
    text = config.lower()
    if any(token in text for token in ("hsb", "upper_sorbian", "upper-sorbian", "upper sorbian")):
        return "hsb"
    if any(token in text for token in ("dsb", "lower_sorbian", "lower-sorbian", "lower sorbian")):
        return "dsb"
    return None


def write_candidates(configs: Iterable[str]) -> list[str]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    candidates = [
        cfg
        for cfg in configs
        if any(token in cfg.lower() for token in ("hsb", "dsb", "sorbian", "upper", "lower"))
    ]
    with CANDIDATES_FILE.open("w", encoding="utf-8") as f:
        f.write(f"dataset_id: {DATASET_ID}\n")
        f.write("candidate_configs:\n")
        for cfg in candidates:
            f.write(f"- {cfg}\n")
    return candidates


def resolve_language_configs(candidates: list[str]) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for cfg in candidates:
        lang = classify_config(cfg)
        if lang and lang not in resolved:
            resolved[lang] = cfg
    return resolved


def export_stream(config: str, lang: str, max_docs: int, split: str) -> int:
    from datasets import load_dataset

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / f"fineweb2_{lang}_raw_{max_docs}.jsonl"
    if out_file.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {out_file}")

    ds = load_dataset(DATASET_ID, name=config, split=split, streaming=True)
    count = 0
    with out_file.open("w", encoding="utf-8") as f:
        for row in ds:
            f.write(
                json.dumps(
                    {
                        "source_dataset": DATASET_ID,
                        "config": config,
                        "split": split,
                        "raw": row,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            count += 1
            if count >= max_docs:
                break
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-docs", type=int, default=50000)
    parser.add_argument("--split", default="train")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    from datasets import get_dataset_config_names

    configs = get_dataset_config_names(DATASET_ID)
    candidates = write_candidates(configs)
    resolved = resolve_language_configs(candidates)

    print(f"dataset_id={DATASET_ID}")
    print(f"candidate_file={CANDIDATES_FILE}")
    print(f"candidate_count={len(candidates)}")
    for cfg in candidates:
        print(f"candidate={cfg}")
    print(f"resolved={json.dumps(resolved, ensure_ascii=False, sort_keys=True)}")

    if "hsb" not in resolved or "dsb" not in resolved:
        print("status=needs_manual_verification")
        return 0

    if args.dry_run:
        print("status=dry_run")
        print("No documents exported. Re-run with --no-dry-run to stream limited samples.")
        return 0

    for lang, config in resolved.items():
        count = export_stream(config, lang, args.max_docs, args.split)
        print(f"exported lang={lang} config={config} count={count}")
    print("status=downloaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
