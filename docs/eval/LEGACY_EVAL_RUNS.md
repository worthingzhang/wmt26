# Legacy Eval Runs

This document separates formal standardized results from smoke, debug, broken,
and manual comparison outputs. These legacy directories are kept in place for
traceability but should not be used as canonical benchmark results.

## Formal Standardized Runs

| standard_dir | status | source | notes |
|---|---|---|---|
| `reports/eval/base_qwen35_2b__zero_shot` | aggregated | `runs/eval/eval_base_qwen35_2b_full` | Formal base zero-shot full run. QA and generative tasks are both under the source directory. |
| `reports/eval/base_qwen35_2b__fewshot_devsplit_v1` | aggregated | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149` | Latest fixed 8GPU devsplit few-shot run. |

## Debug Runs

| source_dir | reason | notes |
|---|---|---|
| `runs/eval/eval_base_qwen35_2b_smoke` | smoke | Small base zero-shot QA smoke run; not a full benchmark. |
| `runs/eval/eval_base_qwen35_2b_gen_fix_smoke` | smoke | Small base zero-shot generative smoke run; not a full benchmark. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_035102` | debug | Limit-3 devsplit few-shot debug run. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_035512` | debug | Limit-3 devsplit few-shot debug run. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_035921` | debug | Limit-3 devsplit few-shot debug run. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_153337` | debug | Pre-fix limit-3 devsplit few-shot debug run. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_153619` | debug | Registered pre-fix limit-3 devsplit few-shot debug run. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260618_160509` | debug | Registered fixed limit-3 devsplit few-shot debug run. |
| `runs/eval/fewshot_probe/deu-hsb_0shot` | probe | Ad hoc tiny probe; path name includes `fewshot_probe` but setting is 0-shot. |
| `runs/eval/fewshot_probe/deu-hsb_2shot` | probe | Ad hoc tiny 2-shot MT probe. |
| `runs/eval/fewshot_probe/hsbqa_2shot` | probe | Ad hoc tiny 2-shot QA probe. |

## Broken / Obsolete Runs

| source_dir | reason | notes |
|---|---|---|
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260617_161452` | broken | Broken few-shot run. Few-shot assistant demonstrations used the wrong untagged target format, so this does not represent the fixed profile. Its `summary/` files are obsolete for current reporting. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162059` | incomplete | Partial failed 8GPU launch skeleton with no full result JSON/samples/logs. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034743` | incomplete | Early setup/debug directory with no final result JSON. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034834` | incomplete | Early setup/debug directory with no final result JSON. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_034857` | incomplete | Early setup/debug directory with no final result JSON. |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1/20260617_153222` | incomplete | Pre-fix directory with run log but no final result JSON. |

## Manual Comparison Runs

| source_dir | reason | notes |
|---|---|---|
| `runs/eval/Qwen3.5-2B/sorbian_baselines/20260617_zeroshot_vs_devsplit_fewshot` | manual comparison | Derived zero-shot vs old few-shot summary. Not raw lm-eval output and includes the obsolete broken few-shot run. |
