# Eval Result Standard

> 生效日期：2026-06-24
> 适用范围：WMT26 Limited Resources LLM 项目所有模型（base / CPT / SFT / OPD）的 Sorbian 官方 zero-shot 评测，以及内部 experimental 评测。

## 1. 总原则

### 1.1 评测主线

- **官方主线 = official zero-shot**，使用 `repos/official_eval` 的官方任务（`sorbian_dev` group + QA）。
- **few-shot v1/v2 是 experimental**，不得作为官方 baseline 或对外汇报依据。
- **v2 的 MT→deu、SC、GC 已确认 invalid/regressed**（见 `docs/eval/DEVSPLIT_FEWSHOT_V2_REGRESSION_REPORT.md`）。
- 旧的 `reports/eval/base_qwen35_2b__zero_shot` 是 **pre-official-align** 结果（MR 含 chrf、SC/GC 用旧严格正则），**不得标记为 official-ready**。
- 后续 CPT / SFT / OPD checkpoint 全部复用同一套 `official_zeroshot` 结构。

### 1.2 `runs/` 与 `reports/` 分工

```text
runs/   = 原始运行证据区（raw evidence）
reports/= 聚合结果展示区（human-readable summary）
```

**`runs/` 保存：**

- lm-eval 原始 `results_*.json`
- `samples_*.jsonl`
- `run.log`、命令脚本、环境变量
- 多卡 shard 输出（`shards/gpu*/...`）
- 原始 `run.yaml`（如果生成器已产出）

可以很详细，但不作为人类主阅读入口。

**`reports/` 保存：**

- `RESULTS.md`：人类可读汇总
- `scores.csv`：扁平任务/指标表
- `run.yaml`：聚合后的标准 metadata
- `raw/README.md`：文字说明指向对应 `runs/` 源目录

不直接堆放大量 `samples_*.jsonl` 或 shard 原始文件。

---

## 2. 目录规范

### 2.1 官方 zero-shot 主线

```text
reports/eval_official/
└── <model_tag>/
    └── official_zeroshot/
        ├── RESULTS.md
        ├── scores.csv
        ├── run.yaml
        └── raw/
            └── README.md

runs/eval_official/
└── <model_tag>/
    └── official_zeroshot/
        └── <run_id>/
            ├── qa/
            │   └── __home__zc__.../results_*.json
            │   └── __home__zc__.../samples_*.jsonl
            │   └── run.log
            ├── gen/
            │   └── __home__zc__.../results_*.json
            │   └── __home__zc__.../samples_*.jsonl
            │   └── run.log
            ├── logs/
            ├── commands/
            ├── status/
            └── run.yaml
```

- `<model_tag>` 见第 3 节。
- `<run_id>` 可包含时间戳，例如 `eval_base_qwen35_2b_official_20260624_01`。
- QA 与生成式任务分两个子目录，与官方 README 的两段式命令一致。
- 多卡 shard 原始结果放在 `runs/eval_official/<model_tag>/official_zeroshot/<run_id>/shards/gpu*/` 下，聚合后只把 summary 写入 `reports/`。

### 2.2 Experimental / 内部探索

```text
reports/eval_experimental/
├── fewshot/
│   └── <model_tag>/fewshot_devsplit_v{1,2}/
├── backend_compare/
│   └── <model_tag>/official_zeroshot__vllm_candidate/
└── smoke/
    └── <model_tag>/smoke_<what>/

runs/eval_experimental/
├── fewshot/
├── backend_compare/
├── smoke/
└── debug/
```

- `fewshot/`：few-shot v1/v2 等 overlay 实验结果。
- `backend_compare/`：vLLM / sglang 等候选 backend 与 HF reference 的对比结果。
- `smoke/`：limit/batch_size 探测、快速验证。
- `debug/`：失败的、临时的、未聚合的运行。

### 2.3 旧目录处理（仅规范，不移动）

现有旧目录保留在原地，后续单独迁移：

- `reports/eval/base_qwen35_2b__zero_shot` → 未来归档到 `reports/eval_experimental/pre_official_align/` 或 `archive/`
- `reports/eval/base_qwen35_2b__fewshot_devsplit_v1` → `reports/eval_experimental/fewshot/base_qwen35_2b/fewshot_devsplit_v1/`
- `runs/eval/Qwen3.5-2B/...` → 未来按 model_tag 重命名/归档

