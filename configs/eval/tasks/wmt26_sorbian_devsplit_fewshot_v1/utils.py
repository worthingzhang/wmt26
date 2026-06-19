"""Local utility module for WMT26 Sorbian devsplit few-shot overlay tasks.

This module provides shot-loading helpers used by the overlay YAMLs under
``configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/``.  Each subdirectory
(qa, mt, sc, gc, mr) contains a symlink to this file so that lm-eval can
resolve ``!function utils.X`` relative to each YAML's directory.

The separate ``lm_eval.tasks.wmt26-lrl.utils`` module (inside the official eval
repo) is used for ``process_docs``, ``process_results``, and the ``chrf_pp``
metric function.
"""

from __future__ import annotations

import json
from pathlib import Path


_SHOTS_DIR = Path("/home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/shots")


def _load_shots(name: str) -> list[dict]:
    path = _SHOTS_DIR / f"{name}.jsonl"
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def hsbqa_shots() -> list[dict]: return _load_shots("hsbqa")
def dsbqa_shots() -> list[dict]: return _load_shots("dsbqa")
def hsbsc_shots() -> list[dict]: return _load_shots("hsbsc")
def dsbsc_shots() -> list[dict]: return _load_shots("dsbsc")
def hsbgc_shots() -> list[dict]: return _load_shots("hsbgc")
def dsbgc_shots() -> list[dict]: return _load_shots("dsbgc")
def hsbmr_shots() -> list[dict]: return _load_shots("hsbmr")
def dsbmr_shots() -> list[dict]: return _load_shots("dsbmr")
def de_hsb_mt_shots() -> list[dict]: return _load_shots("de-hsb_mt")
def de_dsb_mt_shots() -> list[dict]: return _load_shots("de-dsb_mt")
def hsb_dsb_mt_shots() -> list[dict]: return _load_shots("hsb-dsb_mt")


def target_hsb(doc: dict) -> str:
    return f"<hsb> {doc['hsb']} </hsb>"


def target_dsb(doc: dict) -> str:
    return f"<dsb> {doc['dsb']} </dsb>"


def target_deu(doc: dict) -> str:
    return f"<deu> {doc['de']} </deu>"


def target_answer(doc: dict) -> str:
    return f"<answer> {doc['answer']} </answer>"


def target_wrong_corrected(doc: dict) -> str:
    return f"<wrong> {doc['incorrect_word']} </wrong> <corrected> {doc['correct_word']} </corrected>"
