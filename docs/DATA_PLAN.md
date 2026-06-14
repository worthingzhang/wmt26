# 数据规划

本文档说明 CPT、SFT、OPD 三类训练所需数据的来源、目标格式、以及使用限制。

## 通用原则

- 所有原始数据放在 `data/raw/`，不提交 git。
- 处理后的标准格式数据放在 `data/processed/`，不提交 git。
- 每个数据集生成一个 manifest，放在 `data/manifests/`，提交 git。
- 外部训练仓库只通过绝对路径读取 `data/processed/` 下数据，不复制进 `repos/`。

## CPT 数据

### 目标格式

`data/processed/cpt/*.jsonl`，每行：

```json
{"text": "..."}
```

### 数据来源

- 官方提供的继续预训练语料
- 往年 WMT 任务相关单语/平行语料
- 外部公开单语语料（需注意许可证）
- 合成语料（如 back-translation、LLM 生成后过滤）

### 处理要点

- 语言混合配比需要实验
- 去重、清洗、长度过滤
- 可选 packing（LlamaFactory 支持）

## SFT 数据

### 目标格式

`data/processed/sft/*.jsonl`，每行采用 ShareGPT messages 格式：

```json
{"messages": [
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."}
]}
```

同时生成 `dataset_info.json` 供 LlamaFactory 使用。

### 数据来源

按任务类型区分：

| 任务类型 | 说明 |
|----------|------|
| MT | 机器翻译平行句对 |
| QA | 问答数据 |
| SC | Sentence/Sequence Classification |
| GC | Grammaticality/Generation Challenge |
| MR | Multi-hop Reasoning / 推理类 |

### 数据分类

- **官方数据**：WMT26 官方发布的数据，按规则使用。
- **往年数据**：往届 WMT 任务数据，可用于训练，需注意 license。
- **外部公开数据**：如 Flores、XP3、Alpaca 等，需确认 license。
- **合成数据**：通过教师模型或规则生成的数据，需控制质量。

## OPD Prompt 数据

### 目标格式

`data/processed/opd_prompts/*.jsonl` 或 `.parquet`，每条至少包含：

```json
{
  "task": "mt",
  "prompt": "Translate the following sentence to German: ...",
  "source": "sft_v1",
  "lang": "en-de"
}
```

### 来源

- 从 SFT 数据中抽取 prompt（去掉 reference answer）
- 额外收集的 prompt 池
- 按任务和语言分桶，便于控制配比

## 数据使用限制

### 禁止或谨慎使用

- **Test split**：任何任务的官方 test set 都不能用于训练。
- **可能泄漏的 benchmark**：避免使用与官方评测高度重叠的数据。
- **PolyMath 相关数据**：如任务涉及，需特别确认是否允许用于训练。
- **未授权数据**：只使用 license 允许的数据。

### 建议做法

- 维护 `data/manifests/` 记录每个数据集的 license、来源、split、用途。
- 对合成数据标注生成方法和过滤规则。
- 定期检查数据是否与评测集重叠。

## Manifest 格式

每个 manifest 为 JSON，包含：

```json
{
  "manifest_version": "1.0",
  "dataset_id": "cpt_mix_v1",
  "dataset_type": "cpt",
  "output_dir": "data/processed/cpt",
  "files": ["cpt_mix_v1.jsonl"],
  "num_samples": 12345,
  "sources": ["wmt26_official", "flores", "synthetic_bt"],
  "created_at": "2026-06-14T12:00:00Z",
  "notes": "..."
}
```
