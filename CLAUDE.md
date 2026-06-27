# CLAUDE.md — WMT26 Limited Resources LLM

Compact index for Claude Code sessions.

## Project Goal

Build a **model experiment DAG** for WMT26 Limited Resources LLM (Qwen3.5-2B).
CPT, SFT, and OPD are parallel operators; any model can feed any later training step.

## Quick Links

- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) — directory layout
- [docs/EXPERIMENT_PLAN.md](docs/EXPERIMENT_PLAN.md) — model experiment DAG design
- [docs/DATA_PLAN.md](docs/DATA_PLAN.md) — data formats and restrictions
- [docs/RUNBOOK.md](docs/RUNBOOK.md) — commands and current milestone
- [docs/ENV_STATUS.md](docs/ENV_STATUS.md) — environment and baseline status
- [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) — naming conventions
- [docs/EXTERNAL_REPOS.md](docs/EXTERNAL_REPOS.md) — external backend repos
- [docs/ADR.md](docs/ADR.md) — durable architecture decisions
- [docs/eval/EVAL_RESULT_STANDARD.md](docs/eval/EVAL_RESULT_STANDARD.md) — tracked eval summary layout
- [docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md](docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md) — official eval alignment (current mainline)
- [docs/eval/OFFICIAL_ZEROSHOT_RUNBOOK.md](docs/eval/OFFICIAL_ZEROSHOT_RUNBOOK.md) — official zero-shot eval script usage
- [docs/SESSION_LOG.md](docs/SESSION_LOG.md) — session history
- [docs/agents/git.md](docs/agents/git.md) — commit conventions
- [.claude/rules/project-rules.md](.claude/rules/project-rules.md) — rules and pitfalls

## Directory Structure

```
/home/zc/wmt26/
├── repos/          # external backends (ignored by git)
│   ├── official_eval/   # lm-eval-harness fork
│   └── thunlp_opd/      # LlamaFactory + verl/OPD fork
├── data/           # data assets (raw/interim/processed ignored)
│   ├── manifests/       # tracked
│   └── README.md
├── models/         # model node library
│   ├── base/Qwen3.5-2B  # ignored
│   ├── checkpoints/     # ignored
│   └── registry/        # tracked
├── configs/        # tracked
│   ├── env/mirrors.env  # mirror/timeout config
│   ├── data/
│   ├── train/{cpt,sft,opd}/
│   └── eval/
├── scripts/        # tracked entry points
│   ├── setup/
│   ├── data/
│   ├── train/
│   ├── eval/
│   ├── analysis/
│   └── utils/
├── runs/           # logs/results (ignored)
│   ├── train_registry.csv
│   └── eval_registry.csv
└── submissions/    # final outputs
```

## Servers

| Server | Address | Project root | GPUs | Role | Status |
|---|---|---|---|---|---|
| Development / original | `zc@10.249.46.1` (port 8888) | `/home/zc/wmt26` | 8 × RTX 4090 24 GB | 开发、轻量评测 | ⚠️ 不稳定，今日多次系统重启 |
| Lab cluster / training | `zc@10.249.45.139` | `/data1/zc/wmt26` | 8 × RTX 4090 48 GB | 长时间训练、大显存任务 | ✅ 已 setup，CPT v1 full 完成 |

Both servers share the same git repo but do **not** auto-sync files. Move code via `git push/pull` and move data/models via `rsync`.

## Environments

| Environment | Path | Python | Purpose |
|-------------|------|--------|---------|
| Main/Eval | `.venv` | 3.12 | Project tooling, pandas, official_eval/lm_eval |
| CPT/SFT | `.venvs/llamafactory` | 3.11 | LlamaFactory from `repos/thunlp_opd/LlamaFactory` |
| OPD/verl | `.conda/envs/verl` | 3.12 | OPD / verl / vLLM / sglang via conda prefix |

All project scripts auto-load `configs/env/mirrors.env`.

## Key Commands

### Setup

```bash
# Main/Eval env (already done)
uv venv --python 3.12 .venv
uv pip install pandas pyyaml tqdm rich jsonlines
uv pip install -e repos/official_eval[hf]

# LlamaFactory env (next TODO)
bash scripts/setup/setup_llamafactory_env.sh
```

### Verify

```bash
source .venv/bin/activate
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -c "import transformers; print(transformers.__version__)"
python -c "import lm_eval; print(lm_eval.__version__)"
python -m lm_eval --help

source .venvs/llamafactory/bin/activate
llamafactory-cli version
```

### Data

```bash
python scripts/data/build_cpt_corpus.py --input-dir data/raw/... --output-dir data/processed/cpt ...
python scripts/data/build_sft_data.py --input-dir data/raw/... --output-dir data/processed/sft ...
python scripts/data/build_opd_prompts.py --input-path data/processed/sft/... --output-dir data/processed/opd_prompts ...
```

