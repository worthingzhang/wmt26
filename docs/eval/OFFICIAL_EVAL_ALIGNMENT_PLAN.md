# WMT26 官方评测链路对齐计划（OFFICIAL_EVAL_ALIGNMENT_PLAN）

> 目标：把 WMT26 官方评测链路对齐并固化为项目主线，暂停 few-shot 工程。
> 状态：**仓库/代码对齐已执行（2026-06-24）；本轮未运行任何评测、未生成新结果、未 push。** 详见 §0.5 执行记录。
> 生成日期：2026-06-24（调查）；对齐执行：2026-06-24。
> 约束：评测入口脚本与重跑 baseline **仍待后续**（用户将先设计结果存储结构与命名规范，再统一设计入口）。

---

## 0. TL;DR

1. **eval-code repo 与 data repo 是两个仓库，当前 remote 配错了**：本地 `repos/official_eval` 的 `upstream` 指向的是 **data repo**（`TUM-NLP/llms-limited-resources2026`），而真正的官方 **eval-code repo**（`TUM-NLP/llms-lim-res-eval-2026`）**根本没配成 remote**。
2. 官方 eval-code main（缓存快照 `711a2b4f`）比我们 fork 基点 `3e2bd75c` **领先 2 个 commit**：
   - `8be394d6 "Minor metric update."` —— 实质代码改动（MR 指标 → `exact_match`，且 SC/GC 抽取正则放宽 `\s*`）；
   - `711a2b4f "Update baseline results."` —— 只改 `README.md` 的 baseline 数字。
3. 我们唯一的本地补丁 `1e6ab97b "ensure Sorbian MR metrics return scalar"` **基本被官方 `8be394d6` 取代**：两者都把 MR 的 `acc` 换成 `exact_match`，但我们**多保留了 chrf**、**没加显式 aggregation/higher_is_better**、**没动 ukrmr**、且**缺少 SC/GC 正则放宽**。
4. harness 里的 **MT 任务已经和官方一致**（用 `<deu>`、零样本）；之前 `<de>` 的回归只存在于**自研 few-shot profile**（`configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v2/`），不在 harness 内。
5. **网络（已复核）**：开发服务器**当前可直连 GitHub**（curl 多次 200、`git ls-remote`/`fetch` 正常，~0.8s，偶发延迟尖刺）。之前的 130s 超时是这台不稳定机器的**瞬时抖动**，非持续封锁。本轮已直连 fetch 确认官方 commit（见 §0.5）。建议：fetch 时带 `timeout`/重试；**备用方案** = Windows 端 `ssh -N -T WMT-codex-tunnel` 反向隧道（服务器 `127.0.0.1:17890` → Windows Clash `127.0.0.1:7897`），需要时用 URL 限定让 git 只对 github 走代理：`git -c http.https://github.com/.proxy=http://127.0.0.1:17890 fetch …`。

---

## 0.5 执行记录（2026-06-24，已执行；未跑评测 / 未 push）

本轮按本计划执行了 `repos/official_eval` 的**代码与仓库对齐**，**未运行任何评测、未生成新结果、未 push**。

| 项 | 结果 |
|---|---|
| eval-code `upstream/main`（直连 fetch 确认） | **`711a2b4f`** "Update baseline results."（2026-06-14） |
| data repo main（确认并对齐到） | **`2b712ac6`** "Upload evaluation script. Minor fixes."（2026-06-19） |
| remote 命名 | 旧 `upstream`（错指 data repo）→ 改名 `data`；新增 `upstream` → 官方 eval-code `TUM-NLP/llms-lim-res-eval-2026` |
| 安全备份 tag | `pre-align-1e6ab97b` → `1e6ab97b`（已创建并校验） |
| eval-code 对齐 | `git reset --hard upstream/main`：`main` 由 `1e6ab97b` → `711a2b4f`；本地 MR 补丁已移出 main（仅 tag 保留） |
| data 副本 | `repos/official_eval/llms-limited-resources2026` 实为 **symlink → `data/raw/llms-limited-resources2026`**；已 fetch 并 `reset --hard` 到 `2b712ac6` |
| `.gitignore` | eval repo 加入 `llms-limited-resources2026`（**无斜杠**，因是 symlink）以消除 untracked 噪音；这是唯一一处有意的本地改动 |
| **决定** | **`official_eval` 采纳纯官方口径（§2.4 选项 A）：本地 `1e6ab97b` 不保留，仅 tag 备份；MR 不再保留 chrf。** |

