# Session Log

## Session: 2026-06-23 / 2026-06-24（官方评测链路对齐 + 状态栏/代理排查）

### Summary

暂停 few-shot 主线，专注**官方 zero-shot 口径**。确认 `repos/official_eval` 的 remote 配错（`upstream` 错指 data repo），官方 eval-code repo `TUM-NLP/llms-lim-res-eval-2026` 未配 remote。执行完整的代码/仓库对齐：修正 remote 命名 → fetch → tag 备份 → `reset --hard` 到官方 eval-code main → 对齐 data 副本 → 标注 few-shot 为 experimental。**未运行任何评测、未生成新结果、未 push。** 另排查修好 Claude Code 状态栏（Kimi 真实 256k 窗口），确认开发服务器当前可直连 GitHub（此前超时为瞬时抖动），并定位 codex 的 Windows 反向隧道代理（`codex-wmt` → `127.0.0.1:17890` → Windows Clash `7897`）。

### Files Changed / Created

- `docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md` — 新建（调查清单 + §0.5 执行记录）。
- `docs/EXTERNAL_REPOS.md` — 重写 official_eval 段（remote 命名、`711a2b4f`、对齐记录）+ 新增官方 data repo 段。
- `reports/eval/eval_index.csv` — v1/v2 行 notes 加 `[EXPERIMENTAL]`/`[REGRESSED]`（**不改分数**）。
- `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/README.md` — 加 experimental banner。
- `configs/eval/tasks/.../fewshot_v{1,2}/EXPERIMENTAL.md` + `configs/eval/devsplits/sorbian_devsplit_fewshot_v{1,2}/EXPERIMENTAL.md` — 新建 4 个标记。
- `docs/eval/DEVSPLIT_FEWSHOT_V2_REGRESSION_REPORT.md` — 加状态 banner（v2 invalid/regressed）。
- `repos/official_eval/.gitignore` — 新增 `llms-limited-resources2026`（symlink，无斜杠）。
- 项目仓外：`~/.claude/statusline-command.sh`、记忆 `kimi-256k-context-limit.md`。

### Commands / Tests Run（关键，全部成功）

```bash
cd /home/zc/wmt26/repos/official_eval
git remote rename upstream data
git remote add upstream https://github.com/TUM-NLP/llms-lim-res-eval-2026.git
git fetch upstream && git fetch data          # upstream/main=711a2b4f, data/main=2b712ac6
git tag pre-align-1e6ab97b                     # 备份旧 HEAD（含本地 MR 补丁）
git reset --hard upstream/main                 # 1e6ab97b -> 711a2b4f
# data 副本（symlink -> data/raw/llms-limited-resources2026）
git -C llms-limited-resources2026 fetch origin
git -C llms-limited-resources2026 reset --hard origin/main   # 16fa568 -> 2b712ac6
```

### Key Findings

- 官方 `8be394d6 "Minor metric update."`：MR `acc`→`exact_match`（删 chrf，加 mean/higher_is_better）+ SC/GC 抽取正则放宽 `\s*`。本地 `1e6ab97b` 被其取代。
- harness 的 MT 用 `<deu>` 零样本，已对齐；`<de>` 回归只在自研 few-shot v2，不在 harness。
- Math-Verify 不在 harness 内；MR 用 YAML filter 正则 + `exact_match`。
- 开发服务器可直连 GitHub（curl 多次 200，~0.8s）；codex 代理是 Windows `ssh -N -T WMT-codex-tunnel` 反向隧道，按需 `git -c http.https://github.com/.proxy=http://127.0.0.1:17890 …`。

### Unresolved Issues

1. eval fork 本地 `main` 领先 GitHub `origin/main` 2 个 commit（`711a2b4f`），**未 push**。
2. 主仓文档/标注改动 + eval 仓 `.gitignore` 改动**未 commit**。
3. data repo 第二个文物副本 `data/raw/official/llms-limited-resources2026`（`cc3579a`）未同步，非运行路径。
4. 官方口径 zero-shot baseline 待重跑（SC/GC/MR 受正则/指标变更影响）；先设计结果存储结构与命名规范，再做统一入口。
5. CPT full 模型仍未注册、未评测（沿用上一 session 未决项）。

---

## Session: 2026-06-20（CPT V1 DSB4X probe4096 与 full CPT 启动）

### Summary

本次会话完成了 CPT V1 Official Plaintext DSB4X 的 probe4096 验证和 full CPT 启动。probe4096 成功证明 cutoff_len=4096 + DeepSpeed ZeRO-3 在 8× RTX 4090 上稳定可行；full CPT 第一次自动启动因 tmux 配置兼容性问题在 step 0 静默退出，修复 `.tmux.conf` 后由用户在 tmux 中手动启动，目前已稳定推进到 step 12/1000。

