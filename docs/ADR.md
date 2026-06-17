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

## ADR-8: 单卡 fallback 作为多 GPU 不兼容时的默认策略

**Decision**：

- 当模型自定义架构（如 Qwen3.5-2B 的 `qwen3_5` attention）与 `parallelize=True` 或多卡并行冲突时，默认回退到单卡 `cuda:0` 运行。
- 不为此类模型单独维护 patch，除非用户明确要求性能优化。

**Rationale**：

- 结果正确性优先于速度。
- `parallelize=True` 的设备分配逻辑与部分自定义 layer 不兼容，强行使用会导致运行时 device mismatch。
- 单卡 batch_size 调优（如生成式任务从 1 提到 8）已能在合理时间内完成 full dev 评测。
