# Eval Output Inventory

Generated: 2026-06-19

Scope: read-only audit of current evaluation outputs under `runs/`, `logs/`,
`reports/`, `scripts/eval/`, `configs/eval/`, and relevant eval scripts. No
existing result file was moved, deleted, renamed, or regenerated.

## 1. Current Git / Branch Status

- Project root: `/home/zc/wmt26`
- Branch: `feat/devsplit-fewshot`
- `reports/`: MISSING
- `repos/llms-limited-resources2026/`: MISSING
- `repos/llms-lim-res-eval-2026/`: MISSING

Current `git status --short` includes pre-existing uncommitted work:

- Modified docs/config/eval files:
  - `AGENTS.md`
  - `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/...`
  - `runs/eval_registry.csv`
- Untracked directories/files:
  - `data/manifests/`
  - `docs/data/`
  - `scripts/data/clean/`
  - `scripts/data/download/`
  - `scripts/eval/watch_wmt26_eval.sh`
  - `docs/eval/EVAL_OUTPUT_INVENTORY.md` from this audit

## 2. Existing Result Directories

Top-level eval result areas:

- `runs/eval/eval_base_qwen35_2b_smoke`
- `runs/eval/eval_base_qwen35_2b_full`
- `runs/eval/eval_base_qwen35_2b_gen_fix_smoke`
- `runs/eval/fewshot_probe`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu`
- `runs/eval/Qwen3.5-2B/sorbian_baselines`
- `runs/eval_registry.csv`

Important observations:

- Base model zero-shot outputs use `runs/eval/eval_base_qwen35_2b_*`.
- Devsplit few-shot outputs use `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1*`.
- 8GPU few-shot outputs are under `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu`.
- Manual/derived baseline comparison output is under
  `runs/eval/Qwen3.5-2B/sorbian_baselines/20260617_zeroshot_vs_devsplit_fewshot`.
- `reports/` does not exist.

## 3. Existing Logs

Eval logs are mostly colocated with run directories, not under top-level `logs/`.

Top-level `logs/` currently contains data-download logs only:

- `logs/data_download/official_wmt_raw_20260618_185219.log`
- `logs/data_download/official_wmt_raw_20260618_190102.log`
- `logs/data_download/wikipedia_sorbian_raw_20260618_190324.log`

Eval logs found under `runs/eval/` include:

- `runs/eval/eval_base_qwen35_2b_smoke/eval.log`
- `runs/eval/eval_base_qwen35_2b_full/run.log`
- `runs/eval/eval_base_qwen35_2b_full/qa.log`
- `runs/eval/eval_base_qwen35_2b_full/gen.log`
- `runs/eval/eval_base_qwen35_2b_full/gen_fixed/run.log`
- `runs/eval/eval_base_qwen35_2b_gen_fix_smoke/run.log`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/*/run.log`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/*/logs/gpu*.log`

## 4. Existing Reports

No top-level `reports/` directory exists.

Existing report-like eval files:

- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260617_161452/summary/results_summary.csv`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260617_161452/summary/results_summary.json`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260617_161452/summary/results_summary.md`
- `runs/eval/Qwen3.5-2B/sorbian_baselines/20260617_zeroshot_vs_devsplit_fewshot/baseline_summary.csv`
- `runs/eval/Qwen3.5-2B/sorbian_baselines/20260617_zeroshot_vs_devsplit_fewshot/baseline_summary.json`
- `runs/eval/Qwen3.5-2B/sorbian_baselines/20260617_zeroshot_vs_devsplit_fewshot/baseline_summary.md`

Important caveat: the `20260617_161452/summary` files summarize the older
broken few-shot 8GPU run, not the latest fixed run `20260618_162149`.

## 5. Detected Eval Runs

| run_dir | likely_model | likely_setting | likely_tasks | has_results_json | has_samples_jsonl | has_logs | file_count | total_size | notes |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| `runs/eval/eval_base_qwen35_2b_smoke` | base Qwen3.5-2B | zero-shot smoke | hsbqa only, limit 5 | yes | yes | yes | 6 | ~614K | single smoke run |
| `runs/eval/eval_base_qwen35_2b_full/qa` | base Qwen3.5-2B | zero-shot full | hsbqa, dsbqa | yes | yes | parent logs | 9 | ~8.2M | QA separate from generative tasks |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed` | base Qwen3.5-2B | zero-shot full | SC, GC, MR, MT | yes | yes | yes | 14 | ~58M | final base generative run after fix |
| `runs/eval/eval_base_qwen35_2b_gen_fix_smoke` | base Qwen3.5-2B | zero-shot smoke | SC, GC, MR, MT, limit 5 | yes | yes | yes | 27 | ~359K | two smoke result JSONs |
| `runs/eval/fewshot_probe/deu-hsb_0shot` | base Qwen3.5-2B | probe zero-shot | deu-hsb, tiny | yes | yes | no | 2 | ~12K | name contains both `fewshot_probe` and `0shot` |
| `runs/eval/fewshot_probe/deu-hsb_2shot` | base Qwen3.5-2B | probe 2-shot | deu-hsb, tiny | yes | yes | no | 2 | ~18K | ad hoc probe |
| `runs/eval/fewshot_probe/hsbqa_2shot` | base Qwen3.5-2B | probe 2-shot | hsbqa, tiny | yes | yes | no | 5 | ~833K | ad hoc probe |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_035102` | Qwen3.5-2B | devsplit few-shot debug | all Sorbian tasks, limit 3 | yes | yes | yes | 28 | ~1.1M | early debug |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_035512` | Qwen3.5-2B | devsplit few-shot debug | all Sorbian tasks, limit 3 | yes | yes | yes | 28 | ~1.1M | early debug |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_035921` | Qwen3.5-2B | devsplit few-shot debug | all Sorbian tasks, limit 3 | yes | yes | yes | 28 | ~1.1M | early debug |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_153337` | Qwen3.5-2B | devsplit few-shot debug | all Sorbian tasks, limit 3 | yes | yes | yes | 28 | ~1.2M | pre-fix debug |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_153619` | Qwen3.5-2B | devsplit few-shot debug | all Sorbian tasks, limit 3 | yes | yes | yes | 28 | ~1.2M | registered |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260618_160509` | Qwen3.5-2B | devsplit few-shot debug | all Sorbian tasks, limit 3 | yes | yes | yes | 28 | ~1.2M | fixed debug, registered |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260617_161452` | Qwen3.5-2B | devsplit few-shot 8GPU | all Sorbian tasks, sharded | yes | yes | yes | 57 | ~117M | older broken 8GPU run; has summary |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162059` | Qwen3.5-2B | attempted 8GPU | incomplete | no | no | no | 4 | ~10K | failed/partial launch skeleton |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149` | Qwen3.5-2B | devsplit few-shot 8GPU | all Sorbian tasks, sharded | yes | yes | yes | 55 | ~123M | latest fixed full 8GPU run; no summary dir |
| `runs/eval/Qwen3.5-2B/sorbian_baselines/20260617_zeroshot_vs_devsplit_fewshot` | Qwen3.5-2B | derived comparison | zero-shot vs old few-shot | yes | no | no | 3 | ~61K | comparison summary, not raw lm-eval output |

## 6. Detected Result JSON Files

Result JSON files are standard `lm-eval` outputs when named `results_*.json`.
They generally include:

- `results`
- `configs`
- `versions`
- `n-shot`
- `n-samples`
- `config`
- `model_name`
- `chat_template`
- `total_evaluation_time_seconds`

Main result JSON groups:

- Base zero-shot QA:
  - `runs/eval/eval_base_qwen35_2b_full/qa/.../results_2026-06-15T03-25-23.017814.json`
  - Tasks: `hsbqa`, `dsbqa`, plus level subtasks.
  - Metrics: `acc,none`, `acc_stderr,none`.

- Base zero-shot generative:
  - `runs/eval/eval_base_qwen35_2b_full/gen_fixed/.../results_2026-06-15T19-02-45.151488.json`
  - Tasks: `hsbsc`, `dsbsc`, `hsbgc`, `dsbgc`, `hsbmr`, `dsbmr`,
    `deu-hsb`, `hsb-deu`, `deu-dsb`, `dsb-deu`, `dsb-hsb`, `hsb-dsb`.
  - Metrics: SC/GC `exact_match_wrong`, `exact_match_corrected`; MR `chrf`
    and `exact_match`; MT `bleu` and `chrf_pp`.

- Devsplit few-shot debug:
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/*/.../results_*.json`
  - Each successful debug result contains all devsplit few-shot tasks with
    `sample_len=3` because `--limit 3` was used.

- Devsplit few-shot 8GPU:
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/<timestamp>/shards/gpu*/.../results_*.json`
  - One result JSON per shard/GPU.
  - QA shard contains QA subtasks and aggregate QA tasks.
  - SC/GC/MR shards each contain hsb/dsb task pair.
  - MT shards contain one or two MT directions.

