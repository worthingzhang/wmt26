# Architecture Decision Records

## ADR-1: CPT / SFT / OPD 是并列训练算子

**Decision**：不把项目设计成固定流水线 `Base → CPT → SFT → OPD`，而是实现三个并列算子：

- `train_cpt(input_model, data_config, train_config) → output_model`
- `train_sft(input_model, data_config, train_config) → output_model`
- `train_opd(student_model, teacher_model, prompt_config, train_config) → output_model`

**Rationale**：

- 支持任意模型作为后续训练输入，便于构建模型实验 DAG。
- 便于比较不同训练路径：`Base vs CPT`、`CPT → SFT`、`SFT → OPD`、`CPT → SFT → OPD` 等。

## ADR-2: 数据、模型、runs 与外部仓库解耦

**Decision**：

- 数据放在 `/home/zc/wmt26/data/`，外部仓库只通过绝对路径读取。
- 模型 checkpoint 放在 `/home/zc/wmt26/models/checkpoints/`，不放在 `runs/`。
- 训练/评测日志和结果放在 `/home/zc/wmt26/runs/`。
- 外部仓库 `repos/` 只作为 backend，不放入数据或 checkpoint。

**Rationale**：

- 避免大文件进入 git。
- 外部仓库可独立更新，主项目配置传参即可。

## ADR-3: 每个模型、每次训练、每次评测必须可追溯

**Decision**：

- `models/registry/models.jsonl`：记录所有模型及其来源。
- `runs/train_registry.csv`：记录每次训练的运行信息。
- `runs/eval_registry.csv`：记录每次评测的运行信息。

**Rationale**：

- 支持实验图追踪和结果复现。

## ADR-4: 独立环境隔离

**Decision**：

- 主项目/官方评测环境：`.venv`（Python 3.12）
- LlamaFactory CPT/SFT 环境：`.venvs/llamafactory`（Python 3.11）
- OPD/verl 环境未来单独管理。

**Rationale**：

- 不同 backend 的依赖版本冲突较多，隔离环境更安全。
- LlamaFactory 要求 Python >=3.11.0，official_eval 要求 >=3.10，主项目用 3.12。

## ADR-5: 集中镜像配置并自动加载

**Decision**：

- 所有镜像/超时/缓存配置集中在 `configs/env/mirrors.env`。
- 所有项目脚本开头自动加载该文件，无需用户手动 `source`。

**Rationale**：

- 减少手动配置错误。
- 便于统一切换镜像源或调整超时。

## ADR-6: OPD/verl 环境使用 conda prefix

**Decision**：

- OPD/verl/vLLM/sglang 环境使用 conda prefix 环境，路径固定在 `/home/zc/wmt26/.conda/envs/verl`。
- 不使用全局 conda env 名称 `verl`，避免与其他项目冲突。
- `.conda/` 目录加入 `.gitignore`，不进入版本控制。

**Rationale**：

- THUNLP/OPD README 明确要求使用 conda 安装 OPD/verl 依赖。
## ADR-7: 外部 backend 的 task-specific 修复优先于全局框架修改

**Decision**：

- 当外部 backend（如 `repos/official_eval`）出现 task-specific 错误时，优先修改该 task 的 YAML 或 utils，而不是直接 patch backend 的全局代码。
- 若必须修改 backend 源码，需记录原因、文件、commit hash，并同步更新 `docs/EXTERNAL_REPOS.md`。

**Rationale**：

- 保持对 backend 改动的最小化，降低后续同步 upstream 的冲突成本。
- 全局 metric 或框架修改可能影响其他任务，风险更高。
- 详细的修改记录便于复现和回滚。

**本次应用**：

- Sorbian MR 任务在 `generate_until` 输出下错误使用 `acc` metric，导致 `mean` 聚合 TypeError。
- 未修改 `lm_eval/api/metrics.py`，而是将 `lm_eval/tasks/wmt26-lrl/sorbian/mr/{hsbmr,dsbmr}.yaml` 中的 `acc` 改为 `exact_match`。
- 修改 commit：`repos/official_eval@1e6ab97b005464fc0e4581cc850499eac4dc2bc9`。
- **更新（2026-06-24）**：该补丁已被官方 `8be394d6` 取代（见 ADR-10），对齐时丢弃，仅以 tag `pre-align-1e6ab97b` 备份。

