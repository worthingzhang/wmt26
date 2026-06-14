# WMT26 项目数据目录

本目录存放项目的数据资产。

## 目录说明

| 目录 | 说明 | 是否提交 git |
|------|------|--------------|
| `raw/` | 原始数据 | 否 |
| `interim/` | 中间产物 | 否 |
| `processed/` | 处理后的标准格式数据 | 否 |
| `manifests/` | 数据清单 | 是 |
| `cache/` | 缓存 | 否 |

## 标准格式

### CPT

`processed/cpt/*.jsonl`：

```json
{"text": "..."}
```

### SFT

`processed/sft/*.jsonl`：

```json
{"messages": [
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."}
]}
```

### OPD Prompts

`processed/opd_prompts/*.jsonl`：

```json
{"task": "mt", "prompt": "...", "source": "...", "lang": "en-de"}
```

## Manifest

每个数据集应有一个对应的 manifest 文件在 `manifests/` 下，记录来源、样本数、版本等信息。

## 注意事项

- 不要把官方 test set 用于训练。
- 避免使用与评测集重叠的数据。
- 所有外部数据需确认 license。