> `reset --hard` 后 `main` 相对 fork 的 `origin/main`（`3e2bd75c`）ahead 2，**未 push**。
> 另存在第二个未同步的 data 文物副本 `data/raw/official/llms-limited-resources2026`（`cc3579a`），非运行路径，本轮未处理。
> 待后续（用户先定结果存储/命名）：统一官方评测入口脚本、重跑并固化 `base_qwen35_2b` 官方口径 zero-shot baseline（§2.6 / §3）。

---

## 1. 调查事实（一手证据）

### 1.1 仓库拓扑与路径

| 角色 | 远端 | 本地路径 | 说明 |
|---|---|---|---|
| **eval-code repo（官方）** | `github.com/TUM-NLP/llms-lim-res-eval-2026` | —（未克隆为独立目录） | lm-eval-harness fork，**生成预测**用 |
| eval-code fork（我们的） | `github.com/worthingzhang/llms-lim-res-eval-2026` | `repos/official_eval` | `origin` |
| **data repo（官方）** | `github.com/TUM-NLP/llms-limited-resources2026` | 见下 | 数据 + 标准答案 + standalone `evaluation.py` |

> ⚠️ 用户提到的本地路径 `repos/llms-lim-res-eval-2026` **不存在**；真实的 eval-code 工作副本是 `repos/official_eval`。

data repo 在本地有 **3 处副本，且不同步**：

| 路径 | commit | 日期 | 备注 |
|---|---|---|---|
| `data/raw/llms-limited-resources2026` | `16fa568` | 06-09 | 旧 |
| `data/raw/official/llms-limited-resources2026` | `cc3579a` | 06-17 | 含 “Release the baseline outputs and results” |
| `repos/official_eval/llms-limited-resources2026`（untracked） | `16fa568` | 06-09 | **harness 运行时按相对路径读取的就是它**，但目前是旧版 |

### 1.2 `repos/official_eval` 的 git 现状

```
origin    = https://github.com/worthingzhang/llms-lim-res-eval-2026.git   ✓ 正确（我们的 fork）
upstream  = https://github.com/TUM-NLP/llms-limited-resources2026.git     ✗ 配错（这是 data repo）
branch    = main
HEAD      = 1e6ab97b  fix(metrics): ensure Sorbian MR metrics return scalar
tracking  = origin/main（ahead 1，未 push）
worktree  = 干净，仅 1 个 untracked：llms-limited-resources2026/（运行所需，应 gitignore）
```

因为 `upstream` 指向 data repo，`git fetch upstream` 会把 **data repo 的历史**拉进 eval-code 仓库的 refs：当前 `upstream/main = 2b712ac6 "Upload evaluation script. Minor fixes."`（06-19，data repo 的 commit），这在概念上是错的（即便暂时无害）。

### 1.3 commit 关系图

```
        3e2bd75c  "compute acc metric for maths reasoning tasks"   ← 我们 fork 的基点 = origin/main
        /        \
我们:  1e6ab97b    8be394d6  "Minor metric update."        ← 官方 +1
(MR scalar 补丁)        \
                        711a2b4f  "Update baseline results." ← 官方 +2（= 官方 eval-code main，缓存）
```

- 官方 eval-code main 相对我们 fork 基点 **领先 2**：`8be394d6`、`711a2b4f`。
- 我们 HEAD 相对 fork 基点 **领先 1**：`1e6ab97b`（与官方分叉）。

### 1.4 五个对比点（逐项取证）

**① SC/GC 抽取正则** —— `lm_eval/tasks/wmt26-lrl/utils.py::process_sc_results`（SC 与 GC **共用**此函数，无单独 GC 函数）

| | 正则 |
|---|---|
| 官方 `8be394d6` | `r'<wrong>\s*(.*?)\s*</wrong>'` / `r'<corrected>\s*(.*?)\s*</corrected>'`（放宽空白） |
| 我们 `1e6ab97b`（=fork 基点） | `r"<wrong> (.*?) </wrong>"` / `r"<corrected> (.*?) </corrected>"`（**严格单空格**） |

→ **我们缺这个放宽**。模型若输出 `<wrong>X</wrong>`（无空格）或多空格，我们会漏抽 → SC/GC 偏低。**应采纳官方版**。

