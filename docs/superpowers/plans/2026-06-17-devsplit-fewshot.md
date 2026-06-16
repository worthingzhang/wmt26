# WMT26 Sorbian devsplit few-shot profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a project-local `devsplit_fewshot_v1` profile for WMT26 Sorbian evaluation: fixed shot extraction from dev data, eval files with shots removed, overlay lm-eval task YAMLs, and a wrapper script.

**Architecture:** A Python generator reads the official dev JSONLs, extracts deterministic first-N shots, writes shot/eval JSONLs and a manifest. lm-eval overlay YAMLs in `configs/eval/tasks/` point to the absolute eval paths and load shots via `fewshot_config.samples`. A Bash wrapper activates `.venv`, runs lm-eval from `repos/official_eval`, and saves run artifacts.

**Tech Stack:** Python 3.12, Bash, lm-evaluation-harness 0.4.12.dev0, standard library (`hashlib`, `json`, `pathlib`).

---

## File map

| File | Responsibility |
|---|---|
| `scripts/data/build_sorbian_devsplit.py` | Reads official dev JSONLs, writes `shots/*.jsonl`, `eval/*.jsonl`, and `manifest.json` under `configs/eval/devsplits/sorbian_devsplit_fewshot_v1/`. |
| `configs/eval/devsplits/sorbian_devsplit_fewshot_v1/manifest.json` | Records profile, source paths, derived paths, counts, selected indices, QA shot level, sha256. |
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/utils.py` | lm-eval utils: one loader per shot file returning `list[dict]`. |
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/group.yaml` | lm-eval group definition. |
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/qa/*.yaml` | QA overlay group YAMLs with A1/A2/B1/B2 subtasks. |
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/mt/*.yaml` | MT overlay task YAMLs for 6 directions. |
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/sc/*.yaml` | SC overlay task YAMLs. |
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/gc/*.yaml` | GC overlay task YAMLs. |
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/mr/*.yaml` | MR overlay task YAMLs. |
| `scripts/eval/eval_wmt26_sorbian.sh` | Wrapper script for `devsplit_fewshot_v1` (and future profiles). |

---

## Task 1: Build the devsplit generator script

**Files:**
- Create: `scripts/data/build_sorbian_devsplit.py`
- Test: `python scripts/data/build_sorbian_devsplit.py --dry-run` (manual)

**Inputs (read-only):**

```text
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/QA/hsb_qa_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/QA/dsb_qa_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/SC/hsb_sc_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/SC/dsb_sc_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/GC/hsb_gc_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/GC/dsb_gc_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/MR/hsb_mr_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/MR/dsb_mr_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/MT/de-hsb_mt_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/MT/de-dsb_mt_dev.jsonl
/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/MT/hsb-dsb_mt_dev.jsonl
```

**Outputs:**

```text
configs/eval/devsplits/sorbian_devsplit_fewshot_v1/shots/*.jsonl
configs/eval/devsplits/sorbian_devsplit_fewshot_v1/eval/*.jsonl
configs/eval/devsplits/sorbian_devsplit_fewshot_v1/manifest.json
```

- [ ] **Step 1: Create the generator skeleton**

```python
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
    {"name": "hsbqa", "source": "QA/hsb_qa_dev.jsonl", "shot_name": "hsbqa"},
    {"name": "dsbqa", "source": "QA/dsb_qa_dev.jsonl", "shot_name": "dsbqa"},
    {"name": "hsbsc", "source": "SC/hsb_sc_dev.jsonl", "shot_name": "hsbsc"},
    {"name": "dsbsc", "source": "SC/dsb_sc_dev.jsonl", "shot_name": "dsbsc"},
    {"name": "hsbgc", "source": "GC/hsb_gc_dev.jsonl", "shot_name": "hsbgc"},
    {"name": "dsbgc", "source": "GC/dsb_gc_dev.jsonl", "shot_name": "dsbgc"},
    {"name": "hsbmr", "source": "MR/hsb_mr_dev.jsonl", "shot_name": "hsbmr"},
    {"name": "dsbmr", "source": "MR/dsb_mr_dev.jsonl", "shot_name": "dsbmr"},
    {"name": "de-hsb_mt", "source": "MT/de-hsb_mt_dev.jsonl", "shot_name": "de-hsb_mt"},
    {"name": "de-dsb_mt", "source": "MT/de-dsb_mt_dev.jsonl", "shot_name": "de-dsb_mt"},
    {"name": "hsb-dsb_mt", "source": "MT/hsb-dsb_mt_dev.jsonl", "shot_name": "hsb-dsb_mt"},
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
            doc = json.loads(line)
            doc.setdefault("_devsplit_index", i)
            docs.append(doc)
    return docs


def save_jsonl(path: Path, docs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def build_task(task: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    source_path = RAW_DIR / task["source"]
    shot_path = OUT_DIR / "shots" / f"{task['shot_name']}.jsonl"
    eval_path = OUT_DIR / "eval" / f"{task['shot_name']}.jsonl"
    shot_count = SHOT_COUNTS[task["shot_name"]]

    docs = load_jsonl(source_path)
    source_count = len(docs)
    if shot_count >= source_count:
        raise ValueError(f"{task['name']}: shot_count {shot_count} >= source_count {source_count}")

    selected_indices = list(range(shot_count))
    shots = [docs[i] for i in selected_indices]
    eval_docs = [docs[i] for i in range(source_count) if i not in set(selected_indices)]

    record = {
        "task": task["name"],
        "source_file": str(source_path),
        "shots_file": str(shot_path),
        "eval_file": str(eval_path),
        "source_count": source_count,
        "shot_count": len(shots),
        "eval_count": len(eval_docs),
        "selected_indices": selected_indices,
    }

    if task["name"].endswith("qa"):
        record["shot_levels"] = [str(s.get("question_level", s.get("level", ""))) for s in shots]

    if dry_run:
        record["shots_sha256"] = "dry-run"
        record["eval_sha256"] = "dry-run"
        return record

    save_jsonl(shot_path, shots)
    save_jsonl(eval_path, eval_docs)
    record["shots_sha256"] = sha256_file(shot_path)
    record["eval_sha256"] = sha256_file(eval_path)
    return record


def main():
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
```

- [ ] **Step 2: Run dry-run to verify structure**

Run:

```bash
cd /home/zc/wmt26
source .venv/bin/activate
python scripts/data/build_sorbian_devsplit.py --dry-run
```

Expected: JSON manifest printed, no files written, all `shots_sha256`/`eval_sha256` equal `"dry-run"`.

- [ ] **Step 3: Run generator for real**

Run:

```bash
python scripts/data/build_sorbian_devsplit.py
```

Expected: `configs/eval/devsplits/sorbian_devsplit_fewshot_v1/shots/` and `eval/` populated; `manifest.json` written.

- [ ] **Step 4: Verify counts and no overlap**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
m = json.loads(Path("configs/eval/devsplits/sorbian_devsplit_fewshot_v1/manifest.json").read_text())
for t in m["tasks"]:
    assert t["shot_count"] + t["eval_count"] == t["source_count"], t["task"]
    print(t["task"], t["source_count"], t["shot_count"], t["eval_count"])
PY
```

Expected: Each line shows task plus counts that sum correctly.

- [ ] **Step 5: Commit**

```bash
git add scripts/data/build_sorbian_devsplit.py configs/eval/devsplits/sorbian_devsplit_fewshot_v1/
git commit -m "feat(eval): add deterministic Sorbian devsplit few-shot data generator and manifest

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Create lm-eval overlay tasks

**Files:**
- Create: `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/utils.py`
- Create: `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/group.yaml`
- Create: `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/qa/hsbqa.yaml`
- Create: `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/qa/dsbqa.yaml`
- Create: `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/mt/*.yaml` (6 files)
- Create: `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/sc/*.yaml` (2 files)
- Create: `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/gc/*.yaml` (2 files)
- Create: `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/mr/*.yaml` (2 files)

- [ ] **Step 1: Write utils.py**

```python
from __future__ import annotations

import json
from pathlib import Path


_SHOTS_DIR = Path("/home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/shots")


def _load_shots(name: str) -> list[dict]:
    path = _SHOTS_DIR / f"{name}.jsonl"
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def hsbqa_shots() -> list[dict]:
    return _load_shots("hsbqa")


def dsbqa_shots() -> list[dict]:
    return _load_shots("dsbqa")


def hsbsc_shots() -> list[dict]:
    return _load_shots("hsbsc")


def dsbsc_shots() -> list[dict]:
    return _load_shots("dsbsc")


def hsbgc_shots() -> list[dict]:
    return _load_shots("hsbgc")


def dsbgc_shots() -> list[dict]:
    return _load_shots("dsbgc")


def hsbmr_shots() -> list[dict]:
    return _load_shots("hsbmr")


def dsbmr_shots() -> list[dict]:
    return _load_shots("dsbmr")


def de_hsb_mt_shots() -> list[dict]:
    return _load_shots("de-hsb_mt")


def de_dsb_mt_shots() -> list[dict]:
    return _load_shots("de-dsb_mt")


def hsb_dsb_mt_shots() -> list[dict]:
    return _load_shots("hsb-dsb_mt")
```

- [ ] **Step 2: Write group.yaml**

```yaml
group: wmt26_sorbian_devsplit_fewshot_v1
task:
  - hsbqa_devsplit_fs1_v1
  - dsbqa_devsplit_fs1_v1
  - hsbsc_devsplit_fs1_v1
  - dsbsc_devsplit_fs1_v1
  - hsbgc_devsplit_fs1_v1
  - dsbgc_devsplit_fs1_v1
  - hsbmr_devsplit_fs1_v1
  - dsbmr_devsplit_fs1_v1
  - deu-hsb_devsplit_fs5_v1
  - hsb-deu_devsplit_fs5_v1
  - deu-dsb_devsplit_fs5_v1
  - dsb-deu_devsplit_fs5_v1
  - dsb-hsb_devsplit_fs5_v1
  - hsb-dsb_devsplit_fs5_v1
metadata:
  version: 1.0
```

- [ ] **Step 3: Write QA overlay YAMLs**

`configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/qa/hsbqa.yaml`:

```yaml
group: hsbqa_devsplit_fs1_v1
task:
  - task: hsbqa-a1_devsplit_fs1_v1
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_a1
  - task: hsbqa-a2_devsplit_fs1_v1
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_a2
  - task: hsbqa-b1_devsplit_fs1_v1
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_b1
  - task: hsbqa-b2_devsplit_fs1_v1
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_b2
dataset_path: json
dataset_kwargs:
  data_files:
    test: /home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/eval/hsbqa.jsonl
dataset_name: null
test_split: test
num_fewshot: 1
fewshot_config:
  sampler: first_n
  samples: !function utils.hsbqa_shots
  fewshot_delimiter: "\n\n"
  target_delimiter: " "
output_type: multiple_choice
doc_to_text: "{{context.strip() if context else ''}}\n\nQuestion:\n{{question.strip() if question else ''}}\n\nPossible answers:\n{% for k, v in possible_answers|dictsort %}{{k}}: {{v}}\n{% endfor %}\nAnswer:"
doc_to_choice: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
doc_to_target: "{{(correct_answer_num|int)-1}}"
metric_list:
  - metric: acc
    aggregation: mean
    higher_is_better: true
aggregate_metric_list:
  - metric: acc
    aggregation: mean
    weight_by_size: false
metadata:
  version: 1.0
```

`configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/qa/dsbqa.yaml`:

```yaml
group: dsbqa_devsplit_fs1_v1
task:
  - task: dsbqa-a1_devsplit_fs1_v1
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_a1
  - task: dsbqa-a2_devsplit_fs1_v1
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_a2
  - task: dsbqa-b1_devsplit_fs1_v1
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_b1
  - task: dsbqa-b2_devsplit_fs1_v1
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_b2
dataset_path: json
dataset_kwargs:
  data_files:
    test: /home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/eval/dsbqa.jsonl
dataset_name: null
test_split: test
num_fewshot: 1
fewshot_config:
  sampler: first_n
  samples: !function utils.dsbqa_shots
  fewshot_delimiter: "\n\n"
  target_delimiter: " "
output_type: multiple_choice
doc_to_text: "{{context.strip() if context else ''}}\n\nQuestion:\n{{question.strip() if question else ''}}\n\nPossible answers:\n{% for k, v in possible_answers|dictsort %}{{k}}: {{v}}\n{% endfor %}\nAnswer:"
doc_to_choice: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
doc_to_target: "{{(correct_answer_num|int)-1}}"
metric_list:
  - metric: acc
    aggregation: mean
    higher_is_better: true
aggregate_metric_list:
  - metric: acc
    aggregation: mean
    weight_by_size: false
metadata:
  version: 1.0
```

- [ ] **Step 4: Write MT overlay YAMLs**

`configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/mt/deu-hsb.yaml`:

```yaml
task: deu-hsb_devsplit_fs5_v1
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: /home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/eval/de-hsb_mt.jsonl
test_split: test
num_fewshot: 5
fewshot_config:
  sampler: first_n
  samples: !function utils.de_hsb_mt_shots
  fewshot_delimiter: "\n\n"
  target_delimiter: " "
doc_to_text: "Translate the following German text to Upper Sorbian. Put it in this format <hsb> Upper Sorbian translation </hsb>.\n<deu> {{de}} </deu>"
doc_to_target: "{{hsb}}"
generation_kwargs:
  until:
    - "<|endoftext|>"
    - "<|im_end|>"
  max_gen_toks: 256
  temperature: 1
  top_p: 1.0
  top_k: 20
  min_p: 0.0
  repetition_penalty: 1.0
filter_list:
  - name: "remove_tags"
    filter:
      - function: "strip_thinking"
      - function: "regex"
        regex_pattern: "<hsb>\\s*([\\s\\S]*?)\\s*(?:</hsb>|$)"
      - function: "take_first"
metric_list:
  - metric: bleu
  - metric: !function lm_eval.tasks.wmt26-lrl.utils.chrf_pp
    aggregation: chrf++
    higher_is_better: true
metadata:
  version: 1.0
```

`configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/mt/hsb-deu.yaml`:

```yaml
task: hsb-deu_devsplit_fs5_v1
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: /home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/eval/de-hsb_mt.jsonl
test_split: test
num_fewshot: 5
fewshot_config:
  sampler: first_n
  samples: !function utils.de_hsb_mt_shots
  fewshot_delimiter: "\n\n"
  target_delimiter: " "
doc_to_text: "Translate the following Upper Sorbian text to German. Put it in this format <deu> German translation </deu>.\n<hsb> {{hsb}} </hsb>"
doc_to_target: "{{de}}"
generation_kwargs:
  until:
    - "<|endoftext|>"
    - "<|im_end|>"
  max_gen_toks: 256
  temperature: 1
  top_p: 1.0
  top_k: 20
  min_p: 0.0
  repetition_penalty: 1.0
filter_list:
  - name: "remove_tags"
    filter:
      - function: "strip_thinking"
      - function: "regex"
        regex_pattern: "<deu>\\s*([\\s\\S]*?)\\s*(?:</deu>|$)"
      - function: "take_first"
metric_list:
  - metric: bleu
  - metric: !function lm_eval.tasks.wmt26-lrl.utils.chrf_pp
    aggregation: chrf++
    higher_is_better: true
metadata:
  version: 1.0
```

Repeat for `deu-dsb.yaml`, `dsb-deu.yaml` (pointing to `de-dsb_mt.jsonl` and `utils.de_dsb_mt_shots`), and `dsb-hsb.yaml`, `hsb-dsb.yaml` (pointing to `hsb-dsb_mt.jsonl` and `utils.hsb_dsb_mt_shots`). Keep official `doc_to_text`/`doc_to_target` exactly.

- [ ] **Step 5: Write SC overlay YAMLs**

`configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/sc/hsbsc.yaml`:

```yaml
task: hsbsc_devsplit_fs1_v1
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: /home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/eval/hsbsc.jsonl
test_split: test
num_fewshot: 1
fewshot_config:
  sampler: first_n
  samples: !function utils.hsbsc_shots
  fewshot_delimiter: "\n\n"
  target_delimiter: " "
doc_to_text: "The following sentence contains at most one misspelled word. Respond with exactly these two tags and nothing else:\n<wrong> misspelled word </wrong> <corrected> correct spelling </corrected>\nIf the sentence has no error, use the literal string CORRECT in both tags:\n<wrong> CORRECT </wrong> <corrected> CORRECT </corrected>\n<sentence> {{input_sentence}} </sentence>"
doc_to_target: "{{incorrect_word}}, {{correct_word}}"
generation_kwargs:
  until:
    - "<|endoftext|>"
    - "<|im_end|>"
  max_gen_toks: 64
  temperature: 1
  top_p: 1.0
  top_k: 20
  min_p: 0.0
  repetition_penalty: 1.0
filter_list:
  - name: "none"
    filter:
      - function: "strip_thinking"
      - function: "take_first"
process_results: !function lm_eval.tasks.wmt26-lrl.utils.process_sc_results
metric_list:
  - metric: exact_match_wrong
    aggregation: mean
    higher_is_better: true
  - metric: exact_match_corrected
    aggregation: mean
    higher_is_better: true
metadata:
  version: 1.0
```

`dsbsc.yaml` mirrors this with `dsbsc_devsplit_fs1_v1`, `dsbsc.jsonl`, `utils.dsbsc_shots`.

- [ ] **Step 6: Write GC overlay YAMLs**

Mirror SC but use official GC `doc_to_text`:

```yaml
task: hsbgc_devsplit_fs1_v1
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: /home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/eval/hsbgc.jsonl
test_split: test
num_fewshot: 1
fewshot_config:
  sampler: first_n
  samples: !function utils.hsbgc_shots
  fewshot_delimiter: "\n\n"
  target_delimiter: " "
doc_to_text: "The following sentence contains at most one grammatically incorrect word. Respond with exactly these two tags and nothing else:\n<wrong> incorrect word </wrong> <corrected> correct form </corrected>\nIf the sentence has no error, use the literal string CORRECT in both tags:\n<wrong> CORRECT </wrong> <corrected> CORRECT </corrected>\n<sentence> {{input_sentence}} </sentence>"
doc_to_target: "{{incorrect_word}}, {{correct_word}}"
generation_kwargs:
  until:
    - "<|endoftext|>"
    - "<|im_end|>"
  max_gen_toks: 64
  temperature: 1
  top_p: 1.0
  top_k: 20
  min_p: 0.0
  repetition_penalty: 1.0
filter_list:
  - name: "none"
    filter:
      - function: "strip_thinking"
      - function: "take_first"
process_results: !function lm_eval.tasks.wmt26-lrl.utils.process_sc_results
metric_list:
  - metric: exact_match_wrong
    aggregation: mean
    higher_is_better: true
  - metric: exact_match_corrected
    aggregation: mean
    higher_is_better: true
metadata:
  version: 1.0
```

`dsbgc.yaml` mirrors with `dsbgc_devsplit_fs1_v1`, `dsbgc.jsonl`, `utils.dsbgc_shots`.

- [ ] **Step 7: Write MR overlay YAMLs**

`configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/mr/hsbmr.yaml`:

```yaml
task: hsbmr_devsplit_fs1_v1
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: /home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v1/eval/hsbmr.jsonl
test_split: test
num_fewshot: 1
fewshot_config:
  sampler: first_n
  samples: !function utils.hsbmr_shots
  fewshot_delimiter: "\n\n"
  target_delimiter: " "
doc_to_text: "Answer this mathematical reasoning question. Place your final answer, using LateX when appropriate, in this format: <answer> answer </answer> {{question}}"
doc_to_target: "{{answer}}"
generation_kwargs:
  until:
    - "<|endoftext|>"
    - "<|im_end|>"
  max_gen_toks: 512
  temperature: 1
  top_p: 1.0
  top_k: 20
  min_p: 0.0
  repetition_penalty: 1.0
filter_list:
  - name: "remove_tags"
    filter:
      - function: "strip_thinking"
      - function: "regex"
        regex_pattern: "<answer>\\s*(.*?)\\s*</answer>"
      - function: "take_first"
metric_list:
  - metric: chrf
  - metric: exact_match
metadata:
  version: 1.0
```

`dsbmr.yaml` mirrors with `dsbmr_devsplit_fs1_v1`, `dsbmr.jsonl`, `utils.dsbmr_shots`.

- [ ] **Step 8: Validate YAMLs load**

Run:

```bash
cd /home/zc/wmt26/repos/official_eval
source /home/zc/wmt26/.venv/bin/activate
python -m lm_eval --tasks wmt26_sorbian_devsplit_fewshot_v1 \
  --include_path /home/zc/wmt26/configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1 \
  --verbosity INFO \
  2>&1 | head -n 40
```

Expected: Task list resolves without YAML errors and shows 14 tasks.

- [ ] **Step 9: Commit**

```bash
git add configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/
git commit -m "feat(eval): add Sorbian devsplit few-shot overlay tasks

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Create the eval wrapper script

**Files:**
- Create: `scripts/eval/eval_wmt26_sorbian.sh`

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
# Evaluate a model on WMT26 Sorbian profiles.
# Usage:
#   bash scripts/eval/eval_wmt26_sorbian.sh MODEL_PATH devsplit_fewshot_v1 [--debug]

set -euo pipefail

PROJECT_ROOT="/home/zc/wmt26"
OFFICIAL_EVAL_DIR="${PROJECT_ROOT}/repos/official_eval"
TASKS_DIR="${PROJECT_ROOT}/configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1"
DEVSPLIT_DIR="${PROJECT_ROOT}/configs/eval/devsplits/sorbian_devsplit_fewshot_v1"
EVAL_REGISTRY="${PROJECT_ROOT}/runs/eval_registry.csv"

if [[ $# -lt 2 ]]; then
    echo "Usage: $(basename "$0") MODEL_PATH PROFILE [OPTIONS]"
    echo "  PROFILE: devsplit_fewshot_v1"
    echo "  OPTIONS: --debug (adds --limit 3 --write_out)"
    exit 1
fi

MODEL_PATH="$1"
PROFILE="$2"
shift 2
DEBUG=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --debug) DEBUG=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ "${PROFILE}" != "devsplit_fewshot_v1" ]]; then
    echo "Error: unsupported profile: ${PROFILE}"
    exit 1
fi

if [[ ! -d "${MODEL_PATH}" ]]; then
    echo "Error: model path does not exist: ${MODEL_PATH}"
    exit 1
fi

MODEL_NAME="$(basename "${MODEL_PATH}")"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="${PROJECT_ROOT}/runs/eval/${MODEL_NAME}/${PROFILE}/${TIMESTAMP}"
mkdir -p "${OUTPUT_DIR}"

# Environment
source "${PROJECT_ROOT}/configs/env/mirrors.env"
source "${PROJECT_ROOT}/.venv/bin/activate"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1

BATCH_SIZE=1
DTYPE="bfloat16"
DEVICE="cuda:0"

EXTRA_ARGS=(--log_samples)
if [[ "${DEBUG}" == true ]]; then
    EXTRA_ARGS+=(--limit 3 --write_out)
fi

COMMAND=(
    python -m lm_eval run
    --model hf
    --model_args "pretrained=${MODEL_PATH},trust_remote_code=True,dtype=${DTYPE},enable_thinking=False"
    --include_path "${TASKS_DIR}"
    --tasks wmt26_sorbian_devsplit_fewshot_v1
    --batch_size "${BATCH_SIZE}"
    --device "${DEVICE}"
    --output_path "${OUTPUT_DIR}"
    "${EXTRA_ARGS[@]}"
)

# Save command
printf '%q ' "${COMMAND[@]}" > "${OUTPUT_DIR}/command.txt"
echo "" >> "${OUTPUT_DIR}/command.txt"

# Save manifest artifacts
cp "${DEVSPLIT_DIR}/manifest.json" "${OUTPUT_DIR}/fewshot_split_manifest.json"
python - <<'PY' - "${DEVSPLIT_DIR}/manifest.json" "${OUTPUT_DIR}/fewshot_sha256.txt"
import json, sys
from pathlib import Path
manifest = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2])
lines = []
for t in manifest["tasks"]:
    lines.append(f"{t['task']} shots={t['shots_sha256']} eval={t['eval_sha256']}")
out.write_text("\n".join(lines) + "\n")
PY

# Git state
cd "${OFFICIAL_EVAL_DIR}"
echo "official_eval repo: ${OFFICIAL_EVAL_DIR}" > "${OUTPUT_DIR}/official_eval_git.txt"
git rev-parse HEAD >> "${OUTPUT_DIR}/official_eval_git.txt"
git status --short >> "${OUTPUT_DIR}/official_eval_git.txt"

cd "${TASKS_DIR}"
echo "overlay tasks dir: ${TASKS_DIR}" > "${OUTPUT_DIR}/overlay_task_git_or_diff.txt"
git rev-parse HEAD >> "${OUTPUT_DIR}/overlay_task_git_or_diff.txt"
git diff -- configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1 >> "${OUTPUT_DIR}/overlay_task_git_or_diff.txt" || true

# Run eval
cd "${OFFICIAL_EVAL_DIR}"
"${COMMAND[@]}" 2>&1 | tee "${OUTPUT_DIR}/run.log"
EVAL_STATUS=${PIPESTATUS[0]}

# Register
if [[ ! -f "${EVAL_REGISTRY}" ]]; then
    echo "eval_id,model_id,model_path,eval_config,result_path,status,notes" > "${EVAL_REGISTRY}"
fi
RESULT_FILE="${OUTPUT_DIR}/results.json"
STATUS=$([[ ${EVAL_STATUS} -eq 0 ]] && echo "completed" || echo "failed")
python "${PROJECT_ROOT}/scripts/utils/register_eval.py" \
    --eval-id "${MODEL_NAME}_${PROFILE}_${TIMESTAMP}" \
    --model-id "${MODEL_NAME}" \
    --model-path "${MODEL_PATH}" \
    --eval-config "${TASKS_DIR}/group.yaml" \
    --result-path "${RESULT_FILE}" \
    --status "${STATUS}" \
    --notes "profile=${PROFILE} debug=${DEBUG}"

echo "${MODEL_NAME}_${PROFILE}_${TIMESTAMP},${MODEL_NAME},${MODEL_PATH},${TASKS_DIR}/group.yaml,${RESULT_FILE},${STATUS},finished at $(date -Iseconds)" >> "${EVAL_REGISTRY}"

# Debug log assertions
if [[ "${DEBUG}" == true ]]; then
    if grep -q "using test_docs as fewshot_docs" "${OUTPUT_DIR}/run.log"; then
        echo "ERROR: found 'using test_docs as fewshot_docs' in run.log"
        exit 1
    fi
    if grep -q "Overwriting default num_fewshot" "${OUTPUT_DIR}/run.log"; then
        echo "ERROR: found 'Overwriting default num_fewshot' in run.log"
        exit 1
    fi
    echo "Debug log assertions passed."
fi

echo "Evaluation finished with status: ${STATUS}"
exit ${EVAL_STATUS}
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/eval/eval_wmt26_sorbian.sh
```

- [ ] **Step 3: Dry-run syntax check**

```bash
bash -n scripts/eval/eval_wmt26_sorbian.sh
```

Expected: no output (success).

- [ ] **Step 4: Commit**

```bash
git add scripts/eval/eval_wmt26_sorbian.sh
git commit -m "feat(eval): add Sorbian devsplit few-shot wrapper script

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Debug validation on Qwen3.5-2B

**Files:**
- No new files; verifies output in `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/<timestamp>/`.

- [ ] **Step 1: Run debug evaluation**

```bash
cd /home/zc/wmt26
bash scripts/eval/eval_wmt26_sorbian.sh \
  /home/zc/wmt26/models/base/Qwen3.5-2B \
  devsplit_fewshot_v1 \
  --debug
```

Expected: lm-eval runs, `run.log` created, script exits 0, no forbidden warnings.

- [ ] **Step 2: Verify artifacts exist**

Run:

```bash
ls runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/*/
```

Expected: `command.txt`, `fewshot_split_manifest.json`, `fewshot_sha256.txt`, `official_eval_git.txt`, `overlay_task_git_or_diff.txt`, `run.log`, `results.json`, `samples.jsonl` (per task subdirectories from lm-eval).

- [ ] **Step 3: Inspect prompt shot counts**

Run:

```bash
python - <<'PY'
import json, glob
from pathlib import Path
samples = []
for p in Path("runs/eval/Qwen3.5-2B/devsplit_fewshot_v1").glob("*/samples/*.jsonl"):
    with open(p) as f:
        for line in f:
            samples.append(json.loads(line))
