# Agent Guide

This is the first file every coding agent should read in this repository. It is the shared entry point for Codex, Claude Code, and future agents. Claude-specific files still exist, but project-wide rules start here.

## Must Read Before Work

- [docs/agents/git.md](docs/agents/git.md) - Git workflow, commit rules, and staging restrictions.
- [docs/RUNBOOK.md](docs/RUNBOOK.md) - Current environment, commands, and verified workflows.
- [docs/SESSION_LOG.md](docs/SESSION_LOG.md) - Recent work, unresolved issues, and context from prior sessions.
- [docs/ADR.md](docs/ADR.md) - Durable architecture and safety decisions.
- [CLAUDE.md](CLAUDE.md) - Compact project index and current-state summary.
- [.claude/rules/project-rules.md](.claude/rules/project-rules.md) - Practical project rules and common pitfalls.

## Git Rules

- Always check `git status --short` before editing.
- Do not use `git add .`.
- Stage only the files intentionally changed for the task.
- Do not stage generated caches, large outputs, local symlinks, model files, or raw/interim/processed data.
- Do not auto-push. Report what was committed and wait for explicit push approval.
- Follow [docs/agents/git.md](docs/agents/git.md) for commit format and end-of-task reporting.

## Project Safety Rules

- Do not modify official eval task YAMLs under `repos/official_eval/lm_eval/tasks/` unless explicitly requested.
- Prefer project-local overlay configs under `configs/eval/` for evaluation changes.
- Keep raw data under `data/raw/` unchanged.
- Do not commit model checkpoints, caches, large run outputs, or symlinks to local data.
- Keep data, models, runs, and external repos separated as described in [docs/ADR.md](docs/ADR.md).
- Use absolute paths when invoking external, evaluation, or training backends.
- Treat CPT, SFT, and OPD as parallel training operators, not a fixed pipeline.

## Eval Workflow Rules

- Save raw evaluation outputs under `runs/eval/...`; this directory is ignored and should not be committed.
- Save small, human-readable, Git-trackable result summaries under `reports/eval/<model_tag>__<eval_setting>/`.
- Use `scripts/eval/aggregate_eval_results.py` or `scripts/eval/finalize_8gpu_eval_run.sh` to create `RESULTS.md`, `scores.csv`, `run.yaml`, and `reports/eval/eval_index.csv`.
- Record commands, manifests, source paths, and result paths for reproducibility.
- Register eval runs in `runs/eval_registry.csv` when a workflow produces a meaningful result.
- For few-shot or devsplit tasks, verify that fixed shots are removed from eval data and that logs do not show few-shot fallback/leakage warnings.
- Run lm-eval from the expected backend directory when required by the workflow, usually `/home/zc/wmt26/repos/official_eval`.

## Completion Report

When finishing a task, report:

- Files changed.
- Commands run.
- Validation results.
- Final `git status --short`.
- Any skipped validation and the reason.

If the task involves a commit, also report the commit message, commit hash, branch, and whether the working tree is clean.
