#!/usr/bin/env bash
# Baseline smoke evaluation for base Qwen3.5-2B on a single Sorbian QA task.
# Uses lm_eval from repos/official_eval with --limit 5 to avoid a full run.

set -euo pipefail

# RTX 4000 series multi-GPU setup: disable NCCL P2P/IB to avoid accelerate error.
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1

PROJECT_ROOT="/home/zc/wmt26"
MODEL_PATH="${PROJECT_ROOT}/models/base/Qwen3.5-2B"
OUTPUT_DIR="${PROJECT_ROOT}/runs/eval/eval_base_qwen35_2b_smoke"
TASK="hsbqa"
LIMIT=5
BATCH_SIZE=1
DEVICE="cuda:0"
DTYPE="bfloat16"

echo "=== Baseline smoke evaluation ==="
echo "Project root : ${PROJECT_ROOT}"
echo "Model path   : ${MODEL_PATH}"
echo "Task         : ${TASK}"
echo "Limit        : ${LIMIT}"
echo "Batch size   : ${BATCH_SIZE}"
echo "Device       : ${DEVICE}"
echo "Dtype        : ${DTYPE}"
echo "Output dir   : ${OUTPUT_DIR}"

cd "${PROJECT_ROOT}"

# Activate main/eval environment
source "${PROJECT_ROOT}/.venv/bin/activate"

which python
python --version
python -c "import lm_eval; print('lm_eval:', lm_eval.__version__)"

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

# Run a minimal smoke evaluation. Qwen3.5-2B uses a custom architecture,
# so trust_remote_code=True is required.
(
    cd "${DATA_DIR}"
    python -m lm_eval run \
        --model hf \
        --model_args "pretrained=${MODEL_PATH},trust_remote_code=True,dtype=${DTYPE}" \
        --tasks "${TASK}" \
        --limit "${LIMIT}" \
        --batch_size "${BATCH_SIZE}" \
        --device "${DEVICE}" \
        --output_path "${OUTPUT_DIR}" \
        --log_samples \
        2>&1 | tee "${OUTPUT_DIR}/eval.log"
)

echo "=== Smoke evaluation finished ==="
echo "Results written to: ${OUTPUT_DIR}"
