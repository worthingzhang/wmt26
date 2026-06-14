# 实验结果记录

本文档用于记录实验结果汇总表格。

## 结果汇总表

| model_id | training_type | input_model | MT | QA | SC | GC | MR | notes |
|----------|---------------|-------------|----|----|----|----|----|-------|
| base_qwen35_2b | base | - | - | 0.85* | - | - | - | baseline; hsbqa smoke (limit=5) |
| | | | | | | | | |

\* *hsbqa smoke 结果（limit=5，非完整 dev 集）：group acc=0.85；subtasks: a1=1.00, a2=1.00, b1=0.60, b2=0.80。*

## 关键发现

- Base model `Qwen3.5-2B` 可正常加载并运行 official_eval / lm_eval。
- `hsbqa` smoke 在 `cuda:0` 上成功完成，验证了 main/eval 环境、CUDA、数据集路径和任务配置均正确。

## 详细结果路径

- 训练注册表：`runs/train_registry.csv`
- 评测注册表：`runs/eval_registry.csv`
- 每次评测详细结果：`runs/eval/<eval_id>/`
- 汇总分析：`runs/analysis/`
- 本次 smoke 详细结果：`runs/eval/eval_base_qwen35_2b_smoke/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-07-47.986261.json`
