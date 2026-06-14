#!/usr/bin/env bash
# Evaluate any model using the official evaluation backend.
# Usage:
#   bash scripts/eval/eval_model.sh \
#     --eval-id eval_base_qwen35_2b_v1 \
#     --model-id base_qwen35_2b \
#     --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \
#     --eval-config configs/eval/official_all_tasks.yaml \
#     --output-dir /home/zc/wmt26/runs/eval/eval_base_qwen35_2b_v1

set -euo pipefail
# Load mirror/env configuration
set -a
source "/home/zc/wmt26/configs/env/mirrors.env"
set +a


PROJECT_ROOT="/home/zc/wmt26"
OFFICIAL_EVAL_DIR="${PROJECT_ROOT}/repos/official_eval"
REGISTER_EVAL_PY="${PROJECT_ROOT}/scripts/utils/register_eval.py"
EVAL_REGISTRY="${PROJECT_ROOT}/runs/eval_registry.csv"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Evaluate any model with the official evaluation backend.

Required:
  --eval-id ID                 Unique evaluation run ID.
  --model-id ID                Model ID (as registered).
  --model-path PATH            Path to model directory.
  --eval-config PATH           Path to eval config YAML.
  --output-dir PATH            Directory to save evaluation results.

Optional:
  --dry-run                    Print commands without executing.
  -h, --help                   Show this help message.
EOF
}

EVAL_ID=""
MODEL_ID=""
MODEL_PATH=""
EVAL_CONFIG=""
OUTPUT_DIR=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --eval-id) EVAL_ID="$2"; shift 2 ;;
        --model-id) MODEL_ID="$2"; shift 2 ;;
        --model-path) MODEL_PATH="$2"; shift 2 ;;
        --eval-config) EVAL_CONFIG="$2"; shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1"; usage; exit 1 ;;
    esac
done

if [[ -z "${EVAL_ID}" || -z "${MODEL_ID}" || -z "${MODEL_PATH}" || -z "${EVAL_CONFIG}" || -z "${OUTPUT_DIR}" ]]; then
    echo "Error: Missing required arguments."
    usage
    exit 1
fi

if [[ ! -d "${MODEL_PATH}" ]]; then
    echo "Error: Model directory does not exist: ${MODEL_PATH}"
    exit 1
fi
if [[ ! -f "${PROJECT_ROOT}/${EVAL_CONFIG}" && ! -f "${EVAL_CONFIG}" ]]; then
    echo "Error: Eval config not found: ${EVAL_CONFIG}"
    exit 1
fi
if [[ ! -d "${OFFICIAL_EVAL_DIR}" ]]; then
    echo "Error: official_eval directory does not exist: ${OFFICIAL_EVAL_DIR}"
    echo "Please clone official_eval repo first."
    exit 1
fi

EVAL_CONFIG_ABS="$(cd "${PROJECT_ROOT}" && realpath "${EVAL_CONFIG}" 2>/dev/null || realpath "${EVAL_CONFIG}")"
MODEL_PATH_ABS="$(realpath "${MODEL_PATH}")"
OUTPUT_DIR_ABS="$(realpath -m "${OUTPUT_DIR}")"
LOG_FILE="${OUTPUT_DIR_ABS}/eval.log"
RESULT_FILE="${OUTPUT_DIR_ABS}/results.json"

mkdir -p "${OUTPUT_DIR_ABS}"
cp "${EVAL_CONFIG_ABS}" "${OUTPUT_DIR_ABS}/eval_config.yaml"

# Build temporary eval config with placeholders replaced
TMP_EVAL_CONFIG="${OUTPUT_DIR_ABS}/eval_config_resolved.yaml"
sed -e "s|PLACEHOLDER|${MODEL_PATH_ABS}|g" \
    -e "s|model_path: PLACEHOLDER|model_path: ${MODEL_PATH_ABS}|g" \
    -e "s|output_dir: PLACEHOLDER|output_dir: ${OUTPUT_DIR_ABS}|g" \
    "${EVAL_CONFIG_ABS}" > "${TMP_EVAL_CONFIG}"

echo "=== Model Evaluation ==="
echo "Eval ID      : ${EVAL_ID}"
echo "Model ID     : ${MODEL_ID}"
echo "Model path   : ${MODEL_PATH_ABS}"
echo "Eval config  : ${TMP_EVAL_CONFIG}"
echo "Output dir   : ${OUTPUT_DIR_ABS}"
echo "Log file     : ${LOG_FILE}"

if [[ "${DRY_RUN}" == true ]]; then
    echo "[DRY RUN] Would run official evaluation from ${OFFICIAL_EVAL_DIR}"
    cat "${TMP_EVAL_CONFIG}"
    exit 0
fi

mkdir -p "${PROJECT_ROOT}/runs"
if [[ ! -f "${EVAL_REGISTRY}" ]]; then
    echo "eval_id,model_id,model_path,eval_config,result_path,status,notes" > "${EVAL_REGISTRY}"
fi
echo "${EVAL_ID},${MODEL_ID},${MODEL_PATH_ABS},${EVAL_CONFIG_ABS},${RESULT_FILE},running,started at $(date -Iseconds)" >> "${EVAL_REGISTRY}"

# TODO: replace with actual official evaluation launch command.
# Placeholder: create empty results.json so skeleton downstream works.
cd "${OFFICIAL_EVAL_DIR}"
if [[ -f "${OFFICIAL_EVAL_DIR}/eval.py" ]]; then
    python "${OFFICIAL_EVAL_DIR}/eval.py" --config "${TMP_EVAL_CONFIG}" 2>&1 | tee "${LOG_FILE}"
else
    echo "Warning: official_eval eval.py not found at ${OFFICIAL_EVAL_DIR}/eval.py"
    echo "This is a skeleton. Please update scripts/eval/eval_model.sh after confirming official_eval launch command."
    echo "Creating placeholder results.json"
    echo '{"mt": null, "qa": null, "sc": null, "gc": null, "mr": null, "note": "placeholder"}' > "${RESULT_FILE}"
fi

EVAL_STATUS=$?
if [[ ${EVAL_STATUS} -eq 0 ]]; then
    STATUS="completed"
else
    STATUS="failed"
fi

# Register eval result
python "${REGISTER_EVAL_PY}" \
    --eval-id "${EVAL_ID}" \
    --model-id "${MODEL_ID}" \
    --model-path "${MODEL_PATH_ABS}" \
    --eval-config "${EVAL_CONFIG_ABS}" \
    --result-path "${RESULT_FILE}" \
    --status "${STATUS}" \
    --notes "Eval run ${EVAL_ID}"

echo "${EVAL_ID},${MODEL_ID},${MODEL_PATH_ABS},${EVAL_CONFIG_ABS},${RESULT_FILE},${STATUS},finished at $(date -Iseconds)" >> "${EVAL_REGISTRY}"

echo "Evaluation finished with status: ${STATUS}"
exit ${EVAL_STATUS}
