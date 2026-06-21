#!/usr/bin/env bash
# Evaluate a model on WMT26 Sorbian devsplit few-shot profiles.
# Usage:
#   bash scripts/eval/eval_wmt26_sorbian.sh MODEL_PATH devsplit_fewshot_v1 [--debug]
#   bash scripts/eval/eval_wmt26_sorbian.sh MODEL_PATH devsplit_fewshot_v2 [--debug]

set -euo pipefail

PROJECT_ROOT="/home/zc/wmt26"
OFFICIAL_EVAL_DIR="${PROJECT_ROOT}/repos/official_eval"
EVAL_REGISTRY="${PROJECT_ROOT}/runs/eval_registry.csv"

if [[ $# -lt 2 ]]; then
    echo "Usage: $(basename "$0") MODEL_PATH PROFILE [OPTIONS]"
    echo "  PROFILE: devsplit_fewshot_v1 | devsplit_fewshot_v2"
    echo "  OPTIONS: --debug (adds --limit 3 --write_out)"
    exit 1
fi

MODEL_PATH="$1"
PROFILE="$2"
shift 2

if [[ "${PROFILE}" != "devsplit_fewshot_v1" && "${PROFILE}" != "devsplit_fewshot_v2" ]]; then
    echo "Error: unsupported profile: ${PROFILE}"
    exit 1
fi

TASKS_DIR="${PROJECT_ROOT}/configs/eval/tasks/wmt26_sorbian_${PROFILE}"
DEVSPLIT_DIR="${PROJECT_ROOT}/configs/eval/devsplits/sorbian_${PROFILE}"
TASKS_GROUP="wmt26_sorbian_${PROFILE}"

DEBUG=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --debug) DEBUG=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ ! -d "${MODEL_PATH}" ]]; then
    echo "Error: model path does not exist: ${MODEL_PATH}"
    exit 1
fi

MODEL_NAME="$(basename "${MODEL_PATH}")"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
EVAL_ID="${MODEL_NAME}_${PROFILE}_${TIMESTAMP}"
OUTPUT_DIR="${PROJECT_ROOT}/runs/eval/${MODEL_NAME}/${PROFILE}/${TIMESTAMP}"
mkdir -p "${OUTPUT_DIR}"

# Environment
source "${PROJECT_ROOT}/configs/env/mirrors.env"
source "${PROJECT_ROOT}/.venv/bin/activate"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1

BATCH_SIZE=1
DTYPE="bfloat16"
DEVICE="cuda:0"

EXTRA_ARGS=(--log_samples)
if [[ "${DEBUG}" == true ]]; then
    EXTRA_ARGS+=(--limit 3 --write_out)
fi

COMMAND=(
    python -m lm_eval run
    --model hf
    --model_args "pretrained=${MODEL_PATH},trust_remote_code=True,dtype=${DTYPE},enable_thinking=False"
    --include_path "${TASKS_DIR}"
    --tasks "${TASKS_GROUP}"
    --apply_chat_template
    --batch_size "${BATCH_SIZE}"
    --device "${DEVICE}"
    --output_path "${OUTPUT_DIR}"
    "${EXTRA_ARGS[@]}"
)

# Save command as a reproducible shell command
cat > "${OUTPUT_DIR}/command.txt" <<EOF
#!/usr/bin/env bash
# Reproducible command for eval run ${EVAL_ID}
cd "${OFFICIAL_EVAL_DIR}"
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
$(printf '%q ' "${COMMAND[@]}")
EOF

# Save manifest
python3 -c '
import json, sys
from pathlib import Path
manifest = {
    "eval_id": sys.argv[1],
    "model_id": sys.argv[2],
    "model_path": sys.argv[3],
    "profile": sys.argv[4],
    "debug": sys.argv[5].lower() == "true",
    "timestamp": sys.argv[6],
    "output_dir": sys.argv[7],
    "tasks_group": sys.argv[8],
    "tasks_group_config": sys.argv[9],
}
Path(sys.argv[10]).write_text(json.dumps(manifest, indent=2) + "\n")
' "${EVAL_ID}" "${MODEL_NAME}" "${MODEL_PATH}" "${PROFILE}" "${DEBUG}" "${TIMESTAMP}" "${OUTPUT_DIR}" "${TASKS_GROUP}" "${TASKS_DIR}/group.yaml" "${OUTPUT_DIR}/manifest.json"

# Save fewshot split manifest
cp "${DEVSPLIT_DIR}/manifest.json" "${OUTPUT_DIR}/fewshot_split_manifest.json"

# Save fewshot sha256 summary
python3 -c '
import json, sys
from pathlib import Path
manifest = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2])
lines = []
for t in manifest["tasks"]:
    task = t["task"]
    shots = t["shots_sha256"]
    evalsha = t["eval_sha256"]
    lines.append(f"{task} shots={shots} eval={evalsha}")
out.write_text("\n".join(lines) + "\n")
' "${DEVSPLIT_DIR}/manifest.json" "${OUTPUT_DIR}/fewshot_sha256.txt"

# Git state: official_eval repo
cd "${OFFICIAL_EVAL_DIR}"
{
    echo "official_eval repo: ${OFFICIAL_EVAL_DIR}"
    git rev-parse HEAD
    echo "---"
    git status --short
} > "${OUTPUT_DIR}/official_eval_git.txt"

# Git state: overlay task directory
cd "${PROJECT_ROOT}"
{
    echo "overlay tasks dir: ${TASKS_DIR}"
    git rev-parse HEAD
    echo "---"
    git diff -- "${TASKS_DIR}" || true
} > "${OUTPUT_DIR}/overlay_task_git_or_diff.txt"

# Run eval
cd "${OFFICIAL_EVAL_DIR}"
"${COMMAND[@]}" 2>&1 | tee "${OUTPUT_DIR}/run.log"
EVAL_STATUS=${PIPESTATUS[0]}

# Determine status
if [[ ${EVAL_STATUS} -eq 0 ]]; then
    STATUS="completed"
else
    STATUS="failed"
fi
RESULT_FILE="$(find "${OUTPUT_DIR}" -type f -name 'results_*.json' | sort | tail -n 1)"
if [[ -z "${RESULT_FILE}" ]]; then
    RESULT_FILE="${OUTPUT_DIR}/results.json"
fi

# Register the run
python3 "${PROJECT_ROOT}/scripts/utils/register_eval.py" \
    --eval-id "${EVAL_ID}" \
    --model-id "${MODEL_NAME}" \
    --model-path "${MODEL_PATH}" \
    --eval-config "${TASKS_DIR}/group.yaml" \
    --result-path "${RESULT_FILE}" \
    --status "${STATUS}" \
    --notes "profile=${PROFILE} debug=${DEBUG}"

# Debug log assertions
if [[ "${DEBUG}" == true ]]; then
    if grep -q "using test_docs as fewshot_docs" "${OUTPUT_DIR}/run.log"; then
        echo "ERROR: found 'using test_docs as fewshot_docs' in run.log"
        exit 1
    fi
    if grep -q "Overwriting default num_fewshot" "${OUTPUT_DIR}/run.log"; then
        echo "ERROR: found 'Overwriting default num_fewshot' in run.log"
        exit 1
    fi
    echo "Debug log assertions passed."
fi

echo "Evaluation finished with status: ${STATUS}"
exit ${EVAL_STATUS}
