# vLLM Evaluation Environment

> 用途：WMT26 项目 backend_compare 的 candidate backend 环境。
> 状态：已创建并验证（2026-06-24）。
> 注意：该环境**完全隔离**，没有污染 `.venv`（HF reference backend 环境）。

## 环境路径

```text
/home/zc/wmt26/.venvs/eval-vllm
```

激活方式：

```bash
source scripts/env/activate_eval_vllm.sh
```

或手动：

```bash
source /home/zc/wmt26/.venvs/eval-vllm/bin/activate
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
```

## 关键包版本

| 包 | 版本 | 说明 |
|---|---|---|
| Python | 3.12.12 | 与 `.venv` 一致 |
| torch | 2.6.0+cu124 | CUDA 12.4 |
| torch.version.cuda | 12.4 | 与 `.venv` 一致 |
| transformers | 5.12.1 | 略高于 `.venv` 的 5.12.0，在隔离环境内可接受 |
| vllm | 0.8.4 | candidate backend |
| lm_eval | 0.4.12.dev0 | 来自 `repos/official_eval` 的可编辑安装 |

## 安装命令记录

```bash
# 1. 创建隔离环境（不要修改 .venv）
uv venv --python 3.12 /home/zc/wmt26/.venvs/eval-vllm

# 2. 激活
source /home/zc/wmt26/.venvs/eval-vllm/bin/activate

# 3. 升级 setuptools（vllm 需要 >=74.1.1）
uv pip install --upgrade setuptools --index-url https://pypi.org/simple

# 4. 安装 vLLM（PyPI）+ torch CUDA 12.4 wheel
uv pip install vllm==0.8.4 --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cu124

# 5. 安装官方 eval repo 的 lm_eval（可编辑）
uv pip install -e repos/official_eval[hf] --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cu124
```

## 是否污染 `.venv`

**没有。** 验证结果：

```bash
source .venv/bin/activate
python -c "import vllm"  # ModuleNotFoundError，符合预期
```

`.venv` 中 torch / transformers / lm_eval 版本保持不变：

- torch: 2.6.0+cu124
- transformers: 5.12.0
- lm_eval: 0.4.12.dev0

## 轻量验证结果

```bash
source scripts/env/activate_eval_vllm.sh
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.version.cuda)"
# torch: 2.6.0+cu124 cuda: True torch.version.cuda: 12.4

python -c "import transformers; print(transformers.__version__)"
# transformers: 5.12.1

python -c "import vllm; print(vllm.__version__)"
# vllm: 0.8.4

python -m lm_eval --help | head -40
# lm_eval CLI 正常启动
```

## 已知警告

`requests` 报 `urllib3` / `chardet` 版本不匹配警告，但不影响 `vllm`、`lm_eval` 导入和 CLI 启动。该警告来自 vLLM 依赖链中的旧版本 `requests`；后续如影响运行时，可单独升级 `urllib3` 或 `requests`。

## 删除方式

如果 vLLM backend_compare 结果不可接受，可直接删除整个隔离环境：

```bash
rm -rf /home/zc/wmt26/.venvs/eval-vllm
```

不会影响到 `.venv`、模型、数据或已产生的评测结果。

## 后续接入条件

vLLM **目前只是 candidate backend**。只有当 backend_compare 同时满足以下条件时，才允许接入 `official_zeroshot` 主线：

1. HF vs vLLM 在相同模型、相同任务、相同 limit 下分数差异很小。
2. QA `acc` 差异不超过 0.5~1 个百分点。
3. MT `chrF++` / `bleu` 差异很小。
4. SC / GC / MR `exact_match` 无明显异常。
5. vLLM 的 parse invalid rate 没有上升。
6. vLLM 速度有明显提升。

在未通过 backend_compare 之前，所有 vLLM 结果必须写入 `reports/eval_experimental/backend_compare/` 和 `runs/eval_experimental/backend_compare/`，不得进入 `reports/eval_official/`。

## 相关文档

- [docs/eval/EVAL_RESULT_STANDARD.md](EVAL_RESULT_STANDARD.md) — 结果目录结构
- [docs/eval/OFFICIAL_ZEROSHOT_RUNBOOK.md](OFFICIAL_ZEROSHOT_RUNBOOK.md) — HF official zero-shot 入口用法
- [docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md](OFFICIAL_EVAL_ALIGNMENT_PLAN.md) — 官方评测口径对齐
- `scripts/env/activate_eval_vllm.sh` — 环境激活脚本