**② MR 指标 / exact_match / Math-Verify** —— `mr/dsbmr.yaml`、`mr/hsbmr.yaml`（官方还含 `ukrmr.yaml`）

| | `metric_list` |
|---|---|
| 原始 `3e2bd75c` | `[chrf, acc]`（`acc` 对 generate_until 无效 → 我们项目规则明令禁止） |
| 官方 `8be394d6` | `[exact_match (aggregation: mean, higher_is_better: true)]`（**删 chrf**） |
| 我们 `1e6ab97b` | `[chrf, exact_match]`（**留 chrf**，无显式 aggregation，未动 ukrmr） |

→ **harness 里没有 Math-Verify**：MR 的 `<answer>…</answer>` 由 YAML `filter_list` 的正则抽取，再用 `exact_match` 打分。Math-Verify（若有）在 **data repo 的 standalone `baseline_dev/evaluation.py`**，与 harness 解耦。官方 MR 口径 = `exact_match` only。

**③ Sorbian MT YAML 标签** —— `lm_eval/tasks/wmt26-lrl/sorbian/mt/*.yaml`

- 官方 & 我们 HEAD **完全一致**（这 2 个官方 commit 没动 MT）：`dsb-deu`/`hsb-deu` 用 `<deu> … </deu>`、零样本，正则 `<deu>\s*([\s\S]*?)\s*(?:</deu>|$)`。
- → **harness 的 MT 已对齐官方**。`<de>` 回归**只在自研 few-shot profile**（`configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v2/`）里，与 harness 无关（见 `DEVSPLIT_FEWSHOT_V2_REGRESSION_REPORT.md`）。

**④ baseline 命令** —— 官方 `README.md`（`711a2b4f`）

```bash
# (a) 生成式任务（MT/SC/GC/MR），零样本，关思考，套 chat template
python3 -m lm_eval --model hf \
    --model_args pretrained=Qwen/Qwen3.5-2B,enable_thinking=False --apply_chat_template \
    --tasks ukrainian_dev sorbian_dev \
    --output_path baseline_output --log_samples

# (b) QA / MMLU，单独跑，不套 chat template、不设 thinking
python3 -m lm_eval --model hf \
    --model_args pretrained=Qwen/Qwen3.5-2B \
    --tasks ukrqa ukrmmlu hsbqa dsbqa \
    --output_path baseline_output --log_samples
```

- 数据：在 eval repo 根目录 `git clone https://github.com/TUM-NLP/llms-limited-resources2026`；YAML 用相对路径 `llms-limited-resources2026/Sorbian/…`。
- `sorbian_dev` group = `[hsbsc, dsbsc, hsbgc, dsbgc, hsbmr, dsbmr, deu-hsb, hsb-deu, deu-dsb, dsb-deu, dsb-hsb, hsb-dsb]`（SC×2/GC×2/MR×2/MT×6）。QA（hsbqa/dsbqa）单独跑。
- 我们的 `scripts/eval/eval_base_full.sh` **已匹配官方跑法**：Run1=QA `hsbqa dsbqa`（不套 chat template）；Run2=`sorbian_dev` + `--apply_chat_template` + `enable_thinking=False`。
- `711a2b4f` 仅刷新 README 里 **Ukrainian** baseline 数字（`ukrmr` 从 `chrf 2.79` → `exact_match 0.125`），印证官方 MR 口径=exact_match。**Sorbian** 官方 baseline 数字在 **data repo 的 `baseline_dev/`**（`cc3579a` release），不在 eval README。

**⑤ 本地 MR 补丁 vs 官方** —— 见 1.3 + ①②：我们的 `1e6ab97b` 与官方 `8be394d6` **部分重复（都转 exact_match）+ 部分分叉（多留 chrf、缺 SC 正则放宽、未动 ukrmr、无显式 aggregation）**。结论：**被官方取代**，对齐时应丢弃我们的版本、改采官方 `711a2b4f`。

---

## 2. 对齐清单（待确认，不执行）

### 2.1 当前 remotes 是否配置错误 —— ❌ 是

- `repos/official_eval` 的 `upstream` 错指向 **data repo**；官方 **eval-code repo 未配为 remote**。
- 后果：`git fetch upstream` 拉的是 data repo 历史；想拿官方 eval-code 更新只能靠手动 `git fetch <URL>`（上一轮就是这么拿到 `711a2b4f` 进 FETCH_HEAD 的）。