### Files Changed / Created

- `configs/train/cpt/cpt_v1_official_plaintext_dsb4x_full.yaml`
  - `max_steps: 1000`
  - `gradient_accumulation_steps: 4`
  - `logging_steps: 10`
  - `save_steps: 200`
  - `save_total_limit: 3`
  - 移除 `num_train_epochs` 和 `needs_manual_review` 注释
- `scripts/train/run_cpt_v1_plaintext_dsb4x_full.sh` — 移除 manual review 提示
- `docs/train/CPT_V1_OFFICIAL_PLAINTEXT_DSB4X_STATUS.md` — 新增 Probe 4096 章节、Full CPT Plan 与两次 launch 记录
- `models/cpt/cpt_v1_official_plaintext_dsb4x_full/TRAINING_RUN.md` — 新建 full CPT 运行记录
- `docs/RUNBOOK.md` — 更新里程碑、已验证训练命令、下一步
- `.claude/rules/project-rules.md` — 新增 tmux 配置兼容性 pitfall
- `CLAUDE.md` — 更新当前状态与 TODOs

### Commands / Tests Run

```bash
# probe4096 状态检查与验证
git status --short
ps -ef | grep -E "cpt_v1_official_plaintext_dsb4x_probe4096|llamafactory-cli|torchrun"
tmux ls
tail -n 80 logs/train/cpt_v1_official_plaintext_dsb4x/probe4096.log
ls -lah models/cpt/cpt_v1_official_plaintext_dsb4x_probe4096
python3 -m py_compile scripts/data/processed/build_cpt_v1_plaintext_dataset.py
bash -n scripts/train/run_cpt_v1_plaintext_dsb4x_probe4096.sh

# full CPT 启动前检查
ls -lh data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl
wc -l data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl
nvidia-smi
df -h /home/zc/wmt26
python3 -m py_compile scripts/data/processed/build_cpt_v1_plaintext_dataset.py
bash -n scripts/train/run_cpt_v1_plaintext_dsb4x_full.sh

# full CPT 启动与监控
tmux new -d -s cpt-v1-dsb4x-full "bash scripts/train/run_cpt_v1_plaintext_dsb4x_full.sh"
tmux ls
tail -n 60 logs/train/cpt_v1_official_plaintext_dsb4x/full.log
```

### Key Results

| 部分 | 状态 | 关键指标 |
|---|---|---|
| probe4096 | ✅ success | 50/50 steps, final loss 3.4468, ~24.49 s/step, ZeRO-3 active, no OOM |
| full CPT launch attempt 1 | ❌ failed | 静默退出于 step 0，无 OOM/Traceback |
| full CPT launch attempt 2 | 🔄 running | step 12/1000, loss ~4.40, ~24 s/step，tmux `cpt-v1-dsb4x-full` |

### Notes / Issues

- `.tmux.conf` 中 `allow-passthrough on` 与 tmux 3.2a 不兼容，已注释掉。
- 自动化 `tmux new -d -s ...` 在同样配置下两次都在 step 0 静默退出；用户在修复 tmux 后手动创建的 attached session 正常推进。
- full CPT 预计 7–8 小时完成。

### Unresolved Issues

1. **full CPT 尚未完成**：当前运行中，需持续监控至 1000 steps。
2. **full CPT 完成后需评测**：使用 `scripts/eval/eval_model.sh` 对最终模型做 zero-shot 评测。
3. **训练产出需注册**：`cpt_v1_official_plaintext_dsb4x_full` 需登记到 `models/registry/models.jsonl` 和 `runs/train_registry.csv`。

---

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

## Session: 2026-06-15（官方_eval metric 修复与完整生成式 baseline）

### Summary

本次会话定位并修复了 Sorbian 生成式 baseline 在 `repos/official_eval` 中的聚合错误，成功跑完了完整 QA 与完整生成式 baseline，并更新了相关文档与注册表。

### Files Changed / Created

