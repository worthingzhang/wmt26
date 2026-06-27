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

## repos/official_eval（官方 eval-code repo 的 fork）

| 字段 | 值 |
|------|-----|
| 本地路径 | `/home/zc/wmt26/repos/official_eval` |
| origin | `https://github.com/worthingzhang/llms-lim-res-eval-2026.git`（我们的 fork） |
| upstream | `https://github.com/TUM-NLP/llms-lim-res-eval-2026.git`（**官方 eval-code repo**） |
| data | `https://github.com/TUM-NLP/llms-limited-resources2026.git`（**官方 data repo**） |
| 当前 commit | `711a2b4fe80c11c340d75bcae2ffc313ca0e06d7`（= `upstream/main`，2026-06-14 “Update baseline results.”） |
| 安全备份 tag | `pre-align-1e6ab97b` → `1e6ab97b`（对齐前 HEAD，含旧本地 MR 补丁） |

用途：

- 官方评测后端（lm-evaluation-harness fork），生成 WMT26 Limited Resources LLM 任务预测。
- 读取模型路径并执行评测。

**Remote 命名约定（2026-06-24 修正）**：

- 修正前 `upstream` **错误指向 data repo**，官方 eval-code repo 未配 remote。
- 修正后：`origin`=fork、`upstream`=官方 eval-code、`data`=官方 data repo。
- 这样 `git fetch upstream && git merge upstream/main` 才是“跟官方 eval-code 对齐”。

**对齐记录（2026-06-24）**：

- 采纳**纯官方口径**：`git reset --hard upstream/main`，`main` 从 `1e6ab97b` → `711a2b4f`。
- 本地 MR 补丁 `1e6ab97b` **不再保留**（已被官方 `8be394d6 "Minor metric update."` 取代：MR `acc`→`exact_match` 并删 chrf；SC/GC 抽取正则放宽 `\s*`），仅由 tag `pre-align-1e6ab97b` 备份。
- 唯一本地改动：`.gitignore` 增加 `llms-limited-resources2026`（忽略 data repo 的 symlink）。
- 详见 `docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md` §0.5。

## 官方 data repo（标准答案 / 数据）

| 字段 | 值 |
|------|-----|
| 远端 | `https://github.com/TUM-NLP/llms-limited-resources2026.git` |
| 运行时路径 | `repos/official_eval/llms-limited-resources2026`（**symlink** → `data/raw/llms-limited-resources2026`） |
| 真实副本 | `/home/zc/wmt26/data/raw/llms-limited-resources2026` |
| 当前 commit | `2b712ac61cbafceb157823fa48d6531d9f4f37bd`（2026-06-19 “Upload evaluation script. Minor fixes.”） |
| 用途 | 提供 gold/dev 数据（harness 按相对路径 `llms-limited-resources2026/Sorbian/…` 读取）+ standalone `baseline_dev/evaluation.py` |

> 另存在第二个**未同步文物副本** `data/raw/official/llms-limited-resources2026`（`cc3579a`，06-17），非运行路径，未使用。
> baseline 只在**固定 data commit** 下可比；评测 `run.yaml` 须记录 data commit。

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
