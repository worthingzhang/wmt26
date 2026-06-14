# 外部仓库说明

本文档记录本项目使用的外部训练/评测后端仓库。

这些仓库统一放在 `repos/` 下，作为外部引擎使用，不提交到本项目的 git。

## repos/thunlp_opd

| 字段 | 值 |
|------|-----|
| 本地路径 | `/home/zc/wmt26/repos/thunlp_opd` |
| origin | `https://github.com/worthingzhang/OPD.git` |
| upstream | `https://github.com/thunlp/OPD.git` |
| 当前 commit | `1fd6cca846126af90d82ef122e8af261f59d2d37` |

用途：

- 内含 `LlamaFactory`，用于 CPT/SFT 训练。
- 内含 `verl` 及 OPD/GRPO 相关代码，用于 OPD 训练。

## repos/official_eval

| 字段 | 值 |
|------|-----|
| 本地路径 | `/home/zc/wmt26/repos/official_eval` |
| origin | `https://github.com/worthingzhang/llms-lim-res-eval-2026.git` |
| upstream | `https://github.com/TUM-NLP/llms-limited-resources2026.git` |
| 当前 commit | `3e2bd75cc6b1c153b7a9418a6bbb118c71f543e5` |

用途：

- 官方评测后端。
- 负责读取模型路径并执行 WMT26 Limited Resources LLM 任务评测。

## 常用维护命令

```bash
# 查看所有 remote
cd /home/zc/wmt26/repos/thunlp_opd && git remote -v
cd /home/zc/wmt26/repos/official_eval && git remote -v

# 从 upstream 拉取更新
cd /home/zc/wmt26/repos/thunlp_opd && git fetch upstream
cd /home/zc/wmt26/repos/official_eval && git fetch upstream
```

## 注意事项

- 不要把训练数据或模型 checkpoint 复制进这两个仓库。
- 优先通过主项目的 `scripts/` 和 `configs/` 传参，避免直接修改外部仓库源码。
- 如需修改外部仓库源码，请先记录原因和改动，并在本文档备注。