- `docs/agents/git.md` — 更新 agent Git 工作流规则（commit/push 规则、报告要求）。
- `docs/ENV_STATUS.md` — 多次更新：环境总检查、verl 修复、baseline smoke、完整 baseline（含生成式修复后成功）。
- `docs/RESULTS.md` — 记录 smoke、完整 QA、完整生成式结果，以及修复记录。
- `docs/EXTERNAL_REPOS.md` — 更新 official_eval commit hash 与修改说明。
- `docs/RUNBOOK.md` — 更新里程碑、已验证评测命令、下一步。
- `docs/SESSION_LOG.md` — 本记录。
- `docs/ADR.md` — 新增/更新 durable decisions。
- `.claude/rules/project-rules.md` — 更新规则与 pitfalls。
- `CLAUDE.md` — 更新 compact index。
- `scripts/eval/eval_base_smoke.sh` — 新增 base QA smoke 脚本。
- `scripts/eval/eval_base_full.sh` — 新增完整 Sorbian baseline 脚本（QA + 生成式）。
- `runs/eval_registry.csv` — 登记 smoke、full QA、full generative 三次评测。
- `repos/official_eval/lm_eval/tasks/wmt26-lrl/sorbian/mr/hsbmr.yaml` — `acc` → `exact_match`。
- `repos/official_eval/lm_eval/tasks/wmt26-lrl/sorbian/mr/dsbmr.yaml` — `acc` → `exact_match`。

### Commands / Tests Run

```bash
# 验证 metric scalar
cd /home/zc/wmt26
source .venv/bin/activate
python - <<'PY'
import importlib
u = importlib.import_module('lm_eval.tasks.wmt26-lrl.utils')
from lm_eval.api.metrics import exact_match_fn
print(exact_match_fn(references=["42"], predictions=["42"]))
print(u.chrf_pp_corpus([("Hallo", "Hallo"), ("Welt", "Welt")]))
PY

# Sorbian QA smoke
bash scripts/eval/eval_base_smoke.sh

# 完整 Sorbian baseline（QA + 生成式）
bash scripts/eval/eval_base_full.sh

# 生成式 smoke（修复后）
cd /home/zc/wmt26/data/raw
CUDA_VISIBLE_DEVICES=0 NCCL_P2P_DISABLE=1 NCCL_IB_DISABLE=1 \
python -m lm_eval run \
  --model hf \
  --model_args "pretrained=/home/zc/wmt26/models/base/Qwen3.5-2B,trust_remote_code=True,dtype=bfloat16,enable_thinking=False" \
  --tasks sorbian_dev --apply_chat_template --limit 5 --batch_size 1 --device cuda:0 \
  --output_path /home/zc/wmt26/runs/eval/eval_base_qwen35_2b_gen_fix_smoke --log_samples

# 完整生成式 baseline（修复后，batch_size=8，后台运行）
CUDA_VISIBLE_DEVICES=0 NCCL_P2P_DISABLE=1 NCCL_IB_DISABLE=1 \
python -m lm_eval run \
  --model hf \
  --model_args "pretrained=/home/zc/wmt26/models/base/Qwen3.5-2B,trust_remote_code=True,dtype=bfloat16,enable_thinking=False" \
  --tasks sorbian_dev --apply_chat_template --batch_size 8 --device cuda:0 \
  --output_path /home/zc/wmt26/runs/eval/eval_base_qwen35_2b_full/gen_fixed --log_samples
```

### Key Results

| 部分 | 状态 | 关键指标 |
|---|---|---|
| QA smoke (hsbqa, limit=5) | ✅ success | acc=0.85 |
| Full QA (hsbqa + dsbqa) | ✅ success | hsbqa=0.5159, dsbqa=0.4682 |
| Generative smoke (sorbian_dev, limit=5) | ✅ success | MT/SC/GC/MR 均正常聚合 |
| Full generative (sorbian_dev) | ✅ success | MT chrf++ avg=22.04, bleu avg=3.99; SC=0.084; GC=0.004; MR=0.042 |

### Commits

- 主项目：`feat(eval): add full Sorbian baseline script and record partial results` (`30c0bbf`)
- 主项目：`docs(eval): record official_eval metric fix and baseline results` (`a91335d`)
- `repos/official_eval`：`fix(metrics): ensure Sorbian MR metrics return scalar` (`1e6ab97b`)

### Unresolved Issues

1. **Git push 网络不稳定**：最近一次 commit `a91335d` 尚未 push 到 origin（先前多次 push 因 HTTP2/GnuTLS 错误失败）。
2. **数据/训练脚本仍为骨架**：`scripts/data/build_*.py` 和 `scripts/train/train_*.sh` 需要真实数据格式确认后补全。
3. **OPD/verl 依赖冲突**：numpy 版本在部分包之间不完全一致，当前导入正常，smoke 训练时需观察运行时是否报错。
4. **多 GPU 评测未启用**：`parallelize=True` 与 Qwen3.5-2B 自定义 attention 不兼容，当前 baseline 均跑在单卡 `cuda:0` 上。

---

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
