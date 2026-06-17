#!/usr/bin/env python3
"""Build deterministic devsplit shot/eval files for WMT26 Sorbian few-shot eval."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/zc/wmt26")
RAW_DIR = PROJECT_ROOT / "data/raw/llms-limited-resources2026/Sorbian"
OUT_DIR = PROJECT_ROOT / "configs/eval/devsplits/sorbian_devsplit_fewshot_v1"

SHOT_COUNTS = {
    "hsbqa": 1,
    "dsbqa": 1,
    "hsbsc": 1,
    "dsbsc": 1,
    "hsbgc": 1,
    "dsbgc": 1,
    "hsbmr": 1,
    "dsbmr": 1,
    "de-hsb_mt": 5,
    "de-dsb_mt": 5,
    "hsb-dsb_mt": 5,
}

TASKS: list[dict[str, Any]] = [
    {"name": "hsbqa", "source": "QA/hsb_qa_dev.jsonl"},
    {"name": "dsbqa", "source": "QA/dsb_qa_dev.jsonl"},
    {"name": "hsbsc", "source": "SC/hsb_sc_dev.jsonl"},
    {"name": "dsbsc", "source": "SC/dsb_sc_dev.jsonl"},
    {"name": "hsbgc", "source": "GC/hsb_gc_dev.jsonl"},
    {"name": "dsbgc", "source": "GC/dsb_gc_dev.jsonl"},
    {"name": "hsbmr", "source": "MR/hsb_mr_dev.jsonl"},
    {"name": "dsbmr", "source": "MR/dsb_mr_dev.jsonl"},
    {"name": "de-hsb_mt", "source": "MT/de-hsb_mt_dev.jsonl"},
    {"name": "de-dsb_mt", "source": "MT/de-dsb_mt_dev.jsonl"},
    {"name": "hsb-dsb_mt", "source": "MT/hsb-dsb_mt_dev.jsonl"},
]

assert all(t["name"] in SHOT_COUNTS for t in TASKS), "Every TASKS entry must have a matching SHOT_COUNTS key"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            try:
                doc = {**json.loads(line), "_devsplit_index": i}
            except json.JSONDecodeError as exc:
                raise json.JSONDecodeError(
                    f"JSON decode error in {path} at line {i + 1}: {exc.msg}",
                    exc.doc,
                    exc.pos,
                ) from exc
            docs.append(doc)
    return docs


def _get_level(doc: dict[str, Any]) -> str:
    if "question_level" in doc:
        return str(doc["question_level"])
    if "level" in doc:
        return str(doc["level"])
    raise KeyError(f"Document missing both 'question_level' and 'level' keys: {doc.keys()}")


def save_jsonl(path: Path, docs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def build_task(task: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    source_path = RAW_DIR / task["source"]
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    shot_path = OUT_DIR / "shots" / f"{task['name']}.jsonl"
    eval_path = OUT_DIR / "eval" / f"{task['name']}.jsonl"
    shot_count = SHOT_COUNTS[task["name"]]

    docs = load_jsonl(source_path)
    source_count = len(docs)
    if shot_count >= source_count:
        raise ValueError(f"{task['name']}: shot_count {shot_count} >= source_count {source_count}")

    shots = docs[:shot_count]
    eval_docs = docs[shot_count:]

    record = {
        "task": task["name"],
        "source_file": str(source_path),
        "shots_file": str(shot_path),
        "eval_file": str(eval_path),
        "source_count": source_count,
        "shot_count": len(shots),
        "eval_count": len(eval_docs),
        "selected_indices": list(range(shot_count)),
    }

    if task["name"].endswith("qa"):
        record["shot_levels"] = [_get_level(s) for s in shots]

    if dry_run:
        record["shots_sha256"] = "dry-run"
        record["eval_sha256"] = "dry-run"
        return record

    save_jsonl(shot_path, shots)
    save_jsonl(eval_path, eval_docs)
    record["shots_sha256"] = sha256_file(shot_path)
    record["eval_sha256"] = sha256_file(eval_path)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = [build_task(t, args.dry_run) for t in TASKS]
    manifest = {
        "profile": "devsplit_fewshot_v1",
        "raw_dir": str(RAW_DIR),
        "tasks": entries,
    }

    if not args.dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        manifest_path = OUT_DIR / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"Wrote {manifest_path}")

    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
