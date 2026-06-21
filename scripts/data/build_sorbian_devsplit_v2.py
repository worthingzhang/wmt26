#!/usr/bin/env python3
"""Build deterministic, stratified devsplit shot/eval files for WMT26 Sorbian few-shot eval.

This script creates a balanced few-shot split by selecting shots that cover key
variations in the data (correct/error for SC/GC, different answer choices/levels
for QA, different answer values for MR, length diversity for MT).  Selected shots
are removed from the eval set to prevent leakage.

Output profile: ``sorbian_devsplit_fewshot_v2``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/home/zc/wmt26")
RAW_DIR = PROJECT_ROOT / "data/raw/llms-limited-resources2026/Sorbian"
OUT_DIR = PROJECT_ROOT / "configs/eval/devsplits/sorbian_devsplit_fewshot_v2"
PROFILE = "sorbian_devsplit_fewshot_v2"

# shot count and selection strategy per task
TASKS: list[dict[str, Any]] = [
    # QA: cover both binary answer choices and a higher-level question
    {"name": "hsbqa", "source": "QA/hsb_qa_dev.jsonl", "shot_count": 3,
     "strategy": "qa_stratified", "level_order": ["A1", "A1", "A2"],
     "answer_order": [1, 2, None]},  # None = any answer
    {"name": "dsbqa", "source": "QA/dsb_qa_dev.jsonl", "shot_count": 3,
     "strategy": "qa_stratified", "level_order": ["A1", "A1", "A2"],
     "answer_order": [1, 2, None]},

    # SC/GC: one correct example + one error example
    {"name": "hsbsc", "source": "SC/hsb_sc_dev.jsonl", "shot_count": 2,
     "strategy": "correctness_balanced"},
    {"name": "dsbsc", "source": "SC/dsb_sc_dev.jsonl", "shot_count": 2,
     "strategy": "correctness_balanced"},
    {"name": "hsbgc", "source": "GC/hsb_gc_dev.jsonl", "shot_count": 2,
     "strategy": "correctness_balanced"},
    {"name": "dsbgc", "source": "GC/dsb_gc_dev.jsonl", "shot_count": 2,
     "strategy": "correctness_balanced"},

    # MR: two examples with different numeric answers to avoid value bias
    {"name": "hsbmr", "source": "MR/hsb_mr_dev.jsonl", "shot_count": 2,
     "strategy": "mr_diverse"},
    {"name": "dsbmr", "source": "MR/dsb_mr_dev.jsonl", "shot_count": 2,
     "strategy": "mr_diverse"},

    # MT: keep 5 shots, but ensure length diversity
    {"name": "de-hsb_mt", "source": "MT/de-hsb_mt_dev.jsonl", "shot_count": 5,
     "strategy": "mt_diverse"},
    {"name": "de-dsb_mt", "source": "MT/de-dsb_mt_dev.jsonl", "shot_count": 5,
     "strategy": "mt_diverse"},
    {"name": "hsb-dsb_mt", "source": "MT/hsb-dsb_mt_dev.jsonl", "shot_count": 5,
     "strategy": "mt_diverse"},
]


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


def save_jsonl(path: Path, docs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def _is_correct(doc: dict[str, Any]) -> bool:
    word = doc.get("incorrect_word") or ""
    return word.strip().upper() == "CORRECT"


def _get_level(doc: dict[str, Any]) -> str:
    if "question_level" in doc:
        return str(doc["question_level"]).strip().upper()
    if "level" in doc:
        return str(doc["level"]).strip().upper()
    raise KeyError(f"Document missing both 'question_level' and 'level' keys: {doc.keys()}")


def select_correctness_balanced(docs: list[dict[str, Any]], shot_count: int) -> list[int]:
    """Select an equal number of correct and error examples.

    Falls back to first-N if the requested balance cannot be met exactly.
    """
    correct = [i for i, d in enumerate(docs) if _is_correct(d)]
    errors = [i for i, d in enumerate(docs) if not _is_correct(d)]

    n_correct = shot_count // 2
    n_error = shot_count - n_correct

    # adjust if one category is too small
    if len(correct) < n_correct:
        n_correct = len(correct)
        n_error = min(len(errors), shot_count - n_correct)
    if len(errors) < n_error:
        n_error = len(errors)
        n_correct = min(len(correct), shot_count - n_error)

    selected = correct[:n_correct] + errors[:n_error]
    # pad with remaining docs if counts don't add up (shouldn't happen in practice)
    used = set(selected)
    for i, _ in enumerate(docs):
        if len(selected) >= shot_count:
            break
        if i not in used:
            selected.append(i)
    return sorted(selected)


def select_qa_stratified(
    docs: list[dict[str, Any]],
    shot_count: int,
    level_order: list[str],
    answer_order: list[int | None],
) -> list[int]:
    """Select QA shots covering requested levels and answer choices."""
    assert len(level_order) == shot_count
    assert len(answer_order) == shot_count

    selected: list[int] = []
    used: set[int] = set()

    for level, answer in zip(level_order, answer_order):
        level = level.strip().upper()
        # find first unused doc matching level and (optionally) answer
        for i, d in enumerate(docs):
            if i in used:
                continue
            if _get_level(d) != level:
                continue
            if answer is not None and d.get("correct_answer_num") != answer:
                continue
            selected.append(i)
            used.add(i)
            break
        else:
            # fallback: any doc of the requested level
            for i, d in enumerate(docs):
                if i not in used and _get_level(d) == level:
                    selected.append(i)
                    used.add(i)
                    break

    # pad if needed
    for i, _ in enumerate(docs):
        if len(selected) >= shot_count:
            break
        if i not in used:
            selected.append(i)
            used.add(i)

    return sorted(selected)


def select_mr_diverse(docs: list[dict[str, Any]], shot_count: int) -> list[int]:
    """Select MR shots with different answer values to avoid numeric bias."""
    selected: list[int] = []
    used_answers: set[Any] = set()

    # prefer docs with unseen answers
    for i, d in enumerate(docs):
        if len(selected) >= shot_count:
            break
        ans = d.get("answer")
        if ans not in used_answers:
            selected.append(i)
            used_answers.add(ans)

    # pad with first remaining docs
    used = set(selected)
    for i, _ in enumerate(docs):
        if len(selected) >= shot_count:
            break
        if i not in used:
            selected.append(i)

    return sorted(selected)


def select_mt_diverse(docs: list[dict[str, Any]], shot_count: int) -> list[int]:
    """Select MT shots with diverse source-sentence length.

    Picks one short, one long, and fills the rest from the beginning of the file.
    """
    if shot_count <= 2:
        return list(range(shot_count))

    # rank by source length (German for de-*, source language for hsb-dsb)
    def _source_len(i: int) -> int:
        d = docs[i]
        text = d.get("de") or d.get("hsb") or d.get("dsb") or ""
        return len(text.split())

    by_len = sorted(range(len(docs)), key=_source_len)
    selected = [by_len[0], by_len[-1]]  # shortest and longest

    # fill remaining slots with the earliest docs not yet selected
    used = set(selected)
    for i, _ in enumerate(docs):
        if len(selected) >= shot_count:
            break
        if i not in used:
            selected.append(i)

    return sorted(selected)


def select_shots(task: dict[str, Any], docs: list[dict[str, Any]]) -> list[int]:
    strategy = task["strategy"]
    shot_count = task["shot_count"]

    if strategy == "correctness_balanced":
        return select_correctness_balanced(docs, shot_count)
    if strategy == "qa_stratified":
        return select_qa_stratified(
            docs, shot_count,
            level_order=task["level_order"],
            answer_order=task["answer_order"],
        )
    if strategy == "mr_diverse":
        return select_mr_diverse(docs, shot_count)
    if strategy == "mt_diverse":
        return select_mt_diverse(docs, shot_count)

    raise ValueError(f"Unknown strategy: {strategy}")


def build_task(task: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    source_path = RAW_DIR / task["source"]
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    shot_path = OUT_DIR / "shots" / f"{task['name']}.jsonl"
    eval_path = OUT_DIR / "eval" / f"{task['name']}.jsonl"
    shot_count = task["shot_count"]

    docs = load_jsonl(source_path)
    source_count = len(docs)

    selected_indices = select_shots(task, docs)
    if len(selected_indices) != shot_count:
        raise ValueError(
            f"{task['name']}: expected {shot_count} shots, got {len(selected_indices)}"
        )

    shots = [docs[i] for i in selected_indices]
    eval_docs = [d for i, d in enumerate(docs) if i not in selected_indices]

    record: dict[str, Any] = {
        "task": task["name"],
        "source_file": str(source_path),
        "shots_file": str(shot_path),
        "eval_file": str(eval_path),
        "source_count": source_count,
        "shot_count": len(shots),
        "eval_count": len(eval_docs),
        "selected_indices": selected_indices,
        "strategy": task["strategy"],
    }

    if task["name"].endswith("qa"):
        record["shot_levels"] = [_get_level(s) for s in shots]
        record["shot_answers"] = [s.get("correct_answer_num") for s in shots]

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
        "profile": PROFILE,
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
