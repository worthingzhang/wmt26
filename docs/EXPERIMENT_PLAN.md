# 实验计划

本文档说明本项目的核心实验设计思想：把训练过程建模为**模型实验图（Model Experiment DAG）**。

## 核心思想：CPT / SFT / OPD 是并列训练算子

不是固定流水线，而是三个并列算子：

- `train_cpt(input_model, data_config, train_config) → output_model`
- `train_sft(input_model, data_config, train_config) → output_model`
- `train_opd(student_model, teacher_model, prompt_config, train_config) → output_model`

每个算子接收一个或多个输入模型，输出一个新模型。新模型又可以作为后续算子的输入。

## 模型实验图

```
Base (Qwen3.5-2B)
    │
    ├── CPT ──► CPT_v1 ──► SFT ──► SFT_from_CPT_v1
    │              │
    │              └───► OPD ──► OPD_from_CPT_v1
    │
    ├── SFT ──► SFT_v1 ──► OPD ──► OPD_from_SFT_v1
    │
    └── OPD ──► OPD_from_Base_v1
```

实际实验远不止这些，还可能包括：

- 不同数据配比的 CPT 实验
- 不同数据配比的 SFT 实验
- 不同 teacher 的 OPD 实验
- 多次 OPD 迭代
- 混合训练路径

## 候选训练路径

| 路径 | 目的 |
|------|------|
| Base | 基线 |
| Base → CPT | 继续预训练影响 |
| Base → SFT | 监督微调影响 |
| CPT → SFT | CPT 后再 SFT |
| SFT → OPD | 用 SFT 模型作为 student，进行 OPD |
| CPT → OPD | 用 CPT 模型作为 student，进行 OPD |
| CPT → SFT → OPD | 完整路径 |
| Base → OPD | 直接对 base 做 OPD |

## 统一评测

每个模型产出后，都必须调用官方评测仓库进行统一评测。评测结果写入 `runs/eval_registry.csv`。

比较维度包括：

- MT（机器翻译）
- QA（问答）
- SC（分类）
- GC（生成挑战）
- MR（多跳推理）

## 数据配比实验

对每一类训练方法，都可以进行数据配比消融：

- CPT：语言配比、领域配比、单语/平行语配比
- SFT：任务配比、语言配比、官方/外部/合成配比
- OPD：prompt 配比、任务配比、teacher 选择

## 记录规范

每个实验需要记录：

- `run_id`：训练运行 ID
- `model_id`：模型 ID
- `input_model`：输入模型
- `teacher_model`：OPD 教师模型
- `data_config`：数据配置
- `train_config`：训练配置
- 训练日志路径、模型路径、评测结果路径

详见 [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md)。