- Derived summary JSON:
  - `runs/eval/Qwen3.5-2B/sorbian_baselines/20260617_zeroshot_vs_devsplit_fewshot/baseline_summary.json`
  - Top-level keys: `metadata`, `rows`.
  - This is not raw `lm-eval` format.

Current fixed 8GPU result locations:

- QA:
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/.../results_2026-06-18T16-23-58.984302.json`
- SC:
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/.../results_2026-06-18T17-06-48.563686.json`
- GC:
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/.../results_2026-06-18T17-01-41.000561.json`
- MR:
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/.../results_2026-06-18T16-31-36.561326.json`
- MT:
  - `gpu4_mt_de_hsb`, `gpu5_mt_de_dsb`, `gpu6_mt_dsb_hsb`, `gpu7_mt_hsb_dsb`.

## 7. Detected JSONL Sample Files

Sample JSONL files are generated by `--log_samples`. They are per task or per
subtask.

Typical sample scales:

- Debug devsplit runs:
  - each sample file has `3` lines due to `--limit 3`.
- Base zero-shot full:
  - QA: `28-56` lines per level subtask.
  - SC: `2000` lines each.
  - GC: `1250` for dsb, `2000` for hsb.
  - MR: `24` lines each.
  - MT: `4000` lines per direction.
