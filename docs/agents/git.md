# Git workflow for agents

After completing each clear task, the agent should manage Git automatically.

## Before committing

Always run:

```bash
git status -sb
git status --short
git diff --stat
```

Do not commit if any of these are staged or about to be staged:

```text
repos/
.venv/
.venvs/
data/raw/
data/interim/
data/processed/
models/base/
models/checkpoints/
models/teachers/
models/final/
runs/train/
runs/eval/
runs/analysis/
*.log
*.pt
*.bin
*.safetensors
*.parquet
```

If these appear, stop and report the problem.

## Commit rules

Use:

```text
<type>(<scope>): <summary>
```

Allowed types:

```text
feat   new project capability
fix    bug fix
docs   documentation-only change
chore  repo, environment, config, or maintenance change
```

Examples:

```text
chore(repo): initialize project scaffold
chore(env): add mirror configuration
docs(runbook): document LlamaFactory setup
feat(train): add CPT smoke launcher
feat(eval): add model evaluation wrapper
fix(configs): correct dataset path
```

Each commit should have one clear topic. Do not mix environment setup, data scripts, training scripts, evaluation scripts, and documentation changes in one commit unless they are part of the same small task.

## Push rules

After a successful local commit, push to the current branch automatically.

Use:

```bash
git push
```

If the current branch has no upstream, use:

```bash
git push -u origin <current-branch>
```

Never use:

```bash
git push --force
git push -f
```

If push fails because of authentication, remote divergence, rejected updates, missing remote, or branch mismatch, stop and report. Do not rewrite history without explicit human approval.

## End-of-task report

At the end of each task, report:

```text
- Whether a commit was created
- Commit message
- Commit hash
- Whether push succeeded
- Current branch
- Whether the working tree is clean
```
