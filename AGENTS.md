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

- **Current eval mainline = official zero-shot.** Use `repos/official_eval` official tasks (`sorbian_dev` group + QA) with `enable_thinking=False`, `--apply_chat_template`, zero samples.
- **few-shot v1/v2 are experimental.** They must not be reported as official baseline. v2 MT→deu / SC / GC are known invalid/regressed.
- **Every new checkpoint (base / CPT / SFT / OPD) must first run `official_zeroshot`.** Other settings (few-shot, backend_compare, smoke) go into `reports/eval_experimental/`.
- Save raw evaluation outputs under `runs/eval_official/` or `runs/eval_experimental/`; these directories are ignored and should not be committed.
- Save small, human-readable, Git-trackable result summaries under `reports/eval_official/<model_tag>/official_zeroshot/` or `reports/eval_experimental/<category>/<model_tag>/<eval_setting>/`.
- Use `scripts/eval/aggregate_eval_results.py` or `scripts/eval/finalize_8gpu_eval_run.sh` to create `RESULTS.md`, `scores.csv`, `run.yaml`, and update `reports/eval/eval_index.csv`.
- Every formal evaluation must write a `run.yaml` containing at least: `model_tag`, `model_path`, `checkpoint_type`, `eval_setting`, `shot_setting`, `backend`, `backend_role`, `official`, `eval_code_commit`, `data_commit`, `tasks_qa`, `tasks_gen`, `batch_size`, `gpu_setting`, `command`, `source_run_dir`, `generated_at`, `status`, `notes`.
- Do not create a formal evaluation result that lacks `model_tag`, `backend`, `eval_code_commit`, or `data_commit`.
- Do not place smoke, debug, or few-shot results into `reports/eval_official/`.
- Do not use a timestamp as the main directory name under `reports/`; timestamps belong in `runs/<run_id>` only.
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
