# 操作手册

本文档给出常用命令模板。

## Main/Eval Environment

主项目和官方评测共用同一个 Python 环境：

```
/home/zc/wmt26/.venv
```

Python 版本：**3.12**

### 创建环境

```bash
cd /home/zc/wmt26
uv venv --python 3.12 .venv
```

### 激活环境

```bash
source .venv/bin/activate
```

### 检查主项目依赖

```bash
python -c "import pandas, yaml, tqdm, rich, jsonlines; print('project deps ok')"
```

### 检查 torch / transformers / CUDA

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -c "import transformers; print(transformers.__version__)"
```

### 检查 official_eval

official_eval 通过本地 `repos/official_eval/` 以 editable 方式安装，包名为 `lm_eval`：

```bash
python -c "import lm_eval; print(lm_eval.__version__)"
python -m lm_eval --help
```

### 安装方式说明

- 主项目轻量依赖：`uv pip install pandas pyyaml tqdm rich jsonlines ...`
- official_eval：`uv pip install -e repos/official_eval[hf]`
- 不安装：LlamaFactory、verl、vLLM、sglang。

### 当前环境状态

- NVIDIA Driver: 535.183.01
- CUDA Version: 12.2
- torch: `2.6.0+cu124`
- `torch.cuda.is_available()`: `True`
- 检测到 GPU: 8 × RTX 4090

### 常见问题：torch CUDA 版本不匹配

如果 `torch.cuda.is_available()` 返回 `False` 并提示 `The NVIDIA driver on your system is too old`，说明 PyTorch 的 CUDA 版本高于驱动支持。例如 uv 默认可能安装 `torch==2.12.0+cu130`。

解决：卸载当前 torch/triton，换 CUDA 12.4 版本：

```bash
source .venv/bin/activate
uv pip uninstall torch triton
uv pip install torch --index-url https://download.pytorch.org/whl/cu124
```

验证：

```bash
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
```

## 环境准备（速查）

```bash
cd /home/zc/wmt26
source .venv/bin/activate
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
