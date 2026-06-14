# WMT26 Limited Resources LLM — 模型实验图项目

本仓库用于 WMT26 Limited Resources LLM 任务的模型实验框架，核心研究对象为 **Qwen3.5-2B**。

## 核心思想：CPT / SFT / OPD 是并列训练算子

本项目不是一个固定的 `Base → CPT → SFT → OPD` 流水线，而是一个**模型实验图（Model Experiment DAG）**。

三类训练方法被实现为三个并列算子：

- `train_cpt(input_model, data_config, train_config) → output_model`
- `train_sft(input_model, data_config, train_config) → output_model`
- `train_opd(student_model, teacher_model, prompt_config, train_config) → output_model`

任何已有模型都可以作为后续训练的输入，包括原始 base、CPT/SFT/OPD 产出的 checkpoint，以及其他实验中生成的模型。

典型训练路径示例：

- Base vs CPT
- Base vs SFT
- CPT → SFT
- SFT → OPD
- CPT → OPD
- CPT → SFT → OPD
- 不同数据配比的 CPT/SFT/OPD 实验

## 目录结构

```
/home/zc/wmt26/
├── README.md                    # 本文件
├── docs/                        # 项目文档
├── repos/                       # 外部仓库（official_eval, thunlp_opd）
├── data/                        # 数据资产
├── models/                      # 模型节点库
│   ├── base/Qwen3.5-2B          # 原始模型
│   ├── checkpoints/             # 训练产出
│   └── registry/models.jsonl    # 模型注册表
├── configs/                     # 参数配置
├── scripts/                     # 统一调用入口
│   ├── data/                    # 数据构建脚本
│   ├── train/                   # 训练脚本
│   ├── eval/                    # 评测脚本
│   ├── analysis/                # 结果分析
│   └── utils/                   # 注册工具
├── runs/                        # 实验运行记录
│   ├── train/                   # 训练日志
│   ├── eval/                    # 评测结果
│   ├── analysis/                # 分析输出
│   ├── train_registry.csv       # 训练注册表
│   └── eval_registry.csv        # 评测注册表
└── submissions/                 # 最终提交产物
```

## 如何准备数据

### 构建 CPT 语料

```bash
python scripts/data/build_cpt_corpus.py \
  --input-dir data/raw/monolingual_and_parallel \
  --output-dir data/processed/cpt \
  --manifest-path data/manifests/cpt_v1.json
```

### 构建 SFT 数据

```bash
python scripts/data/build_sft_data.py \
  --input-dir data/raw/sft_sources \
  --output-dir data/processed/sft \
  --manifest-path data/manifests/sft_v1.json
```

### 构建 OPD prompt 池

```bash
python scripts/data/build_opd_prompts.py \
  --input-path data/processed/sft/sft_mix_v1.jsonl \
  --output-dir data/processed/opd_prompts \
  --manifest-path data/manifests/opd_prompts_v1.json
```

## 如何运行 smoke 训练

### CPT smoke

```bash
bash scripts/train/train_cpt.sh \
  --run-id cpt_smoke_base_v1 \
  --input-model /home/zc/wmt26/models/base/Qwen3.5-2B \
  --data-config configs/data/cpt_mix_v1.yaml \
  --train-config configs/train/cpt/cpt_smoke.yaml \
  --output-model /home/zc/wmt26/models/checkpoints/cpt/cpt_smoke_base_v1 \
  --model-id cpt_smoke_base_v1
```

### SFT smoke

```bash
bash scripts/train/train_sft.sh \
  --run-id sft_smoke_from_base_v1 \
  --input-model /home/zc/wmt26/models/base/Qwen3.5-2B \
  --data-config configs/data/sft_mix_v1.yaml \
  --train-config configs/train/sft/sft_smoke.yaml \
  --output-model /home/zc/wmt26/models/checkpoints/sft/sft_smoke_from_base_v1 \
  --model-id sft_smoke_from_base_v1
```

### OPD smoke

```bash
bash scripts/train/train_opd.sh \
  --run-id opd_smoke_sft_mt_teacher_v1 \
  --student-model /home/zc/wmt26/models/checkpoints/sft/sft_smoke_from_base_v1 \
  --teacher-model /home/zc/wmt26/models/teachers/mt_teacher_v1 \
  --prompt-config configs/data/opd_prompt_mix_v1.yaml \
  --train-config configs/train/opd/opd_smoke.env \
  --output-model /home/zc/wmt26/models/checkpoints/opd/opd_smoke_sft_mt_teacher_v1 \
  --model-id opd_smoke_sft_mt_teacher_v1
```

## 如何评测任意模型

```bash
bash scripts/eval/eval_model.sh \
  --eval-id eval_base_qwen35_2b_v1 \
  --model-id base_qwen35_2b \
  --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \
  --eval-config configs/eval/official_all_tasks.yaml \
  --output-dir /home/zc/wmt26/runs/eval/eval_base_qwen35_2b_v1
```

## 如何查看结果

- 训练日志：`runs/train/<run_id>/`
- 评测结果：`runs/eval/<eval_id>/`
- 汇总分析：`runs/analysis/`
- 注册表：
  - 模型：`models/registry/models.jsonl`
  - 训练：`runs/train_registry.csv`
  - 评测：`runs/eval_registry.csv`

## 设计原则

1. **并列算子**：CPT/SFT/OPD 不是固定顺序，任意模型均可作为输入。
2. **数据解耦**：数据放在 `data/`，外部仓库只通过绝对路径读取。
3. **模型与运行解耦**：checkpoint 放在 `models/`，日志和结果放在 `runs/`。
4. **全程可追溯**：每个模型、每次训练、每次评测都写入注册表。

## 更多文档

- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)：目录详细说明
- [docs/DATA_PLAN.md](docs/DATA_PLAN.md)：数据规划
- [docs/EXPERIMENT_PLAN.md](docs/EXPERIMENT_PLAN.md)：实验路径设计
- [docs/RUNBOOK.md](docs/RUNBOOK.md)：常用命令模板
- [docs/RESULTS.md](docs/RESULTS.md)：实验结果记录
- [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md)：实验命名规范
