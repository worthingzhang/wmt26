#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter

from official_mono_common import INTERIM, ensure_dirs, read_jsonl, refuse_overwrite

IN_PATH = INTERIM / "candidate_mono_all.jsonl"
OUT_CLEAN = INTERIM / "cleaned_before_leakage.jsonl"
OUT_REPORT = INTERIM / "basic_cleaning_report.json"
OUT_REMOVED = INTERIM / "basic_cleaning_removed.jsonl"

URL_RE = re.compile(r"^(https?://|www\.)\S+$", re.I)
TAG_RE = re.compile(r"</?[A-Za-z][^>]{0,120}>")
README_RE = re.compile(r"^(#|```|Copyright\b|License\b|LICENCE\b|MIT License\b|Apache License\b|GNU GENERAL PUBLIC LICENSE\b|#!/w*|import\s+\w+|from\s+\w+\s+import\b)")


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = "".join(" " if unicodedata.category(ch)[0] == "C" else ch for ch in text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def removal_reason(text: str) -> str | None:
    if not text:
        return "empty"
    non_space = sum(1 for ch in text if not ch.isspace())
    if non_space < 3:
        return "too_short_chars"
    if len(text.split()) < 2 and non_space < 8:
        return "too_short_tokens"
    if URL_RE.match(text):
        return "url_only"
    chars = [ch for ch in text if not ch.isspace()]
    if chars:
        alnum = sum(1 for ch in chars if ch.isalnum())
        alpha = sum(1 for ch in chars if ch.isalpha())
        if alpha == 0 and alnum / max(1, len(chars)) < 0.5:
            return "numbers_punct_only"
    if text.count("\ufffd") / max(1, len(text)) > 0.02:
        return "replacement_char_high"
    tag_chars = sum(len(m.group(0)) for m in TAG_RE.finditer(text))
    if tag_chars / max(1, len(text)) > 0.35:
        return "html_xml_tag_heavy"
    if README_RE.search(text):
        return "readme_license_script_residual"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    ensure_dirs()
    kept = []
    removed = []
    reason_counts = Counter()
    input_count = 0
    for row in read_jsonl(IN_PATH):
        input_count += 1
        if args.limit and input_count > args.limit:
            break
        original = row.get("text", "")
        text = clean_text(original)
        reason = removal_reason(text)
        if reason:
            item = dict(row)
            item["cleaned_text_preview"] = text[:200]
            item["removed_reason"] = reason
            removed.append(item)
            reason_counts[reason] += 1
        else:
            item = dict(row)
            item["text"] = text
            kept.append(item)

    report = {
        "input_count": input_count if not args.limit else min(input_count, args.limit),
        "kept_count": len(kept),
        "removed_count": len(removed),
        "removed_by_reason": dict(sorted(reason_counts.items())),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    refuse_overwrite([OUT_CLEAN, OUT_REPORT, OUT_REMOVED], args.overwrite)
    with OUT_CLEAN.open("w", encoding="utf-8") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with OUT_REMOVED.open("w", encoding="utf-8") as f:
        for row in removed:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
