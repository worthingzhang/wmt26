#!/usr/bin/env bash
# Official WMT26 Sorbian zero-shot evaluation entry script.
#
# Usage:
#   bash scripts/eval/eval_official_sorbian.sh \
#     --model-tag <MODEL_TAG> \
#     --model-path <MODEL_PATH> \
#     --backend <hf|vllm> \
#     [--run-id <RUN_ID>] \
#     [--dry-run] \
#     [--help]
#
# This script evaluates any registered checkpoint (base / CPT / SFT / OPD) on the
# official WMT26 Sorbian zero-shot benchmark using the aligned official_eval
# backend. Only the HF backend is implemented in this round; vLLM is gated behind
# the future backend_compare stage.

set -euo pipefail

# ---------------------------------------------------------------------------
# Project constants
# ---------------------------------------------------------------------------
PROJECT_ROOT="/home/zc/wmt26"
DATA_DIR="${PROJECT_ROOT}/data/raw"
OFFICIAL_EVAL_DIR="${PROJECT_ROOT}/repos/official_eval"

EVAL_CODE_REPO="https://github.com/TUM-NLP/llms-lim-res-eval-2026"
EVAL_CODE_COMMIT="711a2b4f"
DATA_REPO="https://github.com/TUM-NLP/llms-limited-resources2026"
DATA_COMMIT="2b712ac6"

PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python3"
if [[ ! -f "${PYTHON_BIN}" ]]; then
    echo "Error: Python interpreter not found at ${PYTHON_BIN}" >&2
    echo "Please activate the main/eval environment (.venv) before running this script." >&2
    exit 1
fi
MODEL_FAMILY="Qwen3.5-2B"
EVAL_SETTING="official_zeroshot"
SHOT_SETTING="zero_shot"
DEVICE="cuda:0"
BATCH_SIZE="auto"
DTYPE="bfloat16"
GPU_SETTING="single_gpu"

# ---------------------------------------------------------------------------
# Load mirror/env configuration
# ---------------------------------------------------------------------------
if [[ -f "${PROJECT_ROOT}/configs/env/mirrors.env" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "${PROJECT_ROOT}/configs/env/mirrors.env"
    set +a
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
usage() {
    cat <<EOF
Usage: bash scripts/eval/eval_official_sorbian.sh [OPTIONS]

Official WMT26 Sorbian zero-shot evaluation entry.

Required:
  --model-tag  MODEL_TAG   Model tag from models/registry/models.jsonl
  --model-path PATH        Absolute path to the model directory
  --backend    BACKEND     Inference backend: hf (reference) or vllm (candidate)

Optional:
  --run-id     RUN_ID      Custom run ID. If omitted, auto-generated as:
                           eval_<model_tag>__official_zeroshot__<backend>_<YYYYMMDD_HHMMSS>
  --dry-run                Print the plan without running lm_eval or writing files.
  --help                   Show this help message.

Examples:
  bash scripts/eval/eval_official_sorbian.sh \\
    --model-tag base_qwen35_2b \\
    --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \\
    --backend hf \\
    --dry-run

  bash scripts/eval/eval_official_sorbian.sh \\
    --model-tag cpt_v1_official_plaintext_dsb4x_full \\
    --model-path /home/zc/wmt26/models/cpt/cpt_v1_official_plaintext_dsb4x_full \\
    --backend hf

Notes:
  - HF is the reference backend; vLLM is not implemented yet and will error.
  - QA tasks (hsbqa, dsbqa) run without --apply_chat_template.
  - Generative tasks (sorbian_dev) run with --apply_chat_template and enable_thinking=False.
  - Time stamps appear only in the run_id under runs/eval_official/..., never in reports/.
EOF
}

infer_checkpoint_type() {
    local tag="$1"
    case "${tag}" in
        base_*) echo "base" ;;
        cpt_*)  echo "cpt" ;;
        sft_*)  echo "sft" ;;
        opd_*)  echo "opd" ;;
        *)      echo "unknown" ;;
    esac
}

