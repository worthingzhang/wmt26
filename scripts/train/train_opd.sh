#!/usr/bin/env bash
# Train OPD (on-policy distillation) using thunlp_opd OPD/verl training backend.
# Usage:
#   bash scripts/train/train_opd.sh \
#     --run-id opd_smoke_sft_mt_teacher_v1 \
#     --student-model /home/zc/wmt26/models/checkpoints/sft/sft_smoke_from_base_v1 \
#     --teacher-model /home/zc/wmt26/models/teachers/mt_teacher_v1 \
#     --prompt-config configs/data/opd_prompt_mix_v1.yaml \
#     --train-config configs/train/opd/opd_smoke.env \
#     --output-model /home/zc/wmt26/models/checkpoints/opd/opd_smoke_sft_mt_teacher_v1 \
#     --model-id opd_smoke_sft_mt_teacher_v1

set -euo pipefail

PROJECT_ROOT="/home/zc/wmt26"
THUNLP_OPD_DIR="${PROJECT_ROOT}/repos/thunlp_opd"
REGISTER_MODEL_PY="${PROJECT_ROOT}/scripts/utils/register_model.py"
TRAIN_REGISTRY="${PROJECT_ROOT}/runs/train_registry.csv"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Train OPD (on-policy distillation).

Required:
  --run-id ID                  Unique run ID.
  --student-model PATH         Path to student model.
  --teacher-model PATH         Path to teacher model.
  --prompt-config PATH         Path to prompt config YAML.
  --train-config PATH          Path to OPD training env/config.
  --output-model PATH          Path to save output model.
  --model-id ID                Model ID for registry.

Optional:
  --prompt-path PATH           Override prompt data path (jsonl/parquet).
  --dry-run                    Print commands without executing.
  -h, --help                   Show this help message.
EOF
}

RUN_ID=""
STUDENT_MODEL=""
TEACHER_MODEL=""
PROMPT_CONFIG=""
TRAIN_CONFIG=""
OUTPUT_MODEL=""
MODEL_ID=""
PROMPT_PATH=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --run-id) RUN_ID="$2"; shift 2 ;;
        --student-model) STUDENT_MODEL="$2"; shift 2 ;;
        --teacher-model) TEACHER_MODEL="$2"; shift 2 ;;
        --prompt-config) PROMPT_CONFIG="$2"; shift 2 ;;
        --train-config) TRAIN_CONFIG="$2"; shift 2 ;;
        --output-model) OUTPUT_MODEL="$2"; shift 2 ;;
        --model-id) MODEL_ID="$2"; shift 2 ;;
        --prompt-path) PROMPT_PATH="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1"; usage; exit 1 ;;
    esac
done

if [[ -z "${RUN_ID}" || -z "${STUDENT_MODEL}" || -z "${TEACHER_MODEL}" || -z "${PROMPT_CONFIG}" || -z "${TRAIN_CONFIG}" || -z "${OUTPUT_MODEL}" || -z "${MODEL_ID}" ]]; then
    echo "Error: Missing required arguments."
    usage
    exit 1
fi

if [[ ! -d "${STUDENT_MODEL}" ]]; then
    echo "Error: Student model directory does not exist: ${STUDENT_MODEL}"
    exit 1
fi
if [[ ! -d "${TEACHER_MODEL}" ]]; then
    echo "Error: Teacher model directory does not exist: ${TEACHER_MODEL}"
    exit 1
fi
if [[ ! -f "${PROJECT_ROOT}/${PROMPT_CONFIG}" && ! -f "${PROMPT_CONFIG}" ]]; then
    echo "Error: Prompt config not found: ${PROMPT_CONFIG}"
    exit 1
fi
if [[ ! -f "${PROJECT_ROOT}/${TRAIN_CONFIG}" && ! -f "${TRAIN_CONFIG}" ]]; then
    echo "Error: Train config not found: ${TRAIN_CONFIG}"
    exit 1
fi
if [[ ! -d "${THUNLP_OPD_DIR}" ]]; then
    echo "Error: thunlp_opd directory does not exist: ${THUNLP_OPD_DIR}"
    exit 1
fi

PROMPT_CONFIG_ABS="$(cd "${PROJECT_ROOT}" && realpath "${PROMPT_CONFIG}" 2>/dev/null || realpath "${PROMPT_CONFIG}")"
TRAIN_CONFIG_ABS="$(cd "${PROJECT_ROOT}" && realpath "${TRAIN_CONFIG}" 2>/dev/null || realpath "${TRAIN_CONFIG}")"
STUDENT_MODEL_ABS="$(realpath "${STUDENT_MODEL}")"
TEACHER_MODEL_ABS="$(realpath "${TEACHER_MODEL}")"
OUTPUT_MODEL_ABS="$(realpath -m "${OUTPUT_MODEL}")"
RUN_DIR="${PROJECT_ROOT}/runs/train/${RUN_ID}"
LOG_FILE="${RUN_DIR}/train.log"

mkdir -p "${RUN_DIR}"
mkdir -p "$(dirname "${OUTPUT_MODEL_ABS}")"

cp "${PROMPT_CONFIG_ABS}" "${RUN_DIR}/prompt_config.yaml"
cp "${TRAIN_CONFIG_ABS}" "${RUN_DIR}/train_config.env"

