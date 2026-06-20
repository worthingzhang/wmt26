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

## Current State (Checkpoint)

- Project scaffold committed; external repos cloned with upstreams.
- Base model `Qwen/Qwen3.5-2B` copied to `models/base/Qwen3.5-2B`.
- Three environments ready:
  - Main/Eval `.venv`: torch 2.6.0+cu124
  - LlamaFactory `.venvs/llamafactory`: torch 2.7.0+cu126, llamafactory-cli 0.9.5.dev0
  - OPD/verl `.conda/envs/verl`: torch 2.8.0+cu128
- `tmux` 3.2a available.
- Sorbian baseline evaluation completed (QA + generative).
- `repos/official_eval` patched for Sorbian MR exact_match metric, commit `1e6ab97b`.
- **CPT V1 Official Plaintext DSB4X**:
  - Processed data ready: 3,824,702 lines, ~135M tokens, 60/40 hsb/dsb.
  - Smoke (cutoff_len=1024) completed: 20/20 steps, final loss 4.086.
  - Probe4096 (cutoff_len=4096, ZeRO-3) completed: 50/50 steps, final loss 3.4468, ~24.5 s/step.
  - **Full CPT running**: tmux `cpt-v1-dsb4x-full`, step 12/1000, loss ~4.40, ~24 s/step, estimated 7–8 hours.

## Next TODOs

1. Monitor full CPT to completion (1000 steps), validate checkpoints/loss/log, update status docs.
2. Run zero-shot evaluation of `cpt_v1_official_plaintext_dsb4x_full` and compare to base model baseline.
3. Register the full CPT model in `models/registry/models.jsonl` and `runs/train_registry.csv`.