### Training

```bash
bash scripts/train/train_cpt.sh --run-id ... --input-model ... --data-config ... --train-config ... --output-model ... --model-id ...
bash scripts/train/train_sft.sh --run-id ... --input-model ... --data-config ... --train-config ... --output-model ... --model-id ...
bash scripts/train/train_opd.sh --run-id ... --student-model ... --teacher-model ... --prompt-config ... --train-config ... --output-model ... --model-id ...
```

### Eval

```bash
bash scripts/eval/eval_model.sh --eval-id ... --model-id ... --model-path ... --eval-config ... --output-dir ...
```

## Critical Rules

- CPT/SFT/OPD are **parallel operators**, not a fixed pipeline.
- Don't put data or checkpoints into `repos/`.
- Don't modify `repos/` source code unless unavoidable; pass args via `configs/` and `scripts/`.
- Register every model/train/eval in the registry CSVs/JSONL.
- Don't auto-push; ask first.
- Don't install verl/vLLM/sglang unless asked.
- **Eval mainline = official zero-shot.** All checkpoints (base / CPT / SFT / OPD) must first run `official_zeroshot` under aligned `repos/official_eval` + data repo.
- **few-shot v1/v2 are experimental**, not baseline; v2 MT→deu / SC / GC are invalid/regressed.
- `runs/` holds raw evidence (`results_*.json`, `samples_*.jsonl`, logs, shards); `reports/` holds human-readable aggregates (`RESULTS.md`, `scores.csv`, `run.yaml`).
- Every formal eval result must have a `run.yaml` with `model_tag`, `backend`, `eval_code_commit`, `data_commit`, and `official` flag.
- Do not use timestamps as `reports/` directory names; timestamps belong in `runs/<run_id>` only.

## Current State (Checkpoint)

- Project scaffold committed; external repos cloned with upstreams.
- Base model `Qwen/Qwen3.5-2B` copied to `models/base/Qwen3.5-2B`.
- Three environments ready on **both** servers:
  - Main/Eval `.venv`: torch 2.6.0+cu124
  - LlamaFactory `.venvs/llamafactory`: torch 2.7.0+cu126, llamafactory-cli 0.9.5.dev0
  - OPD/verl `.conda/envs/verl`: torch 2.8.0+cu128
- `tmux` 3.2a available.
- Sorbian baseline evaluation completed (QA + generative).
- **Eval mainline = official zero-shot.** `repos/official_eval` aligned to official **eval-code** `upstream/main = 711a2b4f` (pure official 口径). Remotes: `origin`=fork, `upstream`=eval-code (`TUM-NLP/llms-lim-res-eval-2026`), `data`=data repo (`TUM-NLP/llms-limited-resources2026`). Local MR patch `1e6ab97b` dropped (superseded by official `8be394d6`), backed up as tag `pre-align-1e6ab97b`. data repo @ `2b712ac6` (symlink → `data/raw/llms-limited-resources2026`).
- few-shot devsplit **v1/v2 marked experimental** (not official baseline); v2 MT→deu/SC/GC invalid/regressed. See `docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md` + `docs/eval/DEVSPLIT_FEWSHOT_V2_REGRESSION_REPORT.md`.
- Dev-server GitHub is directly reachable (flaky; codex Windows reverse tunnel `127.0.0.1:17890` as fallback).
- **CPT V1 Official Plaintext DSB4X**:
  - Processed data ready: 3,824,702 lines, ~135M tokens, 60/40 hsb/dsb.
  - Smoke (cutoff_len=1024) completed: 20/20 steps, final loss 4.086.
  - Probe4096 (cutoff_len=4096, ZeRO-3) completed: 50/50 steps, final loss 3.4468, ~24.5 s/step.
  - **Full CPT completed on lab cluster**: 1000/1000 steps, final loss 2.148, runtime 3:48:05, checkpoint saved at `models/cpt/cpt_v1_official_plaintext_dsb4x_full/checkpoint-1000/`.

## Next TODOs

1. ~~Design `reports/eval` result-storage structure + naming~~ ✅ Done (see updated `docs/eval/EVAL_RESULT_STANDARD.md` and `reports/eval/eval_index.csv`). Build a unified **official zero-shot** eval entry only after explicit approval (still do NOT create `eval_official_sorbian.sh` or modify `eval_base_full.sh` yet).
2. Re-run + freeze `base_qwen35_2b` official zero-shot baseline (SC/GC/MR changed by official regex/metric; MT/QA reusable); record eval-code `711a2b4f` + data `2b712ac6` in `run.yaml`.
3. Register full CPT model `cpt_v1_official_plaintext_dsb4x_full` in registries; then eval it under the official entry vs base.
4. vLLM is a separate later phase (don't install/configure/test yet).
