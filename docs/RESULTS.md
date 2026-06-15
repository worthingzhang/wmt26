# 实验结果记录

本文档用于记录实验结果汇总表格。

## 结果汇总表

| model_id | training_type | input_model | MT | QA | SC | GC | MR | notes |
|----------|---------------|-------------|----|----|----|----|----|-------|
| base_qwen35_2b | base | - | - | 0.85* | - | - | - | baseline; hsbqa smoke (limit=5) |
| base_qwen35_2b | base | - | 22.04 / 3.99 | 0.49 | 0.084 | 0.004 | 0.042 | full baseline (QA + sorbian_dev generative; MT=chrf++/bleu, SC/GC/MR=exact_match) |
| | | | | | | | | |

\* *hsbqa smoke 结果（limit=5，非完整 dev 集）：group acc=0.85；subtasks: a1=1.00, a2=1.00, b1=0.60, b2=0.80。*

\*\* *完整 baseline 的 QA 部分（hsbqa + dsbqa，无 limit）：group acc 平均约 0.49；hsbqa=0.5159, dsbqa=0.4682。生成式任务（MT/SC/GC/MR）因 official_eval 自定义 chrf_pp metric 聚合时 TypeError 失败，无结果。*

## 完整生成式 baseline 结果（sorbian_dev，无 limit）

| 任务 | Metric | Value |
|---|---|---|
| **MT 平均** | chrf_pp (chrF++) | 22.04 |
| **MT 平均** | bleu | 3.99 |
| deu-dsb | chrf_pp | 11.0569 |
| deu-dsb | bleu | 1.1789 |
| deu-hsb | chrf_pp | 13.6792 |
| deu-hsb | bleu | 1.1068 |
| dsb-deu | chrf_pp | 23.5037 |
| dsb-deu | bleu | 4.8407 |
| dsb-hsb | chrf_pp | 29.6722 |
| dsb-hsb | bleu | 5.4379 |
| hsb-deu | chrf_pp | 26.5890 |
| hsb-deu | bleu | 6.3707 |
| hsb-dsb | chrf_pp | 27.7563 |
| hsb-dsb | bleu | 4.9888 |
| **SC 平均** | exact_match_corrected | 0.084 |
| dsbsc | exact_match_corrected | 0.0740 |
| dsbsc | exact_match_wrong | 0.0695 |
| hsbsc | exact_match_corrected | 0.0945 |
| hsbsc | exact_match_wrong | 0.0960 |
| **GC 平均** | exact_match_corrected | 0.004 |
| dsbgc | exact_match_corrected | 0.0040 |
| dsbgc | exact_match_wrong | 0.0288 |
| hsbgc | exact_match_corrected | 0.0035 |
| hsbgc | exact_match_wrong | 0.0295 |
| **MR 平均** | exact_match | 0.042 |
| dsbmr | exact_match | 0.0417 |
| dsbmr | chrf | 1.7937 |
| hsbmr | exact_match | 0.0417 |
| hsbmr | chrf | 1.9163 |

- 结果路径：`runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json`
- 官方_eval 修改后重新运行生成式任务成功，未再出现 `chrf_pp` / `acc` 聚合 TypeError。

## 详细 QA 结果（完整 dev 集）

| Group | Subtask | acc |
|---|---|---|
| hsbqa | hsbqa::hsbqa-a1 | 0.7000 |
| hsbqa | hsbqa::hsbqa-a2 | 0.6786 |
| hsbqa | hsbqa::hsbqa-b1 | 0.3636 |
| hsbqa | hsbqa::hsbqa-b2 | 0.3214 |
| hsbqa | **group avg** | **0.5159** |
| dsbqa | dsbqa::dsbqa-a1 | 0.7333 |
| dsbqa | dsbqa::dsbqa-a2 | 0.6071 |
| dsbqa | dsbqa::dsbqa-b1 | 0.3182 |
| dsbqa | dsbqa::dsbqa-b2 | 0.2143 |
| dsbqa | **group avg** | **0.4682** |

## 生成式任务失败与修复记录

- **任务**：`sorbian_dev`（包含 deu-hsb, hsb-deu, deu-dsb, dsb-deu, dsb-hsb, hsb-dsb, hsbgc, dsbgc, hsbmr, dsbmr, hsbsc, dsbsc）
- **初次失败位置**：`repos/official_eval/lm_eval/api/metrics.py:36` 的 `mean()` 函数
- **初次错误**：`TypeError: unsupported operand type(s) for +: 'int' and 'list'`
- **根因**：Sorbian MR 任务 YAML 中使用了 `metric: acc`，但 `acc` 不适用于 `generate_until` 输出，导致每个样本返回 `[gold, pred]` list，最终被 `mean` 聚合时失败。
- **修复**：将 `repos/official_eval/lm_eval/tasks/wmt26-lrl/sorbian/mr/hsbmr.yaml` 和 `dsbmr.yaml` 中的 `acc` 改为 `exact_match`。
- **修复后状态**：✅ 完整生成式 baseline 已成功运行完毕，结果见上表。
- **修复 commit**：`repos/official_eval@1e6ab97b005464fc0e4581cc850499eac4dc2bc9`
- **日志**：
  - 失败日志：`runs/eval/eval_base_qwen35_2b_full/gen.log`
  - 成功日志：`runs/eval/eval_base_qwen35_2b_full/gen_fixed/run.log`

## 关键发现

- Base model `Qwen3.5-2B` 可正常加载并运行 official_eval / lm_eval。
- `hsbqa` smoke 和完整 QA 评测均成功。
- 完整 baseline 的生成式任务因 `chrf_pp` metric 实现问题失败，需要修复 official_eval 中的 metric 或向上游报告。

## 详细结果路径

- 训练注册表：`runs/train_registry.csv`
- 评测注册表：`runs/eval_registry.csv`
- 每次评测详细结果：`runs/eval/<eval_id>/`
- 汇总分析：`runs/analysis/`
- 本次 smoke 详细结果：`runs/eval/eval_base_qwen35_2b_smoke/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-07-47.986261.json`
- 本次 full baseline QA 详细结果：`runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json`
- 本次 full baseline 生成式详细结果：`runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json`