### 2.2 推荐 remote 命名

| remote | 目标 URL | 含义 |
|---|---|---|
| `origin` | `worthingzhang/llms-lim-res-eval-2026`（不变） | 我们的 fork |
| `upstream` | `TUM-NLP/llms-lim-res-eval-2026` ← **新增/改指** | 官方 **eval-code** repo（fork 的上游，约定俗成） |
| `data`（原 `upstream` 改名） | `TUM-NLP/llms-limited-resources2026` | 官方 **data** repo |

> 建议操作（**待确认**）：`git remote rename upstream data` → `git remote add upstream https://github.com/TUM-NLP/llms-lim-res-eval-2026.git`。这样 `git fetch upstream && git merge upstream/main` 才是“跟官方 eval-code 对齐”。

### 2.3 应该引入的官方 commits

| commit | 标题 | 内容 | 是否引入 |
|---|---|---|---|
| `8be394d6` | Minor metric update. | MR `acc`→`exact_match`（删 chrf，加 mean/higher_is_better）+ SC/GC 正则放宽 `\s*` | ✅ **引入**（核心） |
| `711a2b4f` | Update baseline results. | 仅 `README.md` baseline 数字 | ⭕ 可选（文档；fast-forward 时自然带入） |

> 引入方式（**待确认**）：remote 修好后，`git fetch upstream`，将 `main` 对齐到 `upstream/main`（`711a2b4f`）。因为我们 HEAD（`1e6ab97b`）与官方分叉，需 **rebase 我们的本地 delta 到 `711a2b4f` 之上**，或直接 `reset --hard upstream/main` 丢弃我们的 delta（见 2.4 决定保留与否）。

### 2.4 应该保留的本地补丁

- `repos/official_eval` 内**唯一**本地补丁是 `1e6ab97b`，且已被官方 `8be394d6` 覆盖 → **默认不保留**（直接采官方版，顺带白拿 SC/GC 正则放宽 + ukrmr 修正）。
- **唯一需要你拍板的分叉点**：官方把 MR 的 **chrf 删了**，只留 exact_match；我们之前留了 chrf 当辅助诊断。
  - **选项 A（✅ 已采纳，纯官方口径）：丢 chrf，与官方完全一致 → 排行榜/可比性最干净。本地 `1e6ab97b` 不保留，仅 tag `pre-align-1e6ab97b` 备份。**
  - 选项 B：在官方基础上**另起一个明确标注的本地 commit** 把 chrf 加回 MR 作“附加诊断列”，但心里清楚官方只认 exact_match。
- `repos/official_eval` 之外的本地资产（`scripts/eval/*`、`configs/eval/*`、`reports/eval/*`）都在 **wmt26 主仓**，不受 eval-fork 对齐影响，**全部保留**。

### 2.5 应该废弃 / 标记 experimental 的自研 few-shot 内容

