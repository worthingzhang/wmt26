#!/usr/bin/env python3
"""Download instruction datasets filtered to target languages.

Target languages:
  - English (eng/en)
  - German (deu/de)
  - Slavic languages proximate to Sorbian:
    Polish (pol/pl), Czech (ces/cs), Slovak (slk/sk),
    Ukrainian (ukr/uk), Russian (rus/ru), Bulgarian (bul/bg),
    Serbian (srp/sr), Croatian (hrv/hr), Slovenian (slv/sl)
  - Sorbian itself if present: hsb, dsb

Datasets:
  1. Magpie-Align/Magpie-Llama-3.1-Pro-MT-300K-v0.1  (lang field: EN, DE, ...)
  2. CohereForAI/aya_dataset                           (language_code: eng, deu, pol, ...)
  3. OpenAssistant/oasst2                               (lang: en, de, pl, ...)
  4. Muennighoff/flan                                   (English only, no lang field)
  5. EuroBlocks — NOT FOUND on HuggingFace Hub (skipped, noted)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT_DIR = Path("/home/zc/wmt26")
OUT_DIR = ROOT_DIR / "data" / "raw" / "instruction"

# --- Language code normalization ---
# Map various ISO code formats to our canonical 639-3 codes
LANG_NORMALIZE: dict[str, str] = {
    # English
    "en": "eng", "eng": "eng", "EN": "eng", "english": "eng",
    # German
    "de": "deu", "deu": "deu", "DE": "deu", "german": "deu", "de-DE": "deu",
    # Polish
    "pl": "pol", "pol": "pol", "PL": "pol", "polish": "pol",
    # Czech
    "cs": "ces", "ces": "ces", "CS": "ces", "czech": "ces",
    # Slovak
    "sk": "slk", "slk": "slk", "SK": "slk", "slovak": "slk",
    # Ukrainian
    "uk": "ukr", "ukr": "ukr", "uk-UA": "ukr", "UK": "ukr", "ukrainian": "ukr",
    # Russian
    "ru": "rus", "rus": "rus", "RU": "rus", "russian": "rus",
    # Bulgarian
    "bg": "bul", "bul": "bul", "BG": "bul", "bulgarian": "bul",
    # Serbian
    "sr": "srp", "srp": "srp", "SR": "srp", "serbian": "srp",
    # Croatian
    "hr": "hrv", "hrv": "hrv", "HR": "hrv", "croatian": "hrv",
    # Slovenian
    "sl": "slv", "slv": "slv", "SL": "slv", "slovenian": "slv",
    # Upper/Lower Sorbian
    "hsb": "hsb", "dsb": "dsb", "upper_sorbian": "hsb", "lower_sorbian": "dsb",
}

TARGET_LANGS = set(LANG_NORMALIZE.values())


def normalize_lang(raw: str | None) -> str | None:
    if raw is None:
        return None
    return LANG_NORMALIZE.get(raw, LANG_NORMALIZE.get(raw.lower(), None))


# --- Dataset-specific downloaders ---

def download_magpie_mt(max_docs: int, split: str) -> dict:
    from datasets import load_dataset

    ds_id = "Magpie-Align/Magpie-Llama-3.1-Pro-MT-300K-v0.1"
    out_file = OUT_DIR / "magpie_mt.jsonl"
    ds = load_dataset(ds_id, split=split, streaming=True)
    counts: dict[str, int] = {}
    total = 0
    kept = 0
    with out_file.open("w", encoding="utf-8") as f:
        for row in ds:
            total += 1
            lang = normalize_lang(row.get("language"))
            if lang not in TARGET_LANGS:
                continue
            rec = {
                "source": ds_id,
                "lang": lang,
                "instruction": row.get("instruction", ""),
                "response": row.get("response", ""),
                "conversations": row.get("conversations"),
                "task_category": row.get("task_category"),
                "difficulty": row.get("difficulty"),
                "input_quality": row.get("input_quality"),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            counts[lang] = counts.get(lang, 0) + 1
            kept += 1
            if kept >= max_docs:
                break
    return {"dataset": ds_id, "file": str(out_file), "total_scanned": total, "kept": kept, "by_lang": counts}


def download_aya(max_docs: int, split: str) -> dict:
    from datasets import load_dataset

    ds_id = "CohereForAI/aya_dataset"
    out_file = OUT_DIR / "aya.jsonl"
    ds = load_dataset(ds_id, split=split, streaming=True)
    counts: dict[str, int] = {}
    total = 0
    kept = 0
    with out_file.open("w", encoding="utf-8") as f:
        for row in ds:
            total += 1
            lang = normalize_lang(row.get("language_code"))
            if lang not in TARGET_LANGS:
                continue
            rec = {
                "source": ds_id,
                "lang": lang,
                "instruction": row.get("inputs", ""),
                "response": row.get("targets", ""),
                "annotation_type": row.get("annotation_type"),
                "language_name": row.get("language"),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            counts[lang] = counts.get(lang, 0) + 1
            kept += 1
            if kept >= max_docs:
                break
    return {"dataset": ds_id, "file": str(out_file), "total_scanned": total, "kept": kept, "by_lang": counts}


def download_oasst2(max_docs: int, split: str) -> dict:
    from datasets import load_dataset

    ds_id = "OpenAssistant/oasst2"
    out_file = OUT_DIR / "oasst2.jsonl"
    ds = load_dataset(ds_id, split=split, streaming=True)
    counts: dict[str, int] = {}
    total = 0
    kept = 0
    with out_file.open("w", encoding="utf-8") as f:
        for row in ds:
            total += 1
            lang = normalize_lang(row.get("lang"))
            if lang not in TARGET_LANGS:
                continue
            if row.get("deleted") == "True":
                continue
            rec = {
                "source": ds_id,
                "lang": lang,
                "message_id": row.get("message_id"),
                "parent_id": row.get("parent_id"),
                "text": row.get("text", ""),
                "role": row.get("role"),
                "message_tree_id": row.get("message_tree_id"),
                "tree_state": row.get("tree_state"),
                "review_result": row.get("review_result"),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            counts[lang] = counts.get(lang, 0) + 1
            kept += 1
            if kept >= max_docs:
                break
    return {"dataset": ds_id, "file": str(out_file), "total_scanned": total, "kept": kept, "by_lang": counts}


def download_flan(max_docs: int, split: str) -> dict:
    from datasets import load_dataset

    ds_id = "Muennighoff/flan"
    out_file = OUT_DIR / "flan_v2_en.jsonl"
    ds = load_dataset(ds_id, split=split, streaming=True)
    total = 0
    kept = 0
    with out_file.open("w", encoding="utf-8") as f:
        for row in ds:
            total += 1
            rec = {
                "source": ds_id,
                "lang": "eng",
                "instruction": row.get("inputs", ""),
                "response": row.get("targets", ""),
                "task": row.get("task"),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            kept += 1
            if kept >= max_docs:
                break
    return {"dataset": ds_id, "file": str(out_file), "total_scanned": total, "kept": kept, "by_lang": {"eng": kept}}


DATASET_REGISTRY = [
    ("magpie_mt", download_magpie_mt),
    ("aya", download_aya),
    ("oasst2", download_oasst2),
    ("flan", download_flan),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--datasets", nargs="*", default=None,
                        help="Subset of datasets to download. Choices: magpie_mt, aya, oasst2, flan. Default: all.")
    parser.add_argument("--max-docs", type=int, default=50000,
                        help="Max documents to keep per dataset (after language filter). Default: 50000.")
    parser.add_argument("--split", default="train", help="Dataset split. Default: train.")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    selected = args.datasets or [name for name, _ in DATASET_REGISTRY]
    registry = {name: fn for name, fn in DATASET_REGISTRY}

    results = []
    for name in selected:
        if name not in registry:
            print(f"WARNING: unknown dataset '{name}', skipping")
            continue
        print(f"--- Downloading {name} (max_docs={args.max_docs}, split={args.split}) ---")
        result = registry[name](args.max_docs, args.split)
        results.append(result)
        print(f"  scanned={result['total_scanned']} kept={result['kept']} by_lang={result['by_lang']}")

    summary = {
        "target_langs": sorted(TARGET_LANGS),
        "max_docs_per_dataset": args.max_docs,
        "split": args.split,
        "results": results,
        "skipped": ["EuroBlocks (not found on HuggingFace Hub)"],
    }
    summary_file = OUT_DIR / "download_summary.json"
    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSummary written to {summary_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