---

## 3. `model_tag` 规则

### 3.1 必须来自注册表或明确记录

- `model_tag` 必须与 `models/registry/models.jsonl` 中的 `model_id` 一致。
- 如果评测的是未注册模型，必须先注册或在本条 `run.yaml` 中显式声明 `model_tag` 来源。

### 3.2 命名示例

| 模型 | model_tag |
|---|---|
| base 模型 | `base_qwen35_2b` |
| CPT probe | `cpt_v1_official_plaintext_dsb4x_probe4096` |
| CPT full | `cpt_v1_official_plaintext_dsb4x_full` |
| SFT from CPT | `sft_v1_xxx_from_cpt_v1_official_plaintext_dsb4x_full` |
| OPD | `opd_v1_xxx` |

### 3.3 禁止事项

- **禁止**在正式 `reports/eval_official/` 中使用 `Qwen3.5-2B` 这种不稳定显示名作为 `model_tag`。
- **禁止**用时间戳作为 `reports/` 主目录名。
- 时间戳只能出现在 `runs/eval_official/<model_tag>/official_zeroshot/<run_id>/` 的 `<run_id>` 中。

---

## 4. `run.yaml` 强制字段

每个聚合结果目录必须包含 `run.yaml`，schema 如下：

```yaml
# 模型标识
model_tag: "base_qwen35_2b"
model_path: "/home/zc/wmt26/models/base/Qwen3.5-2B"
model_family: "Qwen3.5-2B"
checkpoint_type: "base"   # base | cpt | sft | opd

# 评测设置
eval_setting: "official_zeroshot"   # 或 fewshot_devsplit_v1, backend_compare, smoke, ...
shot_setting: "zero_shot"           # zero_shot | fewshot

# 推理后端
backend: "hf"                       # hf | vllm | sglang
backend_role: "reference"           # reference | candidate | accepted
official: true                      # true | false

# 代码/数据版本（保证可比性）
eval_code_repo: "https://github.com/TUM-NLP/llms-lim-res-eval-2026"
eval_code_commit: "711a2b4f"
data_repo: "https://github.com/TUM-NLP/llms-limited-resources2026"
data_commit: "2b712ac6"

# 任务配置
tasks_qa: ["hsbqa", "dsbqa"]
tasks_gen: ["sorbian_dev"]
apply_chat_template_for_gen: true
enable_thinking_for_gen: false
qa_uses_chat_template: false

# 运行配置
batch_size: 1
gpu_setting: "single_gpu"   # single_gpu | 8gpu_sharded | ...
dtype: "bfloat16"
command: "bash scripts/eval/eval_official_sorbian.sh --model-path ..."

# 来源与状态
source_run_dir: "runs/eval_official/base_qwen35_2b/official_zeroshot/eval_base_qwen35_2b_official_20260624_01"
generated_at: "2026-06-24T..."
status: "aggregated"        # aggregated | completed | failed | smoke

# 备注
notes: "Official zero-shot baseline on aligned eval-code 711a2b4f + data 2b712ac6"
```

### 4.1 backend 规则

- **HF 是当前 reference backend**。
- **vLLM / sglang 在通过 `backend_compare` 一致性验证前，只能作为 candidate**，结果写入 `reports/eval_experimental/backend_compare/`。
- 一旦某 backend 被验证为与 HF reference 一致并被接受，后续主线结果仍放在 `official_zeroshot/` 目录下，不长期维护 `official_zeroshot_hf` / `official_zeroshot_vllm` 两套主目录。
- `backend` 信息只写入 `run.yaml` 和 `eval_index.csv`，不体现在目录名中。

### 4.2 `checkpoint_type`

- `base`：未训练的 base 模型。
- `cpt`：继续预训练（Continual Pre-Training）产出。
- `sft`：监督微调（Supervised Fine-Tuning）产出。
- `opd`：在线偏好蒸馏（Online Preference Distillation）产出。

---

## 5. `reports/eval/eval_index.csv` 字段

### 5.1 表头

```csv
standard_run_dir,model_tag,checkpoint_type,eval_setting,shot_setting,parallel_setting,backend,backend_role,official,eval_code_commit,data_commit,source_run_dir,results_md,scores_csv,run_yaml,status,notes
```

