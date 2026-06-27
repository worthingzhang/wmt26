# 操作手册

项目脚本会自动加载 `configs/env/mirrors.env`；手动调试时才需要 `source` 它。

## 服务器分工

| 服务器 | 地址 | 项目路径 | GPU | 主要用途 |
|---|---|---|---|---|
| 开发服务器（本机） | `zc@10.249.46.1:8888` | `/home/zc/wmt26` | 8 × RTX 4090 24 GB | 代码开发、文档、git、轻量评测 |
| 实验室训练集群 | `zc@10.249.45.139` | `/data1/zc/wmt26` | 8 × RTX 4090 48 GB | 长时间 CPT/SFT/OPD 训练 |

同步方式：代码走 `git push/pull`，数据/模型/环境走 `rsync`。

## 当前里程碑（Checkpoint 2026-06-24：官方评测链路对齐）

暂停 few-shot 主线，转向**官方 zero-shot 口径**。详见 `docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md`。

### 已完成（本次）

- `repos/official_eval` remote 命名修正：`origin`=fork、`upstream`=官方 eval-code（`TUM-NLP/llms-lim-res-eval-2026`）、`data`=官方 data repo。
- eval-code 对齐到官方 `upstream/main = 711a2b4f`（`reset --hard`，丢弃本地 `1e6ab97b`，tag `pre-align-1e6ab97b` 备份）。
- data 副本（symlink → `data/raw/llms-limited-resources2026`）对齐到官方 `2b712ac6`。
- few-shot v1/v2 标记 **experimental**（不删、不修）；v2 的 MT→deu/SC/GC 确认 invalid/regressed。
- 开发服务器确认可直连 GitHub；codex 代理为 Windows 反向隧道（备用）。

### 已验证命令（本次，全部成功）

```bash
cd /home/zc/wmt26/repos/official_eval
git remote rename upstream data
git remote add upstream https://github.com/TUM-NLP/llms-lim-res-eval-2026.git
git fetch upstream && git fetch data
git tag pre-align-1e6ab97b
git reset --hard upstream/main                               # -> 711a2b4f
git -C llms-limited-resources2026 fetch origin
git -C llms-limited-resources2026 reset --hard origin/main   # -> 2b712ac6
# 备用代理（仅 github，不影响 pip/hf）：先在 Windows 跑 `ssh -N -T WMT-codex-tunnel`
git -c http.https://github.com/.proxy=http://127.0.0.1:17890 fetch upstream
```

### 下一步（本主线）

1. 设计结果存储结构与命名规范（`reports/eval` 布局），再统一设计官方评测入口（**暂不**创建 `eval_official_sorbian.sh`、**暂不**改 `eval_base_full.sh`）。
2. 用官方口径重跑并固化 `base_qwen35_2b` zero-shot baseline（SC/GC/MR 受正则/指标变更影响需重跑；MT/QA 可复用）。
3. 评测 `run.yaml` 须记录 eval-code commit (`711a2b4f`) 与 data commit (`2b712ac6`)。
4. vLLM 作为下一阶段单独处理（暂不安装/配置/测试）。

> 以下为上一里程碑（CPT）记录。

## 当前里程碑（Checkpoint 2026-06-21）

### 已完成

- 项目骨架、外部仓库、三个训练/评测环境、base model、镜像配置、tmux 均已就绪。
- **服务器分工已确定**：老服务器做开发/评测，新 lab cluster（48GB GPU）做训练。
- **Sorbian baseline 评测已完成**：
  - QA smoke（hsbqa limit=5）：acc=0.85。
  - 完整 QA（hsbqa + dsbqa）：hsbqa=0.5159，dsbqa=0.4682。
  - 完整生成式 baseline（sorbian_dev，batch_size=8）：MT chrf++=22.04，bleu=3.99；SC=0.084；GC=0.004；MR=0.042。
- `repos/official_eval` 已做最小修复：Sorbian MR `acc` → `exact_match`，commit `1e6ab97b`。
- **CPT V1 Official Plaintext DSB4X 数据处理完成**：
  - processed file: `data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl`
  - line count: 3,824,702
  - estimated tokens: ~135M
  - hsb/dsb ratio: 59.98% / 40.02%
- **CPT smoke 完成**：`models/cpt/cpt_v1_official_plaintext_dsb4x_smoke`，20/20 steps，final loss 4.086。
- **CPT probe4096 完成**：`models/cpt/cpt_v1_official_plaintext_dsb4x_probe4096`，50/50 steps，cutoff_len=4096，DeepSpeed ZeRO-3，final loss 3.4468，~24.5 s/step。
- **Full CPT 已完成（lab cluster）**：`models/cpt/cpt_v1_official_plaintext_dsb4x_full/checkpoint-1000/`，1000/1000 steps，final loss 2.148，runtime 3:48:05。

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
source /data/wyt/miniconda3/etc/profile.d/conda.sh
conda activate /home/zc/wmt26/.conda/envs/verl
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -c "import verl, vllm, sglang, math_verify; print('imports ok')"
```

### 已验证训练命令

```bash
# CPT smoke
bash scripts/train/run_cpt_v1_plaintext_dsb4x_smoke.sh

# CPT probe4096（cutoff_len=4096，ZeRO-3，50 steps）
bash scripts/train/run_cpt_v1_plaintext_dsb4x_probe4096.sh

# Full CPT（cutoff_len=4096，ZeRO-3，1000 steps）— 推荐在 tmux 中运行
tmux new -s cpt-v1-dsb4x-full
cd /home/zc/wmt26
bash scripts/train/run_cpt_v1_plaintext_dsb4x_full.sh
# detach: Ctrl-b d
```

### 已验证评测命令

```bash
# Sorbian QA smoke
cd /home/zc/wmt26/data/raw
CUDA_VISIBLE_DEVICES=0 NCCL_P2P_DISABLE=1 NCCL_IB_DISABLE=1 \
python -m lm_eval run \
  --model hf \
  --model_args "pretrained=/home/zc/wmt26/models/base/Qwen3.5-2B,trust_remote_code=True,dtype=bfloat16" \
  --tasks hsbqa --limit 5 --batch_size 1 --device cuda:0 \
  --output_path /home/zc/wmt26/runs/eval/eval_base_qwen35_2b_smoke --log_samples

# 完整 Sorbian 生成式 baseline
cd /home/zc/wmt26/data/raw
CUDA_VISIBLE_DEVICES=0 NCCL_P2P_DISABLE=1 NCCL_IB_DISABLE=1 \
python -m lm_eval run \
  --model hf \
  --model_args "pretrained=/home/zc/wmt26/models/base/Qwen3.5-2B,trust_remote_code=True,dtype=bfloat16,enable_thinking=False" \
  --tasks sorbian_dev --apply_chat_template --batch_size 8 --device cuda:0 \
  --output_path /home/zc/wmt26/runs/eval/eval_base_qwen35_2b_full/gen_fixed --log_samples
```

### 未完成的下一步

1. **注册 full CPT 模型**：将 `cpt_v1_official_plaintext_dsb4x_full` 登记到 `models/registry/models.jsonl` 和 `runs/train_registry.csv`。
2. **Full CPT 完成后评测**：使用 `scripts/eval/eval_model.sh` 对 `models/cpt/cpt_v1_official_plaintext_dsb4x_full` 做 zero-shot 评测，与 base model baseline 对比。
3. **更新训练状态文档**：更新 `docs/train/CPT_V1_OFFICIAL_PLAINTEXT_DSB4X_STATUS.md` 为完成状态。
4. **推进后续实验节点**：基于 CPT 结果启动 SFT / OPD smoke。

本文档给出常用命令模板。

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
