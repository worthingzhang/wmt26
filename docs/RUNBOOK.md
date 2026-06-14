# 操作手册

本文档给出常用命令模板。

## 环境准备

```bash
cd /home/zc/wmt26
# 推荐使用 uv 管理环境
# uv venv
# source .venv/bin/activate
```

## 数据构建

### 构建 CPT 语料

```bash
python scripts/data/build_cpt_corpus.py \
  --input-dir data/raw/monolingual_and_parallel \
  --output-dir data/processed/cpt \
  --output-name cpt_mix_v1.jsonl \
  --manifest-path data/manifests/cpt_mix_v1.json
```

### 构建 SFT 数据

```bash
python scripts/data/build_sft_data.py \
  --input-dir data/raw/sft_sources \
  --output-dir data/processed/sft \
  --output-name sft_mix_v1.jsonl \
  --dataset-info-path data/processed/sft/dataset_info.json \
  --manifest-path data/manifests/sft_mix_v1.json
```

### 构建 OPD Prompt 池

```bash
python scripts/data/build_opd_prompts.py \
  --input-path data/processed/sft/sft_mix_v1.jsonl \
  --output-dir data/processed/opd_prompts \
  --output-name opd_prompt_mix_v1.jsonl \
  --manifest-path data/manifests/opd_prompt_mix_v1.json
```

### 检查 jsonl 文件

```bash
python scripts/data/inspect_jsonl.py \
  --input-path data/processed/cpt/cpt_mix_v1.jsonl \
  --num-samples 3 \
  --stat-field task
```

## Smoke 训练

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

### SFT from CPT checkpoint

```bash
bash scripts/train/train_sft.sh \
  --run-id sft_smoke_from_cpt_v1 \
  --input-model /home/zc/wmt26/models/checkpoints/cpt/cpt_smoke_base_v1 \
  --data-config configs/data/sft_mix_v1.yaml \
  --train-config configs/train/sft/sft_smoke.yaml \
  --output-model /home/zc/wmt26/models/checkpoints/sft/sft_smoke_from_cpt_v1 \
  --model-id sft_smoke_from_cpt_v1
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

## 评测任意模型

### 评测 base 模型

```bash
bash scripts/eval/eval_model.sh \
  --eval-id eval_base_qwen35_2b_v1 \
  --model-id base_qwen35_2b \
  --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \
  --eval-config configs/eval/official_all_tasks.yaml \
  --output-dir /home/zc/wmt26/runs/eval/eval_base_qwen35_2b_v1
```

### 评测 checkpoint

```bash
bash scripts/eval/eval_model.sh \
  --eval-id eval_cpt_smoke_base_v1 \
  --model-id cpt_smoke_base_v1 \
  --model-path /home/zc/wmt26/models/checkpoints/cpt/cpt_smoke_base_v1 \
  --eval-config configs/eval/official_all_tasks.yaml \
  --output-dir /home/zc/wmt26/runs/eval/eval_cpt_smoke_base_v1
```

## 结果汇总

```bash
python scripts/analysis/compare_models.py \
  --eval-registry runs/eval_registry.csv \
  --output-dir runs/analysis \
  --output-name comparison_v1
```

## 注册模型（手动）

如果训练脚本未完成自动注册，可手动调用：

```bash
python scripts/utils/register_model.py \
  --model-id cpt_smoke_base_v1 \
  --model-path /home/zc/wmt26/models/checkpoints/cpt/cpt_smoke_base_v1 \
  --training-type cpt \
  --input-model /home/zc/wmt26/models/base/Qwen3.5-2B \
  --data-config configs/data/cpt_mix_v1.yaml \
  --train-config configs/train/cpt/cpt_smoke.yaml \
  --notes "CPT smoke test from base"
```

## 后台运行

服务器无 SLURM，可使用 `tmux` 或 `nohup`：

```bash
# tmux
tmux new -s cpt_smoke
bash scripts/train/train_cpt.sh ...
# Ctrl+B, D detach

# nohup
nohup bash scripts/train/train_cpt.sh ... > runs/train/cpt_smoke_base_v1/nohup.out 2>&1 &
```
