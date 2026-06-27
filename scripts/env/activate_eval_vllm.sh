#!/usr/bin/env bash
# Activate the isolated vLLM evaluation environment for WMT26 backend_compare.
# This script does NOT modify .venv, does not start any evaluation, and does not
# set any global proxy.

source /home/zc/wmt26/.venvs/eval-vllm/bin/activate

# RTX 4000 series multi-GPU setup: disable NCCL P2P/IB to avoid accelerate error.
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1

echo "Activated eval-vllm environment: $(which python)"
echo "Python: $(python --version)"
echo "torch: $(python -c 'import torch; print(torch.__version__, torch.cuda.is_available())')"
echo "vllm: $(python -c 'import vllm; print(vllm.__version__)')"
echo "lm_eval: $(python -c 'import lm_eval; print(lm_eval.__version__)')"