for s in samples[:5]:
    print(s["doc_id"], len(s.get("arguments", [])), s.get("prompt", "")[:200])
PY
```

Expected: For MT samples, arguments length indicates few-shot turns; visually verify 5-shot + query. For QA/SC/GC/MR, verify 1-shot + query.

- [ ] **Step 4: Confirm no eval leakage**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
m = json.loads(Path("configs/eval/devsplits/sorbian_devsplit_fewshot_v1/manifest.json").read_text())
for t in m["tasks"]:
    shots = [json.loads(l)["_devsplit_index"] for l in open(t["shots_file"])]
    evals = [json.loads(l)["_devsplit_index"] for l in open(t["eval_file"])]
    overlap = set(shots) & set(evals)
    print(t["task"], "overlap:", overlap)
    assert not overlap
print("No overlap verified.")
PY
```

Expected: All overlap sets empty.

- [ ] **Step 5: Confirm no forbidden warnings**

Run:

```bash
LOG=$(ls -t runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/*/run.log | head -1)
if grep -q "using test_docs as fewshot_docs" "$LOG"; then echo "FAIL: test_docs fallback"; exit 1; fi
if grep -q "Overwriting default num_fewshot" "$LOG"; then echo "FAIL: num_fewshot override"; exit 1; fi
echo "Warnings check passed."
```

Expected: `Warnings check passed.`

- [ ] **Step 6: Record results summary**

Capture `results.json` snippet and prompt examples for the final report. No commit needed for run outputs (they live in `runs/` which is git-ignored).

---

## Self-review checklist

1. **Spec coverage**
   - Deterministic first-N split → Task 1.
   - Manifest with indices, counts, sha256, QA shot level → Task 1.
   - Overlay tasks with unique names and absolute eval paths → Task 2.
   - `utils.py` loaders → Task 2.
   - No CLI `--num_fewshot` → Task 3.
   - Run from `repos/official_eval` → Task 3.
   - Debug validation and log assertions → Task 4.

2. **Placeholder scan**
   - No TBD/TODO/fill-in-details patterns.

3. **Type consistency**
   - Loader names in `utils.py` match `!function utils.<name>` references in YAMLs.
   - Shot file basenames match generator and utils.

No gaps found.
