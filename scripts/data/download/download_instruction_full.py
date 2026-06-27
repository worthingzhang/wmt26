#!/usr/bin/env python3
"""Download full Magpie-Pro-300K-Filtered and flan_v2_converted for TartuNLP reproduction."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path("/home/zc/wmt26")
OUT_DIR = ROOT_DIR / "data" / "raw" / "instruction"


def download_magpie_pro(max_docs: int | None) -> dict:
    from datasets import load_dataset

    ds_id = "Magpie-Align/Magpie-Pro-300K-Filtered"
    out_file = OUT_DIR / "magpie_pro_300k_full.jsonl"
    if out_file.exists():
        raise FileExistsError(f"File exists: {out_file}")

    ds = load_dataset(ds_id, split="train", streaming=True)
    count = 0
    with out_file.open("w", encoding="utf-8") as f:
        for row in ds:
            rec = {
                "source": ds_id,
                "uuid": row.get("uuid"),
                "conversations": row.get("conversations"),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
            if max_docs and count >= max_docs:
                break
            if count % 50000 == 0:
                print(f"  magpie: {count}...")

    return {"dataset": ds_id, "file": str(out_file), "rows": count}


def download_flan_v2_converted(max_docs: int | None) -> dict:
    from datasets import load_dataset

    ds_id = "ai2-adapt-dev/flan_v2_converted"
    out_file = OUT_DIR / "flan_v2_converted_full.jsonl"
    if out_file.exists():
        raise FileExistsError(f"File exists: {out_file}")

    ds = load_dataset(ds_id, split="train", streaming=True)
    count = 0
    with out_file.open("w", encoding="utf-8") as f:
        for row in ds:
            rec = {
                "source": ds_id,
                "inputs": row.get("inputs", ""),
                "targets": row.get("targets", ""),
                "messages": row.get("messages"),
                "_task_source": row.get("_task_source"),
                "_task_name": row.get("_task_name"),
                "_template_type": row.get("_template_type"),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
            if max_docs and count >= max_docs:
                break
            if count % 50000 == 0:
                print(f"  flan_v2: {count}...")

    return {"dataset": ds_id, "file": str(out_file), "rows": count}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="*", default=["magpie", "flan_v2"])
    parser.add_argument("--max-docs", type=int, default=None, help="Max docs per dataset (default: all)")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    if "magpie" in args.datasets:
        print("--- Downloading Magpie-Pro-300K-Filtered ---")
        r = download_magpie_pro(args.max_docs)
        results.append(r)
        print(f"  done: {r['rows']} rows -> {r['file']}")

    if "flan_v2" in args.datasets:
        print("--- Downloading ai2-adapt-dev/flan_v2_converted ---")
        r = download_flan_v2_converted(args.max_docs)
        results.append(r)
        print(f"  done: {r['rows']} rows -> {r['file']}")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "max_docs_per_dataset": args.max_docs,
        "results": results,
        "notes": [
            "Magpie-Pro-300K-Filtered: ~296k conversations, English only, no lang field",
            "flan_v2_converted: ~90k instruction pairs, English only, has messages format",
            "German FineWeb2: available at HuggingFaceFW/fineweb-2 config deu_Latn, NOT downloaded (not needed for TartuNLP final model)",
        ],
    }
    summary_file = OUT_DIR / "download_summary_full.json"
    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSummary: {summary_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
