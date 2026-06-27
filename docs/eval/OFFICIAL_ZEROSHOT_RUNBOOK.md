# Official Zero-shot Sorbian Evaluation Runbook

> 本文档说明 `scripts/eval/eval_official_sorbian.sh` 的用法、目录结构和后端规则。

## 1. 用途

`scripts/eval/eval_official_sorbian.sh` 是 WMT26 项目官方 zero-shot 评测的统一入口，支持任意注册过的 checkpoint：

- base 模型
- CPT 模型
- SFT 模型
- OPD 模型

它严格遵循官方 eval-code（`repos/official_eval`）的 Sorbian 评测口径：

- QA 任务：`hsbqa`、`dsbqa`，**不加** `--apply_chat_template`，**不加** `enable_thinking=False`。
- 生成式任务：`sorbian_dev`，**必须加** `--apply_chat_template`，**必须** `enable_thinking=False`。
- 零样本：不注入任何 few-shot。

## 2. 基本用法

### 2.1 Dry-run（推荐先预览）

```bash
cd /home/zc/wmt26
bash scripts/eval/eval_official_sorbian.sh \
  --model-tag base_qwen35_2b \
  --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \
  --backend hf \
  --dry-run
```

`--dry-run` 会打印运行计划（目录、命令、run.yaml 位置），**不创建目录、不写文件、不启动 lm_eval**。

### 2.2 正式运行

```bash
cd /home/zc/wmt26
bash scripts/eval/eval_official_sorbian.sh \
  --model-tag base_qwen35_2b \
  --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \
  --backend hf
```

正式运行会：

1. 创建 `runs/eval_official/<model_tag>/official_zeroshot/<run_id>/`。
2. 写入 `commands/qa.sh`、`commands/gen.sh`。
3. 写入 `run.yaml`（含 eval-code commit、data commit、backend、命令等）。
4. 创建 `reports/eval_official/<model_tag>/official_zeroshot/raw/README.md` 指针。
5. 依次执行 QA 和生成式 lm_eval 命令，并把 stdout/stderr tee 到 `logs/qa.log`、`logs/gen.log`。
6. 成功后将 `run.yaml` 的 `status` 从 `running` 更新为 `completed`。

### 2.3 自定义 run_id

```bash
bash scripts/eval/eval_official_sorbian.sh \
  --model-tag base_qwen35_2b \
  --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \
  --backend hf \
  --run-id eval_base_qwen35_2b_official_20260624_01
```

未指定 `--run-id` 时，自动生成：

```text
eval_<model_tag>__official_zeroshot__<backend>_<YYYYMMDD_HHMMSS>
```

## 3. 脚本参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `--model-tag` | 是 | 模型注册 ID，如 `base_qwen35_2b`、`cpt_v1_official_plaintext_dsb4x_full` |
| `--model-path` | 是 | 模型目录绝对路径 |
| `--backend` | 是 | `hf` 或 `vllm`（当前只实现 `hf`） |
| `--run-id` | 否 | 自定义运行 ID；省略则自动生成 |
| `--dry-run` | 否 | 仅打印计划，不执行 |
| `--help` | 否 | 显示帮助 |

## 4. 目录结构

### 4.1 原始运行证据

```text
runs/eval_official/
└── <model_tag>/
    └── official_zeroshot/
        └── <run_id>/
            ├── qa/                  # lm-eval QA 输出
            │   └── __home__zc__.../results_*.json
            │   └── __home__zc__.../samples_*.jsonl
            ├── gen/                 # lm-eval 生成式输出
            │   └── __home__zc__.../results_*.json
            │   └── __home__zc__.../samples_*.jsonl
            ├── logs/
            │   ├── qa.log
            │   └── gen.log
            ├── commands/
            │   ├── qa.sh
            │   └── gen.sh
            ├── status/
            │   ├── qa.exit
            │   └── gen.exit
            └── run.yaml
```

### 4.2 聚合结果展示

```text
reports/eval_official/
└── <model_tag>/
    └── official_zeroshot/
        ├── RESULTS.md        # 由 aggregate_eval_results.py 生成
        ├── scores.csv        # 由 aggregate_eval_results.py 生成
        ├── run.yaml          # 由 aggregate_eval_results.py 生成
        └── raw/
            └── README.md     # 指向 runs/... 源目录
```

