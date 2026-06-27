# Devsplit Few-shot v2 回归分析报告

> ⚠️ **状态更新（2026-06-24）：项目主线已转为 official zero-shot 口径**（见 `OFFICIAL_EVAL_ALIGNMENT_PLAN.md`）。v1/v2 few-shot 已标记为 **experimental**；v2 的 MT→deu、SC、GC 确认 **invalid/regressed**。本报告作为根因取证**保留**，**不**作为 baseline；**暂不修复 v2**。

> 调查对象：`base_qwen35_2b` 在 `wmt26_sorbian_devsplit_fewshot_v2` 上的 8GPU 评测
> （run: `runs/eval/Qwen3.5-2B/devsplit_fewshot_v2_8gpu/20260621_161029`）
> 对比基线：`devsplit_fewshot_v1`（run `..._v1_8gpu/20260618_162149`）与 base 模型 zero-shot。
> 状态：**仅调查 + 取证，未做任何修改**（等你看完结论后再改）。
> 生成日期：2026-06-23

---

## 0. TL;DR

v1 → v2 这次改动把 **MT 索布语→德语（dsb-deu / hsb-deu）、SC、GC** 打崩了。经过对**实际生成结果**（samples_*.jsonl）的逐条取证，确认是**两个互相独立、各自 100% 证据闭环**的根因：

| 受损任务 | 现象 | 根因（已证实） |
|---|---|---|
| **MT dsb-deu / hsb-deu** | BLEU 6~8 → ≈0.02，chrF++ 28~34 → ≈1.8 | **标签不一致**：v2 把 prompt 指令和抽取正则从 `<deu>` 改成 `<de>`，但 few-shot 示范的目标格式函数 `utils.target_deu()` 仍然输出 `<deu>`。模型照抄示范输出 `<deu>`，正则只认 `<de>`，抽取结果全是 `[invalid]`。 |
| **SC (dsbsc/hsbsc)、GC (dsbgc)** | exact_match_corrected 0.21~0.39 → ≈0.001~0.005 | **few-shot 示范翻转了模型行为**：v1 是 1-shot，dsbsc/hsbsc/dsbgc 的那一条恰好是 CORRECT（无错）示范，模型大量输出 `CORRECT`；v2 改成 2-shot=`[CORRECT, ERROR]`（ERROR 在最后一条），模型**0% 再输出 CORRECT**，全部去“硬找一个错”，于是 50% 的无错句子全判错。 |

两个根因都不是模型变差，而是**评测/prompt 配置 bug**。base 模型本身没动。

---

## 1. 这次到底改了什么（v1 → v2 的全部 diff）

v2 是一个**全新 profile**（commit `80c733a feat(eval): add stratified devsplit few-shot v2 profile`，配套 `scripts/eval/generate_8gpu_devsplit_v2.py`），不是在 v1 上原地改。相对 v1 的实质变化：

### 1.1 few-shot 数量（num_fewshot）

| 任务 | v1 | v2 |
|---|---:|---:|
| QA | 1 | **3** |
| SC | 1 | **2** |
| GC | 1 | **2** |
| MR | 1 | **2** |
| MT（全部 6 向） | 5 | 5（不变） |

### 1.2 MT prompt / 抽取正则（关键）

四个含德语的方向，把 `<deu>…</deu>` 改成 `<de>…</de>`：

- `deu-dsb` / `deu-hsb`（德→索）：只改了 prompt 里**源句**的包裹标签 `<deu>{{de}}</deu>` → `<de>{{de}}</de>`。**输出端**仍抽 `<dsb>`/`<hsb>` —— 不受影响。
- `dsb-deu` / `hsb-deu`（索→德）：prompt 指令 `Put it in this format <deu>…</deu>` → `<de>…</de>`，**且抽取正则** `<deu>\s*(...)` → `<de>\s*(...)`。

