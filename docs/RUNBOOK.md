# 操作手册

项目脚本会自动加载 `configs/env/mirrors.env`；手动调试时才需要 `source` 它。

## 当前里程碑（Checkpoint 2026-06-15）

### 已完成

- 项目骨架提交到 git：`configs/`、`scripts/`、`docs/`、`models/registry/`、`data/manifests/`。
- 外部仓库已 clone 并配置 upstream：
  - `repos/thunlp_opd`（origin: worthingzhang/OPD，upstream: thunlp/OPD）
  - `repos/official_eval`（origin: worthingzhang/llms-lim-res-eval-2026，upstream: TUM-NLP/llms-limited-resources2026）
- 主项目/评测环境 `.venv`（Python 3.12）已创建并可用：
  - `pandas`, `pyyaml`, `tqdm`, `rich`, `jsonlines` ✅
  - `official_eval` 以 editable 安装，`lm_eval` CLI 可用 ✅
  - `torch==2.6.0+cu124`，CUDA 可用，8 × RTX 4090 识别 ✅
- LlamaFactory 环境 `.venvs/llamafactory`（Python 3.11）已安装并可用：
  - `torch==2.7.0+cu126`，CUDA 可用 ✅
  - `llamafactory-cli` 0.9.5.dev0 可用 ✅
- OPD/verl/vLLM/sglang 环境 `.conda/envs/verl`（conda prefix，Python 3.12）已安装并可用：
  - `torch==2.8.0+cu128`，CUDA 可用 ✅
  - `verl` 0.7.0.dev、`vllm` 0.11.0、`sglang` 0.5.2、`math_verify` 可 import ✅
- Base 模型 `Qwen/Qwen3.5-2B` 已整理到标准路径 `/home/zc/wmt26/models/base/Qwen3.5-2B`。
- 镜像配置已集中管理：`configs/env/mirrors.env`，所有项目脚本自动加载。
- `tmux` 3.2a 已安装，可用于后台长时间任务。

### 已验证命令

```bash
# 主项目环境
cd /home/zc/wmt26
source .venv/bin/activate
python -c "import pandas, yaml, tqdm, rich, jsonlines; print('project deps ok')"
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -c "import transformers; print(transformers.__version__)"
python -c "import lm_eval; print(lm_eval.__version__)"
python -m lm_eval --help

# LlamaFactory 环境
source .venvs/llamafactory/bin/activate
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
llamafactory-cli version

# OPD/verl 环境
conda activate /home/zc/wmt26/.conda/envs/verl
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -c "import verl, vllm, sglang, math_verify; print('imports ok')"
```

### 未完成的下一步

1. 准备/检查 CPT/SFT 数据格式，跑通 CPT smoke training。
2. 跑通 SFT smoke training 和 OPD smoke training（可选，按实验计划）。
3. 用 `scripts/eval/eval_model.sh` 评测 base model 和 smoke checkpoints。

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

## LlamaFactory Environment (CPT/SFT)

CPT/SFT 使用独立的 Python 3.11 环境，位于 `.venvs/llamafactory`：

```bash
cd /home/zc/wmt26
bash scripts/setup/setup_llamafactory_env.sh
```

脚本会自动加载 `configs/env/mirrors.env`、创建环境、单独安装 `torch==2.7.0+cu126`、安装 LlamaFactory，并强制检查 CUDA 可用性。如果 CUDA 检查失败，脚本会退出并报错，不会静默通过。

手动调试时临时加载镜像配置：

```bash
source configs/env/mirrors.env
```

激活环境后验证：

```bash
source .venvs/llamafactory/bin/activate
llamafactory-cli version
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
