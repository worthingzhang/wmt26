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
- [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) — naming conventions
- [docs/EXTERNAL_REPOS.md](docs/EXTERNAL_REPOS.md) — external backend repos
- [docs/ADR.md](docs/ADR.md) — durable architecture decisions
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

- Project scaffold committed.
- External repos cloned with upstreams.
- Base model `Qwen/Qwen3.5-2B` copied to `models/base/Qwen3.5-2B`.
- Main/Eval env ready; `torch==2.6.0+cu124`, CUDA available, 8 × RTX 4090.
- LlamaFactory env ready; `torch==2.7.0+cu126`, `llamafactory-cli` 0.9.5.dev0 available.
- OPD/verl env ready; `torch==2.8.0+cu128`, `verl`/`vllm`/`sglang`/`math_verify` importable.
- `tmux` 3.2a available.
- Data/train/eval scripts are skeletons awaiting real data formats.

## Next TODOs

1. Prepare/check CPT/SFT data formats and run CPT smoke training.
2. Run SFT smoke training and optionally OPD smoke training.
3. Evaluate base model and smoke checkpoints with `scripts/eval/eval_model.sh`.