**但是** few-shot 示范的答案格式函数没改：
```python
# configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v2/utils.py  (v1、v2 完全相同)
def target_deu(doc):
    return f"<deu> {doc['de']} </deu>"   # ← 仍然是 <deu>
```
`dsb-deu.yaml` / `hsb-deu.yaml` 里 `fewshot_config.doc_to_target: !function utils.target_deu`，所以 5 条示范全部以 `<deu>…</deu>` 结尾。

> 即：v2 把“指令 + 抽取”改成了 `<de>`，却漏改了“示范”里的 `<deu>` → 三处不一致。

### 1.3 SC prompt 措辞（仅 SC，GC 未改）

```
v1: "...contains at most one misspelled word ... <wrong> misspelled word </wrong> <corrected> correct spelling </corrected> ..."
v2: "...contains at most one grammatically incorrect word ... <wrong> incorrect word </wrong> <corrected> correct form </corrected> ..."
```
GC 的 `doc_to_text` **完全没动**（diff 里只有 num_fewshot / 路径 / version 变化）。这点很重要：见 §5。

### 1.4 数据重生成（stratified）

v2 的 `eval/` 与 `shots/` JSONL 重新生成。**但无错/有错比例没变**（见 §3），所以数据分布不是根因。

### 1.5 其它

所有 task 名 `_fs1_v1` → `_fsN_v2`，version `1.0` → `2.0`，shots 目录指向 `..._v2/shots`。group.yaml 任务顺序也调整了（无影响）。

---

## 2. 评测结果对照（zero-shot / v1 / v2）

### 2.1 MT — BLEU / chrF++（`remove_tags`）

| 方向 | zero-shot | v1 (fs5) | v2 (fs5) | 判定 |
|---|---|---|---|---|
| deu-dsb | 1.18 / 11.06 | 1.77 / 15.49 | 1.68 / 16.04 | 正常 |
| deu-hsb | 1.11 / 13.68 | 2.01 / 19.04 | 2.09 / 19.81 | 正常 |
| **dsb-deu** | 4.84 / 23.50 | 5.99 / 28.89 | **0.020 / 1.84** | **崩** |
| **hsb-deu** | 6.37 / 26.59 | 8.27 / 33.67 | **0.018 / 1.71** | **崩** |
| dsb-hsb | 5.44 / 29.67 | 7.52 / 36.89 | 7.72 / 37.64 | 正常 |
| hsb-dsb | 4.99 / 27.76 | 6.28 / 35.09 | 6.65 / 35.93 | 正常 |

> 只有“→德语”两个方向崩了；其余四向（→索布语、索↔索）正常。这正好对应 §1.2：只有这两向的**抽取标签**被改成了 `<de>`。

### 2.2 SC — exact_match_corrected / exact_match_wrong

| 任务 | zero-shot | v1 (fs1) | v2 (fs2) | 判定 |
|---|---|---|---|---|
| **dsbsc** | 0.074 / 0.070 | 0.376 / 0.372 | **0.0015 / 0.055** | **崩** |
| **hsbsc** | 0.095 / 0.096 | 0.390 / 0.389 | **0.0050 / 0.088** | **崩** |

### 2.3 GC — exact_match_corrected / exact_match_wrong

| 任务 | zero-shot | v1 (fs1) | v2 (fs2) | 判定 |
|---|---|---|---|---|
| **dsbgc** | 0.004 / 0.029 | 0.212 / 0.214 | **0.0016 / 0.048** | **崩** |
| hsbgc | 0.0035 / 0.030 | 0.0015 / 0.042 | 0.0035 / 0.041 | v1 时就≈0（见 §5） |

### 2.4 没坏 / 变好的任务

| 任务 | v1 | v2 | 备注 |
|---|---|---|---|
| QA dsbqa (acc) | 0.464 | 0.501 | num_fewshot 1→3，略升 |
| QA hsbqa (acc) | 0.457 | 0.471 | 略升 |
| MR dsbmr (chrf) | 2.14 | 6.90 | chrf 升；但 exact_match 0.043→0（样本仅 22 条，噪声大） |
| MR hsbmr (chrf) | 1.39 | 5.26 | 同上 |

---

