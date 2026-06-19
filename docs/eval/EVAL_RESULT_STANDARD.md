# Eval Result Standard

This project uses one standard, human-readable and Git-trackable entry point for
each completed evaluation result:

```text
reports/eval/<model_tag>__<eval_setting>/
  RESULTS.md
  scores.csv
  run.yaml
  raw/
  logs/
```

Raw runtime outputs remain under `runs/eval/...`, which is ignored by Git.
Do not commit `runs/eval/` artifacts. Standard reports under `reports/eval/`
should be small and may be committed.

## Directory Names

Use:

```text
<model_tag>__<eval_setting>
```

Examples:

```text
base_qwen35_2b__zero_shot
base_qwen35_2b__fewshot_devsplit_v1
cpt_v1_official_mono__zero_shot
cpt_v1_official_mono__fewshot_devsplit_v1
```

Recommended `eval_setting` values:

```text
zero_shot
fewshot_devsplit_v1
fewshot_devsplit_v2
```

Do not use a random timestamp as the main directory name. Keep timestamps in
`run.yaml` and in the original raw run directory.

## Required Files

- `RESULTS.md`: human-readable summary for quick inspection.
- `scores.csv`: flat task/metric table for spreadsheets, plots, and comparison.
- `run.yaml`: metadata, source paths, parsed files, sample-file counts, warnings.
- `raw/`: symlinks or references to raw lm-eval outputs.
- `logs/`: symlinks or references to logs.

## 8GPU Workflow

After an 8GPU run finishes, run:

```bash
bash scripts/eval/finalize_8gpu_eval_run.sh \
  --source-run-dir <raw_8gpu_run_dir> \
  --standard-run-dir reports/eval/<model_tag>__<eval_setting> \
  --model-tag <model_tag> \
  --eval-setting <eval_setting> \
  --shot-setting <zero_shot_or_fewshot> \
  --parallel-setting 8gpu \
  --no-symlink-artifacts
```

The finalizer calls `scripts/eval/aggregate_eval_results.py`, recursively reads
`results_*.json`, writes the standard files, and updates
`reports/eval/eval_index.csv` by default.

The finalizer does not delete, move, or rewrite the source run directory.

Use `--no-symlink-artifacts` for tracked reports so `raw/` and `logs/` contain
README references instead of symlinks to ignored local run directories.
