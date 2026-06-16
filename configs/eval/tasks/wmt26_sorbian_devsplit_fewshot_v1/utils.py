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