## 3. 基础数据情况（测试集 & shots）

### 3.1 eval 集：无错/有错比例 —— v1、v2 完全一致（50/50）

| 任务 | v1 | v2 |
|---|---|---|
| dsbsc | 1999 条，CORRECT 999 (50%) / 有错 1000 | 1998 条，999 / 999 |
| hsbsc | 1999 条，999 / 1000 | 1998 条，999 / 999 |
| dsbgc | 1249 条，624 / 625 | 1248 条，624 / 624 |
| hsbgc | 1999 条，1000 / 999 | 1998 条，999 / 999 |

> **数据分布没有变。** SC/GC 的崩溃不是因为测试集变了，而是模型行为变了（§5）。

### 3.2 shots 组成（决定 few-shot 示范“教”模型什么）

| 任务 | v1（取 first 1） | v2（取 first 2） |
|---|---|---|
| dsbsc | `[CORRECT]` | `[CORRECT, ERROR(wokowo→wokoło)]` |
| hsbsc | `[CORRECT]` | `[CORRECT, ERROR]` |
| dsbgc | `[CORRECT]` | `[CORRECT, ERROR(źiśach→źiśimi)]` |
| **hsbgc** | **`[ERROR(Europjanom)]`** | `[CORRECT, ERROR]` |

> 注意 v1 的 hsbgc 那条 shot 是 ERROR，不是 CORRECT —— 这解释了为什么 hsbgc 在 v1 时就已经≈0（§5），是关键佐证。

### 3.3 MT 各方向样本数：3995（dev split），sampler = `first_n`，num_fewshot=5。

---

## 4. 根因 #1：MT 索布语→德语抽取失败（标签不一致）

### 4.1 证据（v2 dsb-deu，实际生成）

```
PROMPT 指令: Put it in this format <de> German translation </de>.
模型 RAW   : <deu> Es ist einfacher, Wolle und Felle abzubrechen. </deu>
抽取 FILTER : [invalid]          ← 正则 <de>\s*(...) 匹配不到 <deu>
GOLD       : Schafe und Ziegen sind leichte Beute.
```
hsb-deu 同样：模型输出 `<deu> … </deu>`，FILTER = `[invalid]`。

### 4.2 为什么模型不听指令、偏要输出 `<deu>`

因为 5 条 few-shot 示范全部以 `<deu>…</deu>` 结尾（`utils.target_deu`）。**in-context 示范的格式权重远大于一句自然语言指令**，模型照抄 `<deu>`。

### 4.3 为什么 v1 没事

v1 三处一致（指令 `<deu>` + 正则 `<deu>` + 示范 `<deu>`）：

```
V1 dsb-deu 指令: Put it in this format <deu> German translation </deu>.
模型 RAW : <deu> In der weißen Schürze liegt die Weite. </deu> (后面还有一堆解释)
抽取     : "In der weißen Schürze liegt die Weite."   ← 抽取成功
```
v1 翻译质量本就一般（BLEU 5.99），但**抽取是通的**；v2 是抽取直接归零。

### 4.4 影响范围自洽

`<de>` 改动只动了 dsb-deu / hsb-deu 的抽取标签；deu-dsb/deu-hsb 抽 `<dsb>`/`<hsb>`、dsb-hsb/hsb-dsb 抽 `<hsb>`/`<dsb>` —— 都没动，所以都正常。**完美对上现象。**

---

## 5. 根因 #2：SC / GC 的 “CORRECT 约定” 崩溃

### 5.1 度量逻辑（v1、v2 共用，未改）

`lm_eval.tasks.wmt26-lrl.utils.process_sc_results`：从输出里正则抽 `<wrong>X</wrong>`、`<corrected>Y</corrected>`，**精确字符串**对比 `doc["incorrect_word"]` / `doc["correct_word"]`。无错句子的 gold 是 `incorrect_word=correct_word="CORRECT"`，模型必须**原样输出 `CORRECT`** 才算对。

### 5.2 行为取证：模型输出 `<wrong>CORRECT</wrong>` 的比例