emit_qa_cmd() {
    cat <<EOF
python3 -m lm_eval run \\
  --model hf \\
  --model_args "pretrained=${MODEL_PATH_ABS},trust_remote_code=True" \\
  --tasks hsbqa,dsbqa \\
  --device ${DEVICE} \\
  --batch_size ${BATCH_SIZE} \\
  --output_path ${QA_OUTPUT} \\
  --log_samples
EOF
}

emit_gen_cmd() {
    cat <<EOF
python3 -m lm_eval run \\
  --model hf \\
  --model_args "pretrained=${MODEL_PATH_ABS},trust_remote_code=True,enable_thinking=False" \\
  --apply_chat_template \\
  --tasks sorbian_dev \\
  --device ${DEVICE} \\
  --batch_size ${BATCH_SIZE} \\
  --output_path ${GEN_OUTPUT} \\
  --log_samples
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
MODEL_TAG=""
MODEL_PATH=""
BACKEND="hf"
RUN_ID=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model-tag)
            MODEL_TAG="$2"
            shift 2
            ;;
        --model-path)
            MODEL_PATH="$2"
            shift 2
            ;;
        --backend)
            BACKEND="$2"
            shift 2
            ;;
        --run-id)
            RUN_ID="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: unknown argument: $1" >&2
            usage
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
if [[ -z "${MODEL_TAG}" ]]; then
    echo "Error: --model-tag is required." >&2
    usage
    exit 1
fi

if [[ -z "${MODEL_PATH}" ]]; then
    echo "Error: --model-path is required." >&2
    usage
    exit 1
fi

if [[ ! -d "${MODEL_PATH}" ]]; then
    echo "Error: model path does not exist: ${MODEL_PATH}" >&2
    exit 1
fi

case "${BACKEND}" in
    hf)
        BACKEND_ROLE="reference"
        OFFICIAL="true"
        ;;
    vllm)
        echo "Error: vLLM backend is not implemented yet; use the backend_compare stage later." >&2
        echo "See docs/eval/OFFICIAL_ZEROSHOT_RUNBOOK.md for backend roadmap." >&2
        exit 1
        ;;
    *)
        echo "Error: unsupported backend '${BACKEND}'. Choose 'hf' or 'vllm'." >&2
        usage
        exit 1
        ;;
esac

CHECKPOINT_TYPE="$(infer_checkpoint_type "${MODEL_TAG}")"
if [[ "${CHECKPOINT_TYPE}" == "unknown" ]]; then
    echo "Warning: could not infer checkpoint_type from model_tag '${MODEL_TAG}'." >&2
fi

MODEL_PATH_ABS="$(realpath "${MODEL_PATH}")"

if [[ -z "${RUN_ID}" ]]; then
    RUN_ID="eval_${MODEL_TAG}__official_zeroshot__${BACKEND}_$(date +%Y%m%d_%H%M%S)"
fi

RUN_DIR="${PROJECT_ROOT}/runs/eval_official/${MODEL_TAG}/official_zeroshot/${RUN_ID}"
REPORTS_DIR="${PROJECT_ROOT}/reports/eval_official/${MODEL_TAG}/official_zeroshot"
QA_OUTPUT="${RUN_DIR}/qa"
GEN_OUTPUT="${RUN_DIR}/gen"
GENERATED_AT="$(date -Iseconds)"

# Literal single-line commands for run.yaml metadata (not executed verbatim).
QA_CMD_LITERAL="${PYTHON_BIN} -m lm_eval run --model hf --model_args \"pretrained=${MODEL_PATH_ABS},trust_remote_code=True\" --tasks hsbqa,dsbqa --device ${DEVICE} --batch_size ${BATCH_SIZE} --output_path ${QA_OUTPUT} --log_samples"
GEN_CMD_LITERAL="${PYTHON_BIN} -m lm_eval run --model hf --model_args \"pretrained=${MODEL_PATH_ABS},trust_remote_code=True,enable_thinking=False\" --apply_chat_template --tasks sorbian_dev --device ${DEVICE} --batch_size ${BATCH_SIZE} --output_path ${GEN_OUTPUT} --log_samples"

