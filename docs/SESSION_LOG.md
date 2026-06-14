# Session Log

## Session: 2026-06-14 / 2026-06-15

### Summary

本次会话完成了 WMT26 Limited Resources LLM 项目的初始骨架搭建、外部仓库接入、主项目/评测环境配置，以及镜像配置和 LlamaFactory 安装脚本的准备。LlamaFactory 环境本身的安装因网络波动尚未执行。

### Files Changed / Created

- `.gitignore`
- `README.md`
- `AGENTS.md`
- `configs/` — 数据、训练、评测配置
- `configs/env/mirrors.env` — 新增镜像/超时统一配置
- `scripts/` — 数据构建、训练、评测、分析、注册脚本
- `scripts/setup/setup_llamafactory_env.sh` — 新增 LlamaFactory 环境安装脚本
- `docs/` — PROJECT_STRUCTURE、DATA_PLAN、EXPERIMENT_PLAN、RUNBOOK、RESULTS、EXPERIMENTS、EXTERNAL_REPOS、agents/git.md
- `models/registry/models.jsonl`
- `runs/train_registry.csv`、`runs/eval_registry.csv`
- `.claude/statusline-command.sh`、`.claude/settings.json`（Claude Code 状态栏配置）

### Commands / Tests Run

```bash
# 项目初始化
git init
git branch -m main

# 外部仓库
git clone https://github.com/worthingzhang/OPD.git repos/thunlp_opd
git clone https://github.com/worthingzhang/llms-lim-res-eval-2026.git repos/official_eval
cd repos/thunlp_opd && git remote add upstream https://github.com/thunlp/OPD.git
cd repos/official_eval && git remote add upstream https://github.com/TUM-NLP/llms-limited-resources2026.git

# 主项目环境
uv venv --python 3.12 .venv
uv pip install pip setuptools wheel pandas pyyaml tqdm rich jsonlines
uv pip install -e repos/official_eval[hf]

# PyTorch CUDA 修复
uv pip uninstall torch triton
uv pip install torch --index-url https://download.pytorch.org/whl/cu124

# 验证
python -c "import pandas, yaml, tqdm, rich, jsonlines; print('project deps ok')"
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -c "import transformers; print(transformers.__version__)"
python -c "import lm_eval; print(lm_eval.__version__)"
python -m lm_eval --help
```

### Unresolved Issues

1. **LlamaFactory 环境未安装完成**：`scripts/setup/setup_llamafactory_env.sh` 已创建，但尚未执行。之前尝试直接安装 `torch==2.6.0+cu124` 时因网络超时/连接重置失败。
2. **OPD/verl 环境未安装**：按当前计划延后。
3. **数据处理和训练流程仍为骨架**：`scripts/data/build_*.py` 和 `scripts/train/train_*.sh` 需要真实数据格式确认后补全。
4. **官方评测任务名称未确认**：`configs/eval/official_all_tasks.yaml` 中的 task 名称仍是 TODO。

## Session: 2026-06-15（续）

### Summary

本次会话完成了 base model 整理、LlamaFactory CPT/SFT 环境安装、OPD/verl conda prefix 环境安装，以及 tmux 确认。三个训练/评测环境（main/eval、LlamaFactory、OPD/verl）均已就绪，base model 已就位。

### Files Changed / Created

- `.gitignore` — 新增 `.conda/`
- `configs/env/mirrors.env` — 改用显式 `export`
- `docs/RUNBOOK.md` — 更新里程碑、环境说明
- `docs/SESSION_LOG.md` — 本记录
- `docs/ENV_STATUS.md` — 新增环境状态总览
- `docs/MODEL_STATUS.md` — 新增 base model 状态
- `models/registry/models.jsonl` — 更新 base 模型登记
- `scripts/setup/setup_llamafactory_env.sh` — 重写，强制 CUDA 检查
- `scripts/setup/setup_opd_verl_conda_env.sh` — 新建 OPD/verl conda 安装脚本

### Commands / Tests Run

```bash
# base model 整理
cp -aL /home/zc/.cache/huggingface/hub/models--Qwen--Qwen3.5-2B/snapshots/15852e8c16360a2fea060d615a32b45270f8a8fc/. /home/zc/wmt26/models/base/Qwen3.5-2B/

# LlamaFactory 环境
bash scripts/setup/setup_llamafactory_env.sh

# OPD/verl conda 环境
bash scripts/setup/setup_opd_verl_conda_env.sh

# tmux
tmux -V
```

### Environment Verification

| 环境 | Python | torch | CUDA | 关键包 |
|------|--------|-------|------|--------|
| `.venv` | 3.12 | 2.6.0+cu124 | True | lm_eval ✅ |
| `.venvs/llamafactory` | 3.11.14 | 2.7.0+cu126 | True | llamafactory-cli 0.9.5.dev0 ✅ |
| `.conda/envs/verl` | 3.12.13 | 2.8.0+cu128 | True | verl 0.7.0.dev, vllm 0.11.0, sglang 0.5.2, math_verify ✅ |

### Unresolved Issues

1. **数据处理和训练流程仍为骨架**：`scripts/data/build_*.py` 和 `scripts/train/train_*.sh` 需要真实数据格式确认后补全。
2. **官方评测任务名称未确认**：`configs/eval/official_all_tasks.yaml` 中的 task 名称仍是 TODO。
3. **OPD/verl 存在依赖冲突**：numpy 版本在 opencv、cupy-cuda12x、outlines、numba、mistral-common 之间不完全一致，当前导入正常，但 smoke 训练时需观察是否引发运行时错误。