- Devsplit few-shot 8GPU full:
  - QA: `28-56` lines per QA level subtask.
  - SC: `1999` lines each.
  - GC: `1249` for dsb, `1999` for hsb.
  - MR: `23` lines each.
  - MT: `3995` lines per direction.

Sample files are currently mixed directly alongside `results_*.json` in each
lm-eval output directory. They are not grouped under a separate `samples/`
subdirectory.

## 8. Current Naming Problems

Observed problems:

- Random timestamps are used heavily:
  - `20260617_035102`
  - `results_2026-06-18T16-23-58.984302.json`
  - sample filenames also contain timestamps.
- Base model naming is inconsistent:
  - `eval_base_qwen35_2b_full`
  - `Qwen3.5-2B/devsplit_fewshot_v1`
  - `Qwen3.5-2B/devsplit_fewshot_v1_8gpu`
- It is not always obvious whether a run is base / CPT / SFT from the path.
- It is not always obvious whether a run is zero-shot / few-shot:
  - `fewshot_probe/deu-hsb_0shot` contains both `fewshot` and `0shot`.
- Eval config/profile is not consistently encoded in all run directories.
- 8GPU status is encoded in directory name, but aggregation status is not.
  - `20260617_161452` has a `summary/`.
  - `20260618_162149` does not.
- Task results are distributed across shard directories for 8GPU runs.
- Sample files and result JSON files are mixed together.
- There is no uniform manifest schema across all run types.
- `runs/eval_registry.csv` does not include the full 8GPU runs.
- Some incomplete run directories remain:
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034743`
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034834`
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034857`
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_153222`
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162059`

## 9. Existing Aggregation Support

Existing scripts:

- `scripts/eval/eval_base_smoke.sh`
  - Runs a small base QA smoke eval.
  - Does not aggregate.

- `scripts/eval/eval_base_full.sh`
  - Runs base zero-shot QA and generative tasks separately.
  - Writes raw lm-eval outputs.
  - Does not aggregate into one canonical summary.

- `scripts/eval/eval_wmt26_sorbian.sh`
  - Runs `devsplit_fewshot_v1` for one model.
  - Writes a manifest, command, fewshot hashes, run log, and registers debug/full single-process runs.
  - Does not support 8GPU sharding internally.
  - Does not aggregate multiple shard results.

- `scripts/eval/watch_wmt26_eval.sh`
  - Human-readable dashboard for task-sharded 8GPU eval runs.
  - Tracks status/progress/GPU usage.
  - Does not aggregate scores.

- `scripts/analysis/compare_models.py`
  - Reads `runs/eval_registry.csv`.
  - Writes comparison CSV/Markdown.
  - Current parser is a skeleton and only looks for coarse keys like `mt`,
    `qa`, `sc`, `gc`, `mr`.
  - It does not parse current lm-eval nested task metrics correctly.
  - It cannot see runs missing from `eval_registry.csv`, including the 8GPU
    full runs.

Existing aggregation files:

- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260617_161452/summary/*`
  - Appears to be an ad hoc summary for the older broken few-shot run.
  - No reusable script was found in `scripts/eval/` to regenerate this for
    `20260618_162149`.

Conclusion: current aggregation support is partial and not reliable enough for
routine reporting.

## 10. Recommended Target Layout

Recommended future layout:

