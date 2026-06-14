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
- Prefix 环境将环境文件保留在项目目录内，便于管理和迁移。
- 与 `.venv`、`.venvs/llamafactory` 的隔离策略一致。
