# 项目结构说明

本文档详细解释 `/home/zc/wmt26` 下每个目录的职责。

## 顶层目录

| 目录 | 职责 |
|------|------|
| `docs/` | 项目文档、设计说明、操作手册 |
| `repos/` | 外部仓库，作为训练/评测引擎 |
| `data/` | 项目数据资产，所有训练/评测数据 |
| `models/` | 模型节点库，包括 base、checkpoint、teacher、final |
| `configs/` | 参数配置，包括数据配置、训练配置、评测配置 |
| `scripts/` | 统一调用入口，所有实验通过脚本触发 |
| `runs/` | 实验运行记录，日志、结果、注册表 |
| `submissions/` | 最终提交产物 |

## `repos/` — 外部引擎

`repos/` 只放外部仓库，不放大文件或实验数据。

- `repos/official_eval/`：官方评测仓库。只负责读取模型路径并执行官方任务评测。
- `repos/thunlp_opd/`：清华 OPD 仓库，包含 LlamaFactory 和 verl/OPD 相关代码。作为 training backend。

**约束**：

- 不要把训练数据或模型 checkpoint 放进这两个仓库。
- 尽量不要直接修改 `thunlp_opd` 源码；如需修改，先说明原因，并优先通过主项目的 `scripts/configs` 传参解决。

## `data/` — 数据资产

```
data/
├── raw/              # 原始数据，不提交到 git
├── interim/          # 中间产物，不提交到 git
├── processed/        # 处理后数据，不提交到 git
│   ├── cpt/          # CPT 语料
│   ├── sft/          # SFT 数据
│   ├── opd_prompts/  # OPD prompt 池
│   ├── opd_coldstart/# OPD cold-start 数据
│   └── eval/         # 评测数据
├── manifests/        # 数据清单，提交到 git
├── cache/            # 缓存，不提交到 git
└── README.md         # 数据说明
```

- `raw/`：官方数据、往年数据、外部公开数据、合成数据的原始文件。
- `processed/`：脚本产出的标准格式数据。
- `manifests/`：数据清单，记录每个数据集的来源、版本、字段、样本数。

## `models/` — 模型节点库

```
models/
├── base/             # 原始模型
│   └── Qwen3.5-2B/
├── checkpoints/      # 训练产出
│   ├── cpt/
│   ├── sft/
│   ├── opd/
│   └── mixed/
├── teachers/         # 教师模型
├── final/            # 最终选定模型
└── registry/         # 模型注册表
    └── models.jsonl
```

每个模型都是实验图中的一个节点，可以被后续训练引用。

## `configs/` — 参数配置

```
configs/
├── data/             # 数据配比配置
├── train/            # 训练配置
│   ├── cpt/
│   ├── sft/
│   └── opd/
└── eval/             # 评测配置
```

- 配置文件中不要写死具体模型路径（除非 base 模型占位）。
- 脚本可以通过命令行参数或环境变量注入路径。

## `scripts/` — 统一调用入口

```
scripts/
├── data/             # 数据构建脚本
├── train/            # 训练脚本
├── eval/             # 评测脚本
├── analysis/         # 结果分析脚本
└── utils/            # 注册/辅助工具
```

所有实验都应通过 `scripts/` 下的脚本触发，而不是直接进入外部仓库操作。

## `runs/` — 实验运行记录

```
runs/
├── train/            # 训练日志
├── eval/             # 评测结果
├── analysis/         # 分析输出
├── train_registry.csv
└── eval_registry.csv
```

- `train/`：每次训练的运行目录，包含日志、config 备份、中间 checkpoint。
- `eval/`：每次评测的运行目录，包含结果文件、日志。
- `analysis/`：汇总分析输出。

**重要**：模型 checkpoint 不放在 `runs/`，而是放在 `models/checkpoints/`。

## 解耦原则总结

1. **数据与外部仓库解耦**：外部仓库只通过绝对路径读取 `data/` 下数据。
2. **模型与运行解耦**：模型在 `models/`，日志结果在 `runs/`。
3. **配置与脚本解耦**：配置可独立维护，脚本读取配置。
4. **外部仓库与主项目解耦**：尽量不修改 `repos/` 源码。