| 任务 | v1 模型说 CORRECT | v2 模型说 CORRECT |
|---|---|---|
| dsbsc | **73.1%** (1462/1999) → corrected 0.376 | **0.0%** (0/1998) → corrected 0.0015 |
| dsbgc | **36.7%** (458/1249) → corrected 0.212 | **0.0%** (0/1248) → corrected 0.0016 |
| hsbgc | **0.0%** (0/1999) → corrected 0.0015 | 0.0% → 0.0035 |

v2 里模型**一次都没用过 CORRECT**，对 50% 的无错句子全部判错，外加在有错句子上精确匹配率也极低（dsbsc 有错半边只命中 3/999）。

### 5.3 这是 few-shot 示范造成的，证据链：

1. **v1 内部对照**：v1 全是 1-shot，唯一区别是那条 shot 是 CORRECT 还是 ERROR：
   - shot=CORRECT 的（dsbsc/hsbsc/dsbgc）→ 模型大量说 CORRECT → 分数 0.21~0.39；
   - shot=ERROR 的（**hsbgc**）→ 模型 0% 说 CORRECT → 分数≈0。
   - ⇒ **单条示范的类型直接决定模型用不用 CORRECT 约定。**
2. **v2**：shots 改成 `[CORRECT, ERROR]`，ERROR 是离 query 最近的一条 → recency 偏置 → 模型一律“找个错”→ 0% CORRECT → 全崩。
3. **GC 的 doc_to_text 根本没改**（§1.3），却和 SC 一样崩 ⇒ **措辞改动不是原因**，共同变量是 few-shot 示范（数量 1→2 + 末条为 ERROR）。

### 5.4 更深一层的隐患

即便是 v1 那个“好看”的 0.38，本质也是“恰好被 CORRECT 示范带着多说 CORRECT”的副产物，而不是模型真的会纠错。这个度量在 50/50 平衡集上**对 few-shot 示范的类型/顺序极其敏感**，单方向 priming 就能把分数从≈0 拉到≈0.39 或反过来。这点在定方案时需要正视。

---

## 6. 结论汇总（事实层面，已证实）

1. MT dsb-deu/hsb-deu 崩 = `utils.target_deu()` 仍输出 `<deu>`，而 v2 的指令+正则改成了 `<de>`，三处不一致。**改一处即可**（统一成 `<de>` 或统一回 `<deu>`）。
2. SC/GC 崩 = v2 的 few-shot 示范（2-shot，末条 ERROR）让模型 0% 使用 CORRECT 约定；和数据分布、SC 措辞、模型本身都无关。
3. QA、MR、→索布语与索↔索 MT 未受影响（QA 因 1→3 略升）。
4. 测试集无错/有错比例 v1=v2=50/50，未变。

---

## 7. 待你决策的问题（我先不动手）

1. **当初为什么要把 MT 从 `<deu>` 改成 `<de>`、把 SC 措辞从 misspelled 改成 grammatical？** 这决定 MT 是“统一成 `<de>`”还是“回退 `<deu>`”。
2. **SC/GC 的 few-shot 策略想怎么定？** 因为度量对示范极敏感（§5.4），可选方向（仅列出，未实施）：
   - a) 保持 2-shot 但**平衡/固定顺序**（如最后一条放 CORRECT，或各 1 条但顺序对调）；
   - b) 回到 1-shot（但要意识到这只是“恰好 priming 成 CORRECT”）；
   - c) 重新设计示范，使 CORRECT 与 ERROR 都被充分演示、且不靠 recency。
   - 建议先做一个**最小消融**（仅 GC、num_fewshot 改回 1 / 或调换末条 shot）来验证 §5 结论，再决定全量方案。
3. 是否需要给 v2 的 MT“→德语”和 SC/GC 结果在 `eval_index.csv` / RESULTS.md 上标注“invalid / regressed”，以免被后续当成真实基线。

> 一旦你给出结论，我再去改 `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v2/` 下对应的 `utils.py` / `*.yaml`，并按需重跑相关 shard。