```text
runs/eval/
  base_qwen35_2b/
    zero_shot/
      sorbian_all_tasks/
        20260619_120000__greedy/
          run_manifest.yaml
          command.sh
          logs/
          raw/
            qa/results.json
            gen/results.json
          samples/
            qa/
            sc/
            gc/
            mr/
            mt/
          results_aggregate.json
          results_summary.csv
          results_summary.md

    few_shot/
      devsplit_fewshot_v1/
        20260619_120000__greedy__8gpu/
          run_manifest.yaml
          shard_manifest.yaml
          logs/
          shards/
            gpu0_qa/
            gpu1_sc/
            gpu2_gc/
            gpu3_mr/
            gpu4_mt_de_hsb/
            gpu5_mt_de_dsb/
            gpu6_mt_dsb_hsb/
            gpu7_mt_hsb_dsb/
          samples/
          results_aggregate.json
          results_summary.csv
          results_summary.md

  cpt_v1_official_mono/
    zero_shot/
      sorbian_all_tasks/
        ...
    few_shot/
      devsplit_fewshot_v1/
        ...
```

Key points:

- Keep raw lm-eval outputs, but put canonical summaries at the run root.
- Make `run_manifest.yaml` mandatory.
- Make `results_aggregate.json`, `results_summary.csv`, and
  `results_summary.md` mandatory for completed runs.
- Put samples under `samples/` instead of mixing them with raw result JSON.
- Put logs under `logs/`.
- For 8GPU runs, keep `shards/` but always aggregate at run root.

## 11. Recommended Run ID Convention

Recommended convention:

```text
<model_tag>__<eval_suite>__<shot_setting>__<decode_setting>__<parallel_setting>__<YYYYMMDD_HHMMSS>
```

Examples:

```text
base_qwen35_2b__sorbian_all_tasks__zero_shot__greedy__1gpu__20260619_120000
base_qwen35_2b__sorbian_all_tasks__devsplit_fewshot_v1__greedy__8gpu__20260619_120000
cpt_v1_official_mono__sorbian_all_tasks__zero_shot__greedy__8gpu__20260619_120000
cpt_v1_official_mono__sorbian_all_tasks__devsplit_fewshot_v1__greedy__8gpu__20260619_120000
```

Recommended manifest fields:

- `run_id`
- `model_tag`
- `model_path`
- `model_family`
- `checkpoint_type`: `base`, `cpt`, `sft`, `opd`, etc.
- `eval_suite`
- `task_profile`
- `shot_setting`
- `decode_setting`
- `parallel_setting`
- `official_eval_dir`
- `include_path`
- `task_names`
- `command`
- `git_commit`
- `git_status_short`
- `started_at`
- `finished_at`
- `status`
- `results_aggregate`
- `results_summary_csv`
- `samples_dir`
- `logs_dir`

## 12. Cleanup Candidates

Do not delete these now. Future cleanup/archive candidates:

- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034743`
  - Contains only command and split manifest; no result JSON.
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034834`
  - Early/incomplete setup run; no result JSON.
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034857`
  - Early/incomplete or failed debug run; no result JSON.
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_153222`
  - Pre-fix run directory with run log but no result JSON.
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162059`
  - Partial failed 8GPU launch; no result JSON/samples/logs.
- `runs/eval/eval_base_qwen35_2b_gen_fix_smoke`
  - Smoke-only outputs; useful for debugging but not a final benchmark.
- `runs/eval/fewshot_probe/*`
  - Ad hoc probe runs; useful historically but not canonical final results.
- Repeated debug result directories under
  `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/`
  - They are limit-3 checks, not final benchmark runs.

## 13. Immediate Next Steps

Recommended next steps:

1. Write `scripts/eval/aggregate_eval_results.py`.
   - Input: one run directory.
   - Detect raw lm-eval `results_*.json` files recursively.
   - Merge shard results.
   - Preserve all per-task metrics.
   - Write:
     - `results_aggregate.json`
     - `results_summary.csv`
     - `results_summary.md`
   - Support both single-process and 8GPU sharded runs.

2. Write `scripts/eval/standardize_eval_run.py`.
   - Input: existing run directory.
   - Read/repair manifest metadata.
   - Validate result/sample/log presence.
   - Optionally register completed runs in `runs/eval_registry.csv`.
   - Should not move files unless explicitly requested.

3. Update eval launch scripts.
   - `eval_base_full.sh` should write into the same normalized layout used by
     future CPT/SFT runs.
   - `eval_wmt26_sorbian.sh` should optionally support sharded run manifests or
     call a separate sharded launcher.
   - 8GPU launcher should always run aggregation at the end.

4. Tighten output directory rules.
   - Avoid bare model names like `Qwen3.5-2B` as top-level run grouping.
   - Include model type (`base`, `cpt_v1_official_mono`, etc.).
   - Include shot setting and eval suite in the run ID.

5. Keep timestamps, but do not rely on timestamps alone.
   - Timestamps are useful for uniqueness.
   - The semantic run ID should still identify model, suite, shot setting,
     decode setting, and parallel setting.

6. Decide registry policy.
   - Every final run should be registered.
   - Debug/smoke runs can be registered with `status=debug` or omitted by policy,
     but the policy should be explicit.
