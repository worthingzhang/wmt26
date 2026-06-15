# 实验结果记录

本文档用于记录实验结果汇总表格。

## 结果汇总表

| model_id | training_type | input_model | MT | QA | SC | GC | MR | notes |
|----------|---------------|-------------|----|----|----|----|----|-------|
| base_qwen35_2b | base | - | - | 0.85* | - | - | - | baseline; hsbqa smoke (limit=5) |
| base_qwen35_2b | base | - | - | 0.49** | - | - | - | full baseline QA (hsbqa+dsbqa) |
| | | | | | | | | |

\* *hsbqa smoke 结果（limit=5，非完整 dev 集）：group acc=0.85；subtasks: a1=1.00, a2=1.00, b1=0.60, b2=0.80。*

\*\* *完整 baseline 的 QA 部分（hsbqa + dsbqa，无 limit）：group acc 平均约 0.49；hsbqa=0.5159, dsbqa=0.4682。生成式任务（MT/SC/GC/MR）因 official_eval 自定义 chrf_pp metric 聚合时 TypeError 失败，无结果。*

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

## 生成式任务失败记录

- **任务**：`sorbian_dev`（包含 deu-hsb, hsb-deu, deu-dsb, dsb-deu, dsb-hsb, hsb-dsb, hsbgc, dsbgc, hsbmr, dsbmr, hsbsc, dsbsc）
- **失败位置**：`repos/official_eval/lm_eval/api/metrics.py:36` 的 `mean()` 函数
- **错误**：`TypeError: unsupported operand type(s) for +: 'int' and 'list'`
- **原因**：official_eval 中的自定义 `chrf_pp` metric 在聚合时返回了 list 而非 scalar，导致 `sum(arr)` 失败。
- **影响**：QA 部分结果完整可用；生成式任务（MT/SC/GC/MR）无结果。
- **日志**：`runs/eval/eval_base_qwen35_2b_full/gen.log`

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
