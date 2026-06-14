#!/usr/bin/env bash
# Train SFT (supervised fine-tuning) using LlamaFactory in thunlp_opd.
# Usage:
#   bash scripts/train/train_sft.sh \
#     --run-id sft_smoke_from_base_v1 \
#     --input-model /home/zc/wmt26/models/base/Qwen3.5-2B \
#     --data-config configs/data/sft_mix_v1.yaml \
#     --train-config configs/train/sft/sft_smoke.yaml \
#     --output-model /home/zc/wmt26/models/checkpoints/sft/sft_smoke_from_base_v1 \
#     --model-id sft_smoke_from_base_v1

set -euo pipefail
# Load mirror/env configuration
set -a
source "/home/zc/wmt26/configs/env/mirrors.env"
set +a


PROJECT_ROOT="/home/zc/wmt26"
LLAMAFACTORY_DIR="${PROJECT_ROOT}/repos/thunlp_opd/LlamaFactory"
REGISTER_MODEL_PY="${PROJECT_ROOT}/scripts/utils/register_model.py"
TRAIN_REGISTRY="${PROJECT_ROOT}/runs/train_registry.csv"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Train SFT (supervised fine-tuning) with LlamaFactory.

Required:
  --run-id ID                  Unique run ID.
  --input-model PATH           Path to input model (base or any checkpoint).
  --data-config PATH           Path to data config YAML.
  --train-config PATH          Path to LlamaFactory training config YAML.
  --output-model PATH          Path to save output model.
  --model-id ID                Model ID for registry.

Optional:
  --deepspeed PATH             Path to DeepSpeed config (optional).
  --dry-run                    Print commands without executing.
  -h, --help                   Show this help message.
EOF
}

RUN_ID=""
INPUT_MODEL=""
DATA_CONFIG=""
TRAIN_CONFIG=""
OUTPUT_MODEL=""
MODEL_ID=""
DEEPSPEED=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --run-id) RUN_ID="$2"; shift 2 ;;
        --input-model) INPUT_MODEL="$2"; shift 2 ;;
        --data-config) DATA_CONFIG="$2"; shift 2 ;;
        --train-config) TRAIN_CONFIG="$2"; shift 2 ;;
        --output-model) OUTPUT_MODEL="$2"; shift 2 ;;
        --model-id) MODEL_ID="$2"; shift 2 ;;
        --deepspeed) DEEPSPEED="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1"; usage; exit 1 ;;
    esac
done

if [[ -z "${RUN_ID}" || -z "${INPUT_MODEL}" || -z "${DATA_CONFIG}" || -z "${TRAIN_CONFIG}" || -z "${OUTPUT_MODEL}" || -z "${MODEL_ID}" ]]; then
    echo "Error: Missing required arguments."
    usage
    exit 1
fi

if [[ ! -d "${INPUT_MODEL}" ]]; then
    echo "Error: Input model directory does not exist: ${INPUT_MODEL}"
    exit 1
fi
if [[ ! -f "${PROJECT_ROOT}/${DATA_CONFIG}" && ! -f "${DATA_CONFIG}" ]]; then
    echo "Error: Data config not found: ${DATA_CONFIG}"
    exit 1
fi
if [[ ! -f "${PROJECT_ROOT}/${TRAIN_CONFIG}" && ! -f "${TRAIN_CONFIG}" ]]; then
    echo "Error: Train config not found: ${TRAIN_CONFIG}"
    exit 1
fi
if [[ ! -d "${LLAMAFACTORY_DIR}" ]]; then
    echo "Error: LlamaFactory directory does not exist: ${LLAMAFACTORY_DIR}"
    exit 1
fi

DATA_CONFIG_ABS="$(cd "${PROJECT_ROOT}" && realpath "${DATA_CONFIG}" 2>/dev/null || realpath "${DATA_CONFIG}")"
TRAIN_CONFIG_ABS="$(cd "${PROJECT_ROOT}" && realpath "${TRAIN_CONFIG}" 2>/dev/null || realpath "${TRAIN_CONFIG}")"
INPUT_MODEL_ABS="$(realpath "${INPUT_MODEL}")"
OUTPUT_MODEL_ABS="$(realpath -m "${OUTPUT_MODEL}")"
RUN_DIR="${PROJECT_ROOT}/runs/train/${RUN_ID}"
LOG_FILE="${RUN_DIR}/train.log"