`eval_official_sorbian.sh` 本身**不写** `RESULTS.md` 和 `scores.csv`，只创建 `raw/README.md` 指针。聚合由 `scripts/eval/aggregate_eval_results.py` 后续完成。

## 5. 后端规则

### 5.1 HF（当前唯一实现）

- `backend=hf` → `backend_role=reference`。
- 在 `official_zeroshot` 设置下，`official=true`。
- 当前使用单卡 `cuda:0`，`--batch_size auto`。
- 多卡 task-sharded 模式后续单独设计，不在本脚本第一轮实现。

### 5.2 vLLM（未实现）

```bash
bash scripts/eval/eval_official_sorbian.sh \
  --model-tag base_qwen35_2b \
  --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \
  --backend vllm \
  --dry-run
```

会报错并退出：

```text
Error: vLLM backend is not implemented yet; use the backend_compare stage later.
```

vLLM 路线图：

1. **backend_compare 阶段**：在 `reports/eval_experimental/backend_compare/` 下跑 vLLM candidate，与 HF reference 逐项对比 MT/QA/SC/GC/MR 分数。
2. **一致性验证**：要求所有任务差异在可接受阈值内。
3. **接受后**：vLLM 结果可以进入 `reports/eval_official/<model_tag>/official_zeroshot/`，`backend=vllm`，`backend_role=accepted`，`official=true`。
4. **不接受前**：vLLM 结果只能留在 experimental，不能进入 official 主线。

## 6. `checkpoint_type` 自动推断

脚本根据 `model_tag` 前缀推断：

| 前缀 | checkpoint_type |
|---|---|
| `base_` | `base` |
| `cpt_` | `cpt` |
| `sft_` | `sft` |
| `opd_` | `opd` |
| 其他 | `unknown`（脚本会警告，但继续） |

## 7. `run.yaml` 字段

运行结束后，`runs/eval_official/<model_tag>/official_zeroshot/<run_id>/run.yaml` 至少包含：

```yaml
model_tag: "base_qwen35_2b"
model_path: "/home/zc/wmt26/models/base/Qwen3.5-2B"
model_family: "Qwen3.5-2B"
checkpoint_type: "base"
eval_setting: "official_zeroshot"
shot_setting: "zero_shot"
backend: "hf"
backend_role: "reference"
official: true
eval_code_repo: "https://github.com/TUM-NLP/llms-lim-res-eval-2026"
eval_code_commit: "711a2b4f"
data_repo: "https://github.com/TUM-NLP/llms-limited-resources2026"
data_commit: "2b712ac6"
tasks_qa:
  - "hsbqa"
  - "dsbqa"
tasks_gen:
  - "sorbian_dev"
apply_chat_template_for_gen: true
enable_thinking_for_gen: false
qa_uses_chat_template: false
batch_size: "auto"
gpu_setting: "single_gpu"
dtype: "bfloat16"
command_qa: 'python3 -m lm_eval run --model hf --model_args "pretrained=..." --tasks hsbqa,dsbqa ...'
command_gen: 'python3 -m lm_eval run --model hf --model_args "pretrained=...,enable_thinking=False" --apply_chat_template --tasks sorbian_dev ...'
source_run_dir: "runs/eval_official/base_qwen35_2b/official_zeroshot/..."
generated_at: "2026-06-24T..."
status: "completed"
notes: "Official zero-shot Sorbian evaluation (HF reference backend) generated by scripts/eval/eval_official_sorbian.sh."
```

## 8. 与旧脚本的关系

- `scripts/eval/eval_base_full.sh`：旧的 base-only zero-shot 脚本，仍保留。不要修改它。
- `scripts/eval/eval_model.sh`：占位骨架，未对接真实 lm-eval。不要修改它。
- `scripts/eval/eval_official_sorbian.sh`：新的统一入口，后续所有官方 zero-shot 评测都走这里。

## 9. 后续步骤

1. 用 `--dry-run` 确认计划。
2. 正式跑 base_qwen35_2b official zero-shot。
3. 注册 CPT full，跑其 official zero-shot。
4. 设计并实现 vLLM backend_compare。
5. 归档旧 `reports/eval/` 和 `runs/eval/` 中的 pre-official-align / experimental 结果。