### 5.2 字段说明

| 字段 | 说明 |
|---|---|
| `standard_run_dir` | 聚合结果目录，必须是 `reports/eval_official/...` 或 `reports/eval_experimental/...` |
| `model_tag` | 来自注册表的 model_id |
| `checkpoint_type` | base / cpt / sft / opd |
| `eval_setting` | official_zeroshot / fewshot_devsplit_v1 / backend_compare / smoke / ... |
| `shot_setting` | zero_shot / fewshot |
| `parallel_setting` | single_gpu / 8gpu_sharded / mixed |
| `backend` | hf / vllm / sglang |
| `backend_role` | reference / candidate / accepted |
| `official` | true / false |
| `eval_code_commit` | `repos/official_eval` 的 commit hash |
| `data_commit` | 官方 data repo 的 commit hash |
| `source_run_dir` | 原始运行目录（`runs/...`） |
| `results_md` | `RESULTS.md` 路径 |
| `scores_csv` | `scores.csv` 路径 |
| `run_yaml` | `run.yaml` 路径 |
| `status` | aggregated / completed / failed / smoke |
| `notes` | 人工标注，必须包含 `[PRE-OFFICIAL-ALIGN]` / `[EXPERIMENTAL]` / `[REGRESSED]` / `[INVALID]` 等 |

### 5.3 旧记录标注规范

- pre-official-align 的 zero-shot：`notes` 必须以 `[PRE-OFFICIAL-ALIGN]` 开头。
- few-shot v1：`[EXPERIMENTAL]`。
- few-shot v2：`[EXPERIMENTAL/REGRESSED/INVALID]`。
- 所有 non-official 结果：`official=false`。

---

## 6. 当前占位文件状态（截至 2026-06-24）

> 以下文件状态已审计，**本轮不修改**，将在后续设计 `scripts/eval/eval_official_sorbian.sh` 和 vLLM backend_compare 时再重写。

### 6.1 `configs/eval/official_all_tasks.yaml`

- **状态：占位文件**。
- 内容仍为 TODO 任务名（`mt_todo`、`qa_todo` 等）和无关语言对列表，与 `repos/official_eval` 的实际任务名称不一致。
- 当前实际评测直接通过 `scripts/eval/eval_base_full.sh` 硬编码任务调用，不读取此文件。
- 后续决定：要么重写为官方任务列表模板，要么弃用，由新 `eval_official_sorbian.sh` 直接管理任务。

### 6.2 `scripts/eval/eval_model.sh`

- **状态：骨架脚本**。
- 期望调用 `repos/official_eval/eval.py`，但该文件不存在，因此会回退到生成 placeholder `results.json`。
- 参数设计（`--eval-id`、`--model-id`、`--model-path`、`--eval-config`、`--output-dir`）合理，但内部逻辑未对接真实 lm-eval 命令。
- 后续决定：与新官方入口 `eval_official_sorbian.sh` 合并或重写，移除 placeholder 逻辑。

---

## 7. 迁移路线图

1. **本轮**：只更新规范、索引、文档和只读检查工具。
2. **下一轮**：实现 `scripts/eval/eval_official_sorbian.sh`（HF backend），重跑 base official zero-shot，写入 `reports/eval_official/base_qwen35_2b/official_zeroshot/`。
3. **再下一轮**：注册 CPT full，跑 `reports/eval_official/cpt_v1_official_plaintext_dsb4x_full/official_zeroshot/`。
4. **vLLM phase**：实现 backend_compare，结果写入 `reports/eval_experimental/backend_compare/`，验证通过后再进入主线。
5. **归档 phase**：将旧 `reports/eval/` 和 `runs/eval/` 中的 pre-official-align / experimental / debug 结果迁移到 `reports/eval_experimental/`、`runs/eval_experimental/` 或 `archive/`。

---

## 8. 禁止事项

- 不允许创建没有 `model_tag`、`backend`、`eval_code_commit`、`data_commit` 的正式评测结果。
- 不允许把 smoke / debug / few-shot 结果写进 `reports/eval_official/`。
- 不允许把多卡 shard 原始文件堆放在 `reports/` 下。
- 不允许用时间戳作为 `reports/` 主目录名。
- 不允许称 pre-official-align 的 zero-shot 为 official-ready。