mkdir -p "${RUN_DIR}"
mkdir -p "$(dirname "${OUTPUT_MODEL_ABS}")"

cp "${DATA_CONFIG_ABS}" "${RUN_DIR}/data_config.yaml"
cp "${TRAIN_CONFIG_ABS}" "${RUN_DIR}/train_config.yaml"

TMP_CONFIG="${RUN_DIR}/llamafactory_config.yaml"
sed -e "s|PLACEHOLDER|${INPUT_MODEL_ABS}|g" \
    -e "s|model_name_or_path: PLACEHOLDER|model_name_or_path: ${INPUT_MODEL_ABS}|g" \
    -e "s|output_dir: PLACEHOLDER|output_dir: ${OUTPUT_MODEL_ABS}|g" \
    "${TRAIN_CONFIG_ABS}" > "${TMP_CONFIG}"

if [[ -n "${DEEPSPEED}" ]]; then
    sed -i "s|deepspeed: PLACEHOLDER|deepspeed: ${DEEPSPEED}|g" "${TMP_CONFIG}"
else
    sed -i "/deepspeed: PLACEHOLDER/d" "${TMP_CONFIG}"
fi

echo "=== SFT Training ==="
echo "Run ID       : ${RUN_ID}"
echo "Input model  : ${INPUT_MODEL_ABS}"
echo "Output model : ${OUTPUT_MODEL_ABS}"
echo "Train config : ${TMP_CONFIG}"
echo "Log file     : ${LOG_FILE}"

if [[ "${DRY_RUN}" == true ]]; then
    echo "[DRY RUN] Would run:"
    echo "cd ${LLAMAFACTORY_DIR} && llamafactory-cli train ${TMP_CONFIG}"
    exit 0
fi

mkdir -p "${PROJECT_ROOT}/runs"
if [[ ! -f "${TRAIN_REGISTRY}" ]]; then
    echo "run_id,train_type,input_model,teacher_model,output_model,data_config,train_config,log_dir,status,notes" > "${TRAIN_REGISTRY}"
fi
echo "${RUN_ID},sft,${INPUT_MODEL_ABS},,${OUTPUT_MODEL_ABS},${DATA_CONFIG_ABS},${TRAIN_CONFIG_ABS},${RUN_DIR},running,started at $(date -Iseconds)" >> "${TRAIN_REGISTRY}"

cd "${LLAMAFACTORY_DIR}"
if command -v llamafactory-cli >/dev/null 2>&1; then
    llamafactory-cli train "${TMP_CONFIG}" 2>&1 | tee "${LOG_FILE}"
elif [[ -f "${LLAMAFACTORY_DIR}/src/llamafactory/cli.py" ]]; then
    python "${LLAMAFACTORY_DIR}/src/llamafactory/cli.py" train "${TMP_CONFIG}" 2>&1 | tee "${LOG_FILE}"
else
    echo "Error: llamafactory-cli not found in ${LLAMAFACTORY_DIR}"
    exit 1
fi

TRAIN_STATUS=$?
if [[ ${TRAIN_STATUS} -eq 0 ]]; then
    STATUS="completed"
else
    STATUS="failed"
fi

if [[ ${TRAIN_STATUS} -eq 0 && -d "${OUTPUT_MODEL_ABS}" ]]; then
    python "${REGISTER_MODEL_PY}" \
        --model-id "${MODEL_ID}" \
        --model-path "${OUTPUT_MODEL_ABS}" \
        --training-type "sft" \
        --input-model "${INPUT_MODEL_ABS}" \
        --data-config "${DATA_CONFIG_ABS}" \
        --train-config "${TRAIN_CONFIG_ABS}" \
        --notes "SFT run ${RUN_ID}"
fi

echo "${RUN_ID},sft,${INPUT_MODEL_ABS},,${OUTPUT_MODEL_ABS},${DATA_CONFIG_ABS},${TRAIN_CONFIG_ABS},${RUN_DIR},${STATUS},finished at $(date -Iseconds)" >> "${TRAIN_REGISTRY}"

echo "SFT training finished with status: ${STATUS}"
exit ${TRAIN_STATUS}