# ---------------------------------------------------------------------------
# Dry-run: print plan and exit without side effects
# ---------------------------------------------------------------------------
if [[ "${DRY_RUN}" == true ]]; then
    echo "=== DRY RUN ==="
    echo "Model tag:        ${MODEL_TAG}"
    echo "Checkpoint type:  ${CHECKPOINT_TYPE}"
    echo "Model path:       ${MODEL_PATH_ABS}"
    echo "Backend:          ${BACKEND} (${BACKEND_ROLE})"
    echo "Official:         ${OFFICIAL}"
    echo "Run ID:           ${RUN_ID}"
    echo "Run dir:          ${RUN_DIR}"
    echo "Reports dir:      ${REPORTS_DIR}"
    echo ""
    echo "QA command:"
    emit_qa_cmd
    echo ""
    echo "Gen command:"
    emit_gen_cmd
    echo ""
    echo "run.yaml would be written to: ${RUN_DIR}/run.yaml"
    echo "commands/qa.sh would be written to: ${RUN_DIR}/commands/qa.sh"
    echo "commands/gen.sh would be written to: ${RUN_DIR}/commands/gen.sh"
    echo "No directories created, no files written, no lm_eval command executed."
    exit 0
fi

# ---------------------------------------------------------------------------
# Non-dry-run: prepare directories and metadata
# ---------------------------------------------------------------------------
echo "=== Official Sorbian zero-shot evaluation ==="
echo "Model tag:        ${MODEL_TAG}"
echo "Checkpoint type:  ${CHECKPOINT_TYPE}"
echo "Model path:       ${MODEL_PATH_ABS}"
echo "Backend:          ${BACKEND} (${BACKEND_ROLE})"
echo "Official:         ${OFFICIAL}"
echo "Run ID:           ${RUN_ID}"
echo "Run dir:          ${RUN_DIR}"
echo ""

mkdir -p "${RUN_DIR}"/qa
mkdir -p "${RUN_DIR}"/gen
mkdir -p "${RUN_DIR}"/logs
mkdir -p "${RUN_DIR}"/commands
mkdir -p "${RUN_DIR}"/status
mkdir -p "${REPORTS_DIR}/raw"

# ---------------------------------------------------------------------------
# Write executable command scripts
# ---------------------------------------------------------------------------
cat > "${RUN_DIR}/commands/qa.sh" <<EOF
#!/usr/bin/env bash
# Auto-generated QA command for ${MODEL_TAG} official zero-shot
set -euo pipefail

# RTX 4000 series multi-GPU setup: disable P2P/IB even when only cuda:0 is used,
# because accelerate initializes distributed state and detects all 8 GPUs.
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export CUDA_VISIBLE_DEVICES=0

# Run from data/raw so that official_eval can resolve
# llms-limited-resources2026/Sorbian/... via relative path.
cd "${DATA_DIR}"
${PYTHON_BIN} -m lm_eval run \\
  --model hf \\
  --model_args "pretrained=${MODEL_PATH_ABS},trust_remote_code=True" \\
  --tasks hsbqa,dsbqa \\
  --device ${DEVICE} \\
  --batch_size ${BATCH_SIZE} \\
  --output_path ${QA_OUTPUT} \\
  --log_samples 2>&1 | tee "${RUN_DIR}/logs/qa.log"
EOF

cat > "${RUN_DIR}/commands/gen.sh" <<EOF
#!/usr/bin/env bash
# Auto-generated generative command for ${MODEL_TAG} official zero-shot
set -euo pipefail

export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export CUDA_VISIBLE_DEVICES=0