# Resolve prompt path if not overridden
if [[ -z "${PROMPT_PATH}" ]]; then
    # Try to infer from prompt config output_dir/output_name
    PROMPT_DIR="${PROJECT_ROOT}/data/processed/opd_prompts"
    PROMPT_NAME="opd_prompt_mix_v1.jsonl"
    PROMPT_PATH="${PROMPT_DIR}/${PROMPT_NAME}"
fi
PROMPT_PATH_ABS="$(realpath -m "${PROMPT_PATH}")"
if [[ ! -f "${PROMPT_PATH_ABS}" ]]; then
    echo "Warning: Prompt file does not exist yet: ${PROMPT_PATH_ABS}"
    echo "Please run scripts/data/build_opd_prompts.py first."
fi

# Prepare env file with placeholders replaced
TMP_ENV="${RUN_DIR}/opd_config.env"
cp "${TRAIN_CONFIG_ABS}" "${TMP_ENV}"
sed -i \
    -e "s|OPD_STUDENT_MODEL_PATH=PLACEHOLDER|OPD_STUDENT_MODEL_PATH=${STUDENT_MODEL_ABS}|g" \
    -e "s|OPD_TEACHER_MODEL_PATH=PLACEHOLDER|OPD_TEACHER_MODEL_PATH=${TEACHER_MODEL_ABS}|g" \
    -e "s|OPD_PROMPT_PATH=PLACEHOLDER|OPD_PROMPT_PATH=${PROMPT_PATH_ABS}|g" \
    -e "s|OPD_OUTPUT_DIR=PLACEHOLDER|OPD_OUTPUT_DIR=${OUTPUT_MODEL_ABS}|g" \
    -e "s|OPD_LOG_DIR=PLACEHOLDER|OPD_LOG_DIR=${RUN_DIR}|g" \
    "${TMP_ENV}"

echo "=== OPD Training ==="
echo "Run ID        : ${RUN_ID}"
echo "Student model : ${STUDENT_MODEL_ABS}"
echo "Teacher model : ${TEACHER_MODEL_ABS}"
echo "Prompt path   : ${PROMPT_PATH_ABS}"
echo "Output model  : ${OUTPUT_MODEL_ABS}"
echo "Train config  : ${TMP_ENV}"
echo "Log file      : ${LOG_FILE}"

if [[ "${DRY_RUN}" == true ]]; then
    echo "[DRY RUN] Would run OPD training with env from ${TMP_ENV}"
    cat "${TMP_ENV}"
    exit 0
fi

mkdir -p "${PROJECT_ROOT}/runs"
if [[ ! -f "${TRAIN_REGISTRY}" ]]; then
    echo "run_id,train_type,input_model,teacher_model,output_model,data_config,train_config,log_dir,status,notes" > "${TRAIN_REGISTRY}"
fi
echo "${RUN_ID},opd,${STUDENT_MODEL_ABS},${TEACHER_MODEL_ABS},${OUTPUT_MODEL_ABS},${PROMPT_CONFIG_ABS},${TRAIN_CONFIG_ABS},${RUN_DIR},running,started at $(date -Iseconds)" >> "${TRAIN_REGISTRY}"

# TODO: replace with actual OPD/verl launch command once thunlp_opd interface is confirmed.
# The command below is a placeholder that sources the env and calls a hypothetical trainer.
cd "${THUNLP_OPD_DIR}"
set -a
source "${TMP_ENV}"
set +a

OPD_TRAINER_SCRIPT="${THUNLP_OPD_DIR}/scripts/train_opd.sh"
if [[ -f "${OPD_TRAINER_SCRIPT}" ]]; then
    bash "${OPD_TRAINER_SCRIPT}" 2>&1 | tee "${LOG_FILE}"
else
    echo "Warning: OPD trainer script not found at ${OPD_TRAINER_SCRIPT}"
    echo "This is a skeleton. Please update scripts/train/train_opd.sh after confirming thunlp_opd OPD launch command."
    echo "Env file is ready at ${TMP_ENV}"
    # Do not fail in skeleton mode; mark as failed in registry but exit 0 so setup can continue.
    TRAIN_STATUS=1
fi

if [[ ${TRAIN_STATUS:-0} -eq 0 ]]; then
    STATUS="completed"
else
    STATUS="failed"
fi

if [[ ${TRAIN_STATUS:-0} -eq 0 && -d "${OUTPUT_MODEL_ABS}" ]]; then
    python "${REGISTER_MODEL_PY}" \
        --model-id "${MODEL_ID}" \
        --model-path "${OUTPUT_MODEL_ABS}" \
        --training-type "opd" \
        --input-model "${STUDENT_MODEL_ABS}" \
        --teacher-model "${TEACHER_MODEL_ABS}" \
        --data-config "${PROMPT_CONFIG_ABS}" \
        --train-config "${TRAIN_CONFIG_ABS}" \
        --notes "OPD run ${RUN_ID}"
fi

echo "${RUN_ID},opd,${STUDENT_MODEL_ABS},${TEACHER_MODEL_ABS},${OUTPUT_MODEL_ABS},${PROMPT_CONFIG_ABS},${TRAIN_CONFIG_ABS},${RUN_DIR},${STATUS},finished at $(date -Iseconds)" >> "${TRAIN_REGISTRY}"

echo "OPD training finished with status: ${STATUS}"
exit ${TRAIN_STATUS:-0}
