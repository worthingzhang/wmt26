#!/usr/bin/env bash
# Full baseline evaluation for base Qwen3.5-2B on all Sorbian tasks.
# Runs QA tasks (loglikelihood) and generative tasks separately to match
# the official_eval baseline recipe.

set -euo pipefail

# Make all 8 GPUs visible (only cuda:0 will be used because
# parallelize=True is incompatible with Qwen3.5-2B's custom architecture).
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# RTX 4000 series multi-GPU setup: disable NCCL P2P/IB to avoid accelerate error.
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1

PROJECT_ROOT="/home/zc/wmt26"
MODEL_PATH="${PROJECT_ROOT}/models/base/Qwen3.5-2B"
OUTPUT_DIR="${PROJECT_ROOT}/runs/eval/eval_base_qwen35_2b_full"
BATCH_SIZE=1
DEVICE="cuda:0"
DTYPE="bfloat16"

echo "=== Full baseline Sorbian evaluation ==="
echo "Project root : ${PROJECT_ROOT}"
echo "Model path   : ${MODEL_PATH}"
echo "Output dir   : ${OUTPUT_DIR}"
echo "Batch size   : ${BATCH_SIZE}"
echo "Device       : ${DEVICE}"
echo "Dtype        : ${DTYPE}"
echo "CUDA devices : ${CUDA_VISIBLE_DEVICES}"
echo ""
echo "Note: parallelize=True is incompatible with Qwen3.5-2B (device mismatch"
echo "      inside custom attention), so the eval runs on a single GPU."

cd "${PROJECT_ROOT}"

# Activate main/eval environment
source "${PROJECT_ROOT}/.venv/bin/activate"

which python
python --version
python -c "import lm_eval; print('lm_eval:', lm_eval.__version__)"
python -c "import torch; print('torch:', torch.__version__, 'cuda:', torch.cuda.is_available())"

mkdir -p "${OUTPUT_DIR}"

# The official_eval task configs reference data files via a relative path
# "llms-limited-resources2026/...". Run lm_eval from data/raw so that path
# resolves to the local data repo clone.
DATA_DIR="${PROJECT_ROOT}/data/raw"
if [[ ! -d "${DATA_DIR}/llms-limited-resources2026" ]]; then
    echo "Error: evaluation data repo not found at ${DATA_DIR}/llms-limited-resources2026"
    echo "Clone it with: git clone https://github.com/TUM-NLP/llms-limited-resources2026.git ${DATA_DIR}/llms-limited-resources2026"
    exit 1
fi

# Run 1: QA tasks (loglikelihood-based). No chat template needed.
echo ""
echo "=== Run 1/2: Sorbian QA tasks (hsbqa, dsbqa) ==="
(
    cd "${DATA_DIR}"
    python -m lm_eval run \
        --model hf \
        --model_args "pretrained=${MODEL_PATH},trust_remote_code=True,dtype=${DTYPE}" \
        --tasks hsbqa dsbqa \
        --batch_size "${BATCH_SIZE}" \
        --device "${DEVICE}" \
        --output_path "${OUTPUT_DIR}/qa" \
        --log_samples \
        2>&1 | tee "${OUTPUT_DIR}/qa.log"
)

# Run 2: Generative tasks (MT, SC, GC, MR). Need chat template and disable thinking.
echo ""
echo "=== Run 2/2: Sorbian generative tasks (sorbian_dev) ==="
(
    cd "${DATA_DIR}"
    python -m lm_eval run \
        --model hf \
        --model_args "pretrained=${MODEL_PATH},trust_remote_code=True,dtype=${DTYPE},enable_thinking=False" \
        --tasks sorbian_dev \
        --apply_chat_template \
        --batch_size "${BATCH_SIZE}" \
        --device "${DEVICE}" \
        --output_path "${OUTPUT_DIR}/gen" \
        --log_samples \
        2>&1 | tee "${OUTPUT_DIR}/gen.log"
)

echo ""
echo "=== Full baseline evaluation finished ==="
echo "Results written to: ${OUTPUT_DIR}"