cd "${DATA_DIR}"
${PYTHON_BIN} -m lm_eval run \\
  --model hf \\
  --model_args "pretrained=${MODEL_PATH_ABS},trust_remote_code=True,enable_thinking=False" \\
  --apply_chat_template \\
  --tasks sorbian_dev \\
  --device ${DEVICE} \\
  --batch_size ${BATCH_SIZE} \\
  --output_path ${GEN_OUTPUT} \\
  --log_samples 2>&1 | tee "${RUN_DIR}/logs/gen.log"
EOF

chmod +x "${RUN_DIR}/commands/qa.sh" "${RUN_DIR}/commands/gen.sh"

# ---------------------------------------------------------------------------
# Write reports/raw/README.md pointer
# ---------------------------------------------------------------------------
cat > "${REPORTS_DIR}/raw/README.md" <<EOF
# Raw run evidence

- model_tag: ${MODEL_TAG}
- backend: ${BACKEND}
- source_run_dir: ${RUN_DIR}
- generated_at: ${GENERATED_AT}

Raw lm-eval outputs (results_*.json, samples_*.jsonl, logs) remain in the source
run directory above and are not duplicated here. Aggregated human-readable results
will be produced by scripts/eval/aggregate_eval_results.py into this reports
branch.
EOF

# ---------------------------------------------------------------------------
# Write run.yaml metadata
# ---------------------------------------------------------------------------
cat > "${RUN_DIR}/run.yaml" <<EOF
model_tag: "${MODEL_TAG}"
model_path: "${MODEL_PATH_ABS}"
model_family: "${MODEL_FAMILY}"
checkpoint_type: "${CHECKPOINT_TYPE}"
eval_setting: "${EVAL_SETTING}"
shot_setting: "${SHOT_SETTING}"
backend: "${BACKEND}"
backend_role: "${BACKEND_ROLE}"
official: ${OFFICIAL}
eval_code_repo: "${EVAL_CODE_REPO}"
eval_code_commit: "${EVAL_CODE_COMMIT}"
data_repo: "${DATA_REPO}"
data_commit: "${DATA_COMMIT}"
tasks_qa:
  - "hsbqa"
  - "dsbqa"
tasks_gen:
  - "sorbian_dev"
apply_chat_template_for_gen: true
enable_thinking_for_gen: false
qa_uses_chat_template: false
batch_size: "${BATCH_SIZE}"
gpu_setting: "${GPU_SETTING}"
dtype: "${DTYPE}"
command_qa: '${QA_CMD_LITERAL}'
command_gen: '${GEN_CMD_LITERAL}'
source_run_dir: "${RUN_DIR}"
generated_at: "${GENERATED_AT}"
status: "running"
notes: "Official zero-shot Sorbian evaluation (HF reference backend) generated by scripts/eval/eval_official_sorbian.sh."
EOF

# ---------------------------------------------------------------------------
# Run lm_eval
# ---------------------------------------------------------------------------
echo "=== Running QA tasks ==="
if bash "${RUN_DIR}/commands/qa.sh"; then
    echo "0" > "${RUN_DIR}/status/qa.exit"
else
    echo "$?" > "${RUN_DIR}/status/qa.exit"
    echo "Error: QA run failed. Check ${RUN_DIR}/logs/qa.log" >&2
    exit 1
fi

echo "=== Running generative tasks ==="
if bash "${RUN_DIR}/commands/gen.sh"; then
    echo "0" > "${RUN_DIR}/status/gen.exit"
else
    echo "$?" > "${RUN_DIR}/status/gen.exit"
    echo "Error: generative run failed. Check ${RUN_DIR}/logs/gen.log" >&2
    exit 1
fi

# Mark completed
sed -i 's/^status: "running"/status: "completed"/' "${RUN_DIR}/run.yaml"

echo ""
echo "=== Evaluation complete ==="
echo "Run dir:     ${RUN_DIR}"
echo "Reports dir: ${REPORTS_DIR}"
echo "Next step:   bash scripts/eval/aggregate_eval_results.py --source-run-dir ${RUN_DIR} --standard-run-dir ${REPORTS_DIR}"