| 资产 | 处置 |
|---|---|
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v2/` | 标 **experimental**；其 MT→deu 与 SC/GC 已证实回归（见回归报告），**不得**当官方 baseline |
| `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v1/` | 标 **experimental**（表现较好，但本质是“恰好 priming”，非官方口径） |
| `configs/eval/devsplits/sorbian_devsplit_fewshot_v{1,2}/` | experimental 配套数据 |
| `scripts/eval/eval_wmt26_sorbian.sh`、`scripts/eval/generate_8gpu_devsplit_v2.py` | few-shot 实验工具链，归入 experimental 轨道 |
| `reports/eval/eval_index.csv` 里的 v2 行 | 给 MT“→德语”、SC、GC 标 `regressed/invalid`，避免被后续当真实基线 |

> 不删除，只**隔离 + 标注**，保留实验可追溯性。官方主线与 few-shot 实验线分开。

### 2.6 对齐后需要重跑的 baseline

固化对象：**`base_qwen35_2b` 官方口径 zero-shot Sorbian dev baseline**。

- 受官方 2 个 commit 影响而**必须重跑**的任务：
  - **SC**（`hsbsc`,`dsbsc`）、**GC**（`hsbgc`,`dsbgc`）：正则放宽 → 抽取率变 → `exact_match_wrong/corrected` 会变。
  - **MR**（`hsbmr`,`dsbmr`）：指标集变为 exact_match-only（exact_match 数值本身不变，因抽取 filter 未变，但报告口径变）。
- **不受影响、可复用**：MT×6、QA×2（这 2 个官方 commit 没动它们；我们现有 `reports/eval/base_qwen35_2b__zero_shot` 的 MT/QA 数值即官方口径）。
- 实操建议（**待确认**）：对齐 + 数据副本 pin 到固定 commit 后，用 `eval_base_full.sh` **整组重跑 `sorbian_dev` + QA**（最干净、一次成图），覆盖/新增一份 `reports/eval/base_qwen35_2b__official_zeroshot/`，并在 `eval_index.csv` 标 `official`。
- ⚠️ 当前 `reports/eval/base_qwen35_2b__zero_shot`（2026-06-19 生成）是在**未对齐**的 patched repo 上跑的：MR 含 chrf、SC 用严格正则 → **SC/GC/MR 三类非官方口径**，需重跑后替换。

### 2.7 风险点与回滚方式

| 风险 | 说明 | 缓解 / 回滚 |
|---|---|---|
| ~~官方 hash 可能已过期~~ ✅ 已复核 | 本机已直连 fetch 确认：eval-code main=`711a2b4f`、data main=`2b712ac6`（§0.5） | 已记入 `docs/EXTERNAL_REPOS.md`；实验室集群跑前可再 `git fetch` 复核 |
| ~~data 副本版本漂移~~ ✅ 已对齐 | 运行副本是 symlink→`data/raw/llms-limited-resources2026`，已对齐 `2b712ac6`(06-19) 并 gitignore | baseline 只在**固定 data commit** 下可比，run.yaml 须记 data commit；另存 `data/raw/official/…`(`cc3579a`) 文物副本未用 |
| ~~丢弃本地补丁~~ ✅ 已备份+执行 | `reset --hard upstream/main` 已把 `1e6ab97b` 移出 main | tag `pre-align-1e6ab97b`→`1e6ab97b` 已建，可随时 `git checkout`/`cherry-pick` 恢复；**未 push** |
| **flag 不一致导致数值漂移** | `enable_thinking` / `--apply_chat_template` / num_fewshot 与官方不符即不可比 | 严格照官方 README（生成式：thinking=False+chat template+0-shot；QA：裸跑），固化进 `eval_base_full.sh` 并写入 run.yaml |
| **few-shot 实验被误当官方基线** | v1/v2 分数被后续引用 | 见 2.5：eval_index 标注 + 目录标 experimental |
| **未 push 的本地领先** | `main` ahead origin 1（`1e6ab97b`） | 对齐方案定了再决定是否 push / 是否丢弃；不要在没结论前 push（项目规则：不自动 push） |

---

## 3. 统一的“官方口径”评测入口（目标 #4 草案，待确认）

- **入口脚本**：沿用 `scripts/eval/eval_base_full.sh` 的两段式（QA 裸跑 / 生成式 `sorbian_dev`+chat template+thinking=False），把它**泛化成任意 checkpoint 可传 `MODEL_PATH`** 的官方口径入口（命名如 `eval_official_sorbian.sh`），与 few-shot 的 `eval_wmt26_sorbian.sh` **彻底分线**。
- **前置条件**：2.2 remote 修好、2.3 官方 commit 引入、2.6 data 副本 pin 到固定 commit。
- **产物规范**：每个 checkpoint 出一份 `reports/eval/<model_tag>__official_zeroshot/`（RESULTS.md + scores.csv + run.yaml），run.yaml 记录 eval-code commit、data commit、flags，保证可比与可复现。

---

## 4. 建议的执行顺序（**全部待你确认后再单独执行**）

1. 在实验室集群复核官方 eval-code / data repo 最新 commit，更新本文 hash。
2. 修 remote 命名（2.2）。
3. `git tag pre-align-1e6ab97b`，再把 `main` 对齐到 `upstream/main`（2.3 / 2.4）。
4. pin 并升级根目录 data 副本，`.gitignore` 之，记录 data commit（2.7）。
5. 重跑 `base_qwen35_2b` 官方口径 zero-shot（2.6），固化 baseline。
6. 标注/隔离 few-shot 实验资产（2.5）。
7. 落地统一官方入口脚本（§3）。
8. 更新 `docs/EXTERNAL_REPOS.md`、`CLAUDE.md`、`eval_index.csv`。

> 到此为止仅为清单。**等你确认后，我再逐项执行**，不提前 merge / cherry-pick / reset / push。
