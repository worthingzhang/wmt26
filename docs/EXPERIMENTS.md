# 实验命名规范

本文档说明 `run_id`、`model_id`、`eval_id` 的命名规范，确保实验可追溯、可比较。

## 命名原则

- **可读性**：从 ID 能推断出训练类型、数据来源、版本。
- **唯一性**：每次运行使用新的 ID，避免覆盖。
- **简洁性**：避免过长，但保留关键信息。

## `model_id` 命名规范

```
{training_type}_{data_version}_{input_hint}_{version}
```

| 字段 | 说明 |
|------|------|
| `training_type` | `cpt` / `sft` / `opd` / `mixed` |
| `data_version` | 数据配置版本，如 `mix_v1` |
| `input_hint` | 输入模型提示，如 `from_base`、`from_cpt_v1`、`sft_mt_teacher` |
| `version` | 本次实验版本，如 `v1`、`v2` |

### 示例

- `cpt_mix_v1_from_base_v1`
- `sft_mix_v1_from_cpt_v1_v2`
- `opd_prompt_v1_sft_from_base_mt_teacher_v1`

## `run_id` 命名规范

```
{training_type}_{data_version}_{input_hint}_{version}
```

通常与 `model_id` 保持一致，但也可加上 `smoke` 等标记：

- `cpt_smoke_base_v1`
- `sft_full_from_cpt_v1_v2`
- `opd_smoke_sft_mt_teacher_v1`

## `eval_id` 命名规范

```
eval_{model_id}_{version}
```

示例：

- `eval_base_qwen35_2b_v1`
- `eval_cpt_smoke_base_v1`
- `eval_sft_smoke_from_cpt_v1_v2`

## 注册表字段说明

### models/registry/models.jsonl

每行 JSON，至少包含：

```json
{
  "model_id": "cpt_smoke_base_v1",
  "model_path": "/home/zc/wmt26/models/checkpoints/cpt/cpt_smoke_base_v1",
  "training_type": "cpt",
  "input_model": "/home/zc/wmt26/models/base/Qwen3.5-2B",
  "teacher_model": null,
  "data_config": "configs/data/cpt_mix_v1.yaml",
  "train_config": "configs/train/cpt/cpt_smoke.yaml",
  "created_at": "2026-06-14T12:00:00Z",
  "notes": "CPT smoke test"
}
```

### runs/train_registry.csv

字段：

- `run_id`
- `train_type`
- `input_model`
- `teacher_model`
- `output_model`
- `data_config`
- `train_config`
- `log_dir`
- `status`
- `notes`

### runs/eval_registry.csv

字段：

- `eval_id`
- `model_id`
- `model_path`
- `eval_config`
- `result_path`
- `status`
- `notes`

## 版本管理

- 每次修改数据配置或训练配置，应升级版本号。
- 同一组配置跑多次，可在版本号后加 `_run2`、`_run3`。
- 所有变更应在 `docs/RESULTS.md` 和注册表中记录。
