# Git 提交规范

本项目使用最小化提交规范。

## 提交前检查

每次 commit 前必须运行：

```bash
git status --short
```

确认以下文件/目录**没有**出现在待提交列表中：

- `repos/`
- `.venv/`、`.venvs/`
- `data/raw/`、`data/interim/`、`data/processed/`
- `models/base/`、`models/checkpoints/`、`models/teachers/`、`models/final/`
- `runs/train/`、`runs/eval/`、`runs/analysis/`
- 大文件/模型文件：`.log`、`.pt`、`.bin`、`.safetensors`、`.parquet`

## Commit message 格式

```
<type>(<scope>): <summary>
```

## 允许的 type

| type | 用途 |
|------|------|
| `feat` | 新增项目能力，例如数据脚本、训练脚本、评测脚本 |
| `fix` | 修复错误 |
| `docs` | 只改文档 |
| `chore` | 仓库、环境、配置维护 |

## 示例

```
chore(repo): initialize project scaffold
chore(repos): record external repository commits
docs(env): document environment policy
feat(train): add CPT smoke launcher
feat(eval): add generic model evaluation script
fix(configs): correct LlamaFactory dataset path
```

## 原则

- 每次 commit 只做一个清晰主题。
- 不要把环境、数据、训练、评测混在一个 commit 里。
- 不要自动 push；需要 push 时先询问项目所有者。
