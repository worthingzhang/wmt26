#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter

from official_mono_common import (
    DOCS,
    INTERIM,
    MANIFESTS,
    distribution,
    dump_yaml,
    ensure_dirs,
    read_jsonl,
    refuse_overwrite,
    sha1_normalized,
)

IN_CLEAN = INTERIM / "mono_all_clean.jsonl"
IN_HELDOUT = INTERIM / "heldout_hashes.jsonl"
OUT_TOKEN = INTERIM / "token_stats.json"
OUT_REPORT = INTERIM / "quality_audit_report.json"
OUT_HSB_SAMPLE = INTERIM / "sample_inspection_hsb.txt"
OUT_DSB_SAMPLE = INTERIM / "sample_inspection_dsb.txt"
OUT_STATUS = DOCS / "INTERIM_CLEANING_STATUS_CPT_V1_OFFICIAL_MONO.md"
OUT_MANIFEST = MANIFESTS / "cpt_v1_official_mono_interim.yaml"
TOKENIZER_PATH = "/home/zc/wmt26/models/base/Qwen3.5-2B"


def maybe_tokenizer():
    try:
        from transformers import AutoTokenizer

        return AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def write_samples(path, rows, title):
    with path.open("w", encoding="utf-8") as f:
        f.write(title + "\n")
        f.write("=" * len(title) + "\n\n")
        for i, row in enumerate(rows, 1):
            f.write(f"[{i}] {row['source']} | {row['source_kind']} | {row['source_path']}:{row.get('line_no')}\n")
            f.write(row["text"] + "\n\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    ensure_dirs()
    rows = []
    for i, row in enumerate(read_jsonl(IN_CLEAN), 1):
        if args.limit and i > args.limit:
            break
        rows.append(row)

    heldout = {row["hash"] for row in read_jsonl(IN_HELDOUT)}
    hashes = [row["normalized_sha1"] for row in rows]
    duplicate_hash_count = len(hashes) - len(set(hashes))
    leakage_hits = sum(1 for row in rows if sha1_normalized(row["text"]) in heldout)
    by_lang = Counter(row["lang"] for row in rows)
    by_source = Counter(row["source"] for row in rows)
    by_kind = Counter(row["source_kind"] for row in rows)
    chars_by_lang: dict[str, list[int]] = {"hsb": [], "dsb": []}
    tokens_by_lang: dict[str, list[int]] = {"hsb": [], "dsb": []}
    replacement_count = 0
    html_heavy_count = 0
    empty_count = 0

    tok = maybe_tokenizer()
    token_stats_skipped = isinstance(tok, dict)
    token_error = tok.get("error") if isinstance(tok, dict) else None

    tag_re = re.compile(r"</?[A-Za-z][^>]{0,120}>")
    for row in rows:
        text = row["text"]
        lang = row["lang"]
        if not text.strip():
            empty_count += 1
        if "\ufffd" in text:
            replacement_count += 1
        tag_chars = sum(len(m.group(0)) for m in tag_re.finditer(text))
        if tag_chars / max(1, len(text)) > 0.20:
            html_heavy_count += 1
        chars_by_lang.setdefault(lang, []).append(len(text))
        if not token_stats_skipped:
            tokens_by_lang.setdefault(lang, []).append(len(tok.encode(text, add_special_tokens=False)))

    token_stats = {
        "token_stats_skipped": token_stats_skipped,
        "tokenizer_path": TOKENIZER_PATH,
        "tokenizer_error": token_error,
        "by_lang": {
            lang: {
                "sample_count": by_lang.get(lang, 0),
                "token_count": sum(tokens_by_lang.get(lang, [])),
                "token_length_distribution": distribution(tokens_by_lang.get(lang, [])),
            }
            for lang in sorted({"hsb", "dsb"} | set(by_lang))
        },
    }
    report = {
        "sample_count": len(rows),
        "by_lang": dict(sorted(by_lang.items())),
        "char_count_by_lang": {lang: sum(vals) for lang, vals in sorted(chars_by_lang.items())},
        "char_length_distribution_by_lang": {lang: distribution(vals) for lang, vals in sorted(chars_by_lang.items())},
        "source_distribution": dict(sorted(by_source.items())),
        "source_kind_distribution": dict(sorted(by_kind.items())),
        "heldout_leakage_hits": leakage_hits,
        "duplicate_hash_count": duplicate_hash_count,
        "replacement_char_rows": replacement_count,
        "html_xml_heavy_rows": html_heavy_count,
        "empty_text_rows": empty_count,
        "token_stats_skipped": token_stats_skipped,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    refuse_overwrite([OUT_TOKEN, OUT_REPORT, OUT_HSB_SAMPLE, OUT_DSB_SAMPLE, OUT_STATUS, OUT_MANIFEST], args.overwrite)
    OUT_TOKEN.write_text(json.dumps(token_stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rng = random.Random(20260618)
    hsb_rows = [row for row in rows if row["lang"] == "hsb"]
    dsb_rows = [row for row in rows if row["lang"] == "dsb"]
    write_samples(OUT_HSB_SAMPLE, rng.sample(hsb_rows, min(50, len(hsb_rows))), "HSB Random Inspection Samples")
    write_samples(OUT_DSB_SAMPLE, rng.sample(dsb_rows, min(50, len(dsb_rows))), "DSB Random Inspection Samples")

    manifest = {
        "run_id": "cpt_v1_official_mono",
        "stage": "interim_cleaning",
        "raw_sources": [
            "llms-limited-resources2026",
            "llms-limited-resources2025",
            "WMT22_UnsupVeryLowResMT_Data",
        ],
        "included_data": [
            "official hsb/dsb monolingual train",
            "official hsb/dsb target side from parallel train",
        ],
        "excluded_data": [
            "dev",
            "valid",
            "validation",
            "test",
            "eval",
            "sample",
            "QA",
            "SC",
            "GC",
            "MR",
            "external FineWeb-2",
            "external Wikipedia",
            "instruction data",
        ],
        "cleaning": {
            "normalize_for_hash": "NFC + strip + collapse_spaces + lowercase",
            "final_text_preserves_case": True,
            "exact_dedup": True,
            "heldout_filtering": True,
        },
        "outputs": {
            "mono_hsb_clean": "data/interim/sorbian/cpt_v1_official_mono/mono_hsb_clean.jsonl",
            "mono_dsb_clean": "data/interim/sorbian/cpt_v1_official_mono/mono_dsb_clean.jsonl",
            "mono_all_clean": "data/interim/sorbian/cpt_v1_official_mono/mono_all_clean.jsonl",
        },
        "counts": {
            "mono_hsb_clean": by_lang.get("hsb", 0),
            "mono_dsb_clean": by_lang.get("dsb", 0),
            "mono_all_clean": len(rows),
        },
    }
    dump_yaml(OUT_MANIFEST, manifest)

    with OUT_STATUS.open("w", encoding="utf-8") as f:
        f.write("# Interim Cleaning Status: CPT V1 Official Mono\n\n")
        f.write("Scope: official hsb/dsb monolingual train data and official hsb/dsb target side from parallel train data.\n\n")
        f.write("No raw files were modified. No processed/LlamaFactory files were generated. No training was started.\n\n")
        f.write("## Final Counts\n\n")
        f.write(f"- hsb clean samples: {by_lang.get('hsb', 0)}\n")
        f.write(f"- dsb clean samples: {by_lang.get('dsb', 0)}\n")
        f.write(f"- total clean samples: {len(rows)}\n")
        f.write(f"- heldout leakage hits after filtering: {leakage_hits}\n")
        f.write(f"- duplicate hashes after dedup: {duplicate_hash_count}\n")
        f.write(f"- token stats skipped: {token_stats_skipped}\n\n")
        f.write("## Outputs\n\n")
        for key, value in manifest["outputs"].items():
            f.write(f"- {key}: `{value}`\n")
        f.write("\n## Inspection Samples\n\n")
        f.write(f"- `{OUT_HSB_SAMPLE.relative_to('/home/zc/wmt26')}`\n")
        f.write(f"- `{OUT_DSB_SAMPLE.relative_to('/home/zc/wmt26')}`\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