## ADR-8: 单卡 fallback 作为多 GPU 不兼容时的默认策略

**Decision**：

- 当模型自定义架构（如 Qwen3.5-2B 的 `qwen3_5` attention）与 `parallelize=True` 或多卡并行冲突时，默认回退到单卡 `cuda:0` 运行。
- 不为此类模型单独维护 patch，除非用户明确要求性能优化。

**Rationale**：

- 结果正确性优先于速度。
- `parallelize=True` 的设备分配逻辑与部分自定义 layer 不兼容，强行使用会导致运行时 device mismatch。
- 单卡 batch_size 调优（如生成式任务从 1 提到 8）已能在合理时间内完成 full dev 评测。

## ADR-9: Full-model CPT on 8× RTX 4090 requires DeepSpeed ZeRO-3

**Decision**:

- Full CPT of Qwen3.5-2B with `cutoff_len=4096` on 8× RTX 4090 (24GB) uses DeepSpeed ZeRO-3 via LlamaFactory.
- Do not fall back to plain DDP or non-sharded full-model training for this workload.

**Rationale**:

- Plain DDP and non-sharded 1024/4096 smoke attempts OOM on 24GB cards.
- ZeRO-3 shards optimizer states, gradients, and parameters across GPUs, fitting the model and 4096-length sequences.
- Verified by probe4096 (50 steps) and currently running full CPT (1000 steps).

**Configuration**:

- `deepspeed: /home/zc/wmt26/repos/thunlp_opd/LlamaFactory/examples/deepspeed/ds_z3_config.json`
- `finetuning_type: full`
- `cutoff_len: 4096`
- `per_device_train_batch_size: 1`
- `gradient_accumulation_steps: 4`
- `bf16: true`
- `gradient_checkpointing: true`

**Notes**:

- ZeRO-3 init is slower than DDP due to parameter partitioning, but training step time stabilizes at ~24 s/step.
- Launch must be via `FORCE_TORCHRUN=1 llamafactory-cli train ...` to ensure 8-GPU torchrun.

## ADR-10: 官方口径优先（official zero-shot），暂停 few-shot 实验线

**Decision**：

- 项目评测主线切换为 **官方 zero-shot 口径**：使用 `repos/official_eval` 官方任务（`sorbian_dev` group + QA），`enable_thinking=False`、`--apply_chat_template`、零样本。
- few-shot v1/v2 保留但**标记为 experimental**，v2 明确标 `invalid/regressed`；不再作为 baseline 或对外汇报依据。
- `repos/official_eval` 与官方 eval-code 仓库 `TUM-NLP/llms-lim-res-eval-2026` 对齐（`upstream`=eval-code、`data`=data repo），采纳**纯官方口径**，不保留本地 MR 补丁 `1e6ab97b`，仅通过 tag `pre-align-1e6ab97b` 备份。
- data repo 运行副本通过 symlink 固定到官方 commit，并在 `run.yaml` 中记录 (eval-code commit, data commit)，确保所有 baseline 可比。

**Rationale**：

- WMT26 排行榜以官方 zero-shot 为准，few-shot 是内部探索。
- 自研 few-shot 结果对 prompt/shots 顺序极度敏感（v2 的 MT 标签不一致、SC/GC CORRECT 约定崩溃），已证明不可靠。
- 与官方 eval-code 对齐可复用其上游修复（MR `exact_match`、SC/GC 正则放宽 `\s*`），避免本地补丁分叉。

**本次应用**：

- eval-code 对齐到 `repos/official_eval@711a2b4f`（官方 `upstream/main`）；data repo @ `2b712ac6`。
- 旧本地 MR 补丁 `1e6ab97b` 由 `pre-align-1e6ab97b` tag 备份。
