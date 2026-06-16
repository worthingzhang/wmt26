# Spec: WMT26 Sorbian devsplit few-shot evaluation profile

**Date:** 2026-06-17  
**Profile:** `devsplit_fewshot_v1`  
**Scope:** Add project-local configs/scripts for fixed devsplit few-shot evaluation of WMT26 Sorbian tasks. Do not modify official evaluation YAMLs.

## Background

The official `repos/official_eval` uses lm-evaluation-harness `0.4.12.dev0`. The official WMT26 Sorbian YAMLs do not declare `num_fewshot`, `fewshot_split`, or `fewshot_config`. Passing `--num_fewshot N` on the CLI would cause lm-eval to fall back to drawing shots from the same test/dev split, creating data leakage. This profile fixes a small set of shots by original dev index, removes them from the eval set, and exposes the shots via `fewshot_config.samples`.

## Goals

1. Create a deterministic, reproducible devsplit for each Sorbian task.
2. Provide local overlay task YAMLs that configure few-shot evaluation without changing official files.
3. Provide a wrapper script `scripts/eval/eval_wmt26_sorbian.sh` that runs the profile.
4. Validate on Qwen3.5-2B with `--limit 3 --write_out --log_samples`.

## Out of scope

- `zero_devsplit_v1`.
- MT training few-shot.
- Synthetic shot generation.
- Modifications to `repos/official_eval/lm_eval/tasks/wmt26-lrl/sorbian/`.

## Directory layout

```
configs/eval/devsplits/sorbian_devsplit_fewshot_v1/
├── manifest.json
├── shots/
│   ├── hsbqa.jsonl
│   ├── dsbqa.jsonl
│   ├── hsbsc.jsonl
│   ├── dsbsc.jsonl
│   ├── hsbgc.jsonl
│   ├── dsbgc.jsonl
│   ├── hsbmr.jsonl
│   ├── dsbmr.jsonl
│   ├── de-hsb_mt.jsonl
│   ├── de-dsb_mt.jsonl
│   └── hsb-dsb_mt.jsonl
└── eval/
    ├── hsbqa.jsonl
    ├── dsbqa.jsonl
    ├── hsbsc.jsonl
    ├── dsbsc.jsonl
    ├── hsbgc.jsonl
    ├── dsbgc.jsonl
    ├── hsbmr.jsonl
    ├── dsbmr.jsonl
    ├── de-hsb_mt.jsonl
    ├── de-dsb_mt.jsonl
    └── hsb-dsb_mt.jsonl

configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/
├── group.yaml
├── utils.py
├── mt/
│   ├── deu-hsb.yaml
│   ├── hsb-deu.yaml
│   ├── deu-dsb.yaml
│   ├── dsb-deu.yaml
│   ├── dsb-hsb.yaml
│   └── hsb-dsb.yaml
├── qa/
│   ├── hsbqa.yaml
│   └── dsbqa.yaml
├── sc/
│   ├── hsbsc.yaml
│   └── dsbsc.yaml
├── gc/
│   ├── hsbgc.yaml
│   └── dsbgc.yaml
└── mr/
    ├── hsbmr.yaml
    └── dsbmr.yaml
```

## Data split rules

1. Read from `/home/zc/wmt26/data/raw/llms-limited-resources2026/Sorbian/` only. Do not modify originals.
2. For each source file produce exactly one `shots/*.jsonl` and one `eval/*.jsonl`.
3. Deterministic selection: first *N* samples by original file order become shots; the remainder become eval.
4. Preserve all original fields. For MT, keep original language-code keys (`de`, `hsb`, `dsb`).
5. Add a private `_devsplit_index` field to every shot/eval record so the source line is traceable.
6. Record in `manifest.json`:
   - `profile`
   - per-task entry with `source_file`, `shots_file`, `eval_file`
   - `source_count`, `shot_count`, `eval_count`
   - `selected_indices`
   - shot `level` for QA
   - `sha256` of shots and eval files

### Shot counts

| Category | Shots |
|---|---|
| MT | 5 per language pair (shared by both directions) |
| QA | 1 per language (shared by A1/A2/B1/B2 subtasks) |
| SC | 1 per language |
| GC | 1 per language |
| MR | 1 per language |

## Overlay task design

- Group YAML declares `group: wmt26_sorbian_devsplit_fewshot_v1` and lists all overlay task names.
- Each overlay task has a unique name (e.g. `deu-hsb_devsplit_fs5_v1`).
- `dataset_kwargs.data_files.test` points to the absolute path of the corresponding `eval/*.jsonl`.
- Each task sets:
  - `num_fewshot: N`
  - `fewshot_config.sampler: first_n`
  - `fewshot_config.samples: !function utils.<loader>`
  - `fewshot_delimiter: "\n\n"`
  - `target_delimiter: " "`
- QA overlay YAMLs keep the official subtask structure (`hsbqa-a1_devsplit_fs1_v1`, etc.) and `process_docs` filters.
- MT overlay YAMLs keep the official `doc_to_text`/`doc_to_target` for the exact direction.
- `utils.py` exposes one loader per source file that returns `list[dict]` from the corresponding `shots/*.jsonl`.

## Eval script

`scripts/eval/eval_wmt26_sorbian.sh MODEL_PATH devsplit_fewshot_v1`

- Activates `.venv`.
- Changes to `repos/official_eval` to run `python -m lm_eval run`.
- Uses `--include_path /home/zc/wmt26/configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1`.
- Uses `--tasks wmt26_sorbian_devsplit_fewshot_v1`.
- Does **not** pass `--num_fewshot`.
- Uses `--log_samples`.
- Writes output to `runs/eval/<model_name>/devsplit_fewshot_v1/<timestamp>/`.
- Saves per-run artifacts:
  - `command.txt`
  - `manifest.json`
  - `fewshot_split_manifest.json` (copy of `configs/eval/devsplits/.../manifest.json`)
  - `fewshot_sha256.txt`
  - `official_eval_git.txt`
  - `overlay_task_git_or_diff.txt`
  - `run.log`
  - lm-eval `results.json` and `samples.jsonl`

## Debug validation

Debug command:

```bash
bash scripts/eval/eval_wmt26_sorbian.sh \
  /home/zc/wmt26/models/base/Qwen3.5-2B \
  devsplit_fewshot_v1 \
  --debug
```

Debug behavior:

- Adds `--limit 3 --write_out --log_samples`.
- Captures full `run.log`.
- Automatically asserts that `run.log` does **not** contain:
  - `"using test_docs as fewshot_docs"`
  - `"Overwriting default num_fewshot"`

Expected prompt composition:

- MT: 5 fixed shots + 1 query.
- QA/SC/GC/MR: 1 fixed shot + 1 query.

## Success criteria

1. All files created in `configs/eval/` only; official YAMLs untouched.
2. `manifest.json` records `selected_indices`, counts, paths, and sha256 for every task.
3. Shot samples do not appear in eval files.
4. Debug run completes without forbidden log warnings.
5. `results.json`, `samples.jsonl`, and all artifacts exist in the output directory.
6. Prompt inspection confirms correct shot counts.
