#!/usr/bin/env bash
# HF vs vLLM backend_compare for WMT26 Sorbian zero-shot.
#
# EXPERIMENTAL: results go under runs/eval_experimental/backend_compare/ and
# reports/eval_experimental/backend_compare/, NEVER under reports/eval_official/.

set -euo pipefail

PROJECT_ROOT="/home/zc/wmt26"
DATA_DIR="${PROJECT_ROOT}/data/raw"
OFFICIAL_EVAL_DIR="${PROJECT_ROOT}/repos/official_eval"

HF_PYTHON="${PROJECT_ROOT}/.venv/bin/python3"
VLLM_PYTHON="${PROJECT_ROOT}/.venvs/eval-vllm/bin/python3"

EVAL_CODE_REPO="https://github.com/TUM-NLP/llms-lim-res-eval-2026"
EVAL_CODE_COMMIT="711a2b4f"
DATA_REPO="https://github.com/TUM-NLP/llms-limited-resources2026"
DATA_COMMIT="2b712ac6"

LIMIT=100
GPU_ID=1

usage() {
    cat <<EOF
Usage: bash scripts/eval/compare_hf_vllm_backend.sh [OPTIONS]

Run a limited HF vs vLLM backend comparison for the WMT26 Sorbian zero-shot benchmark.

Required:
  --model-tag  MODEL_TAG   Model tag (e.g. base_qwen35_2b)
  --model-path PATH        Absolute path to the model directory

Optional:
  --limit N                Number of samples per task (default: 100)
  --gpu-id ID              Physical GPU to use for both HF and vLLM (default: 1)
  --run-id RUN_ID          Custom run ID; default: compare_<model_tag>_<YYYYMMDD_HHMMSS>
  --help                   Show this help

Example:
  bash scripts/eval/compare_hf_vllm_backend.sh \\
    --model-tag base_qwen35_2b \\
    --model-path /home/zc/wmt26/models/base/Qwen3.5-2B \\
    --limit 100 \\
    --gpu-id 1
EOF
}

MODEL_TAG=""
MODEL_PATH=""
RUN_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model-tag) MODEL_TAG="$2"; shift 2 ;;
        --model-path) MODEL_PATH="$2"; shift 2 ;;
        --limit) LIMIT="$2"; shift 2 ;;
        --gpu-id) GPU_ID="$2"; shift 2 ;;
        --run-id) RUN_ID="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Error: unknown argument $1" >&2; usage; exit 1 ;;
    esac
done

if [[ -z "${MODEL_TAG}" || -z "${MODEL_PATH}" ]]; then
    echo "Error: --model-tag and --model-path are required." >&2
    usage
    exit 1
fi

if [[ ! -d "${MODEL_PATH}" ]]; then
    echo "Error: model path does not exist: ${MODEL_PATH}" >&2
    exit 1
fi

MODEL_PATH_ABS="$(realpath "${MODEL_PATH}")"

if [[ -z "${RUN_ID}" ]]; then
    RUN_ID="compare_${MODEL_TAG}_$(date +%Y%m%d_%H%M%S)"
fi

RUN_DIR="${PROJECT_ROOT}/runs/eval_experimental/backend_compare/${MODEL_TAG}/${RUN_ID}"
REPORT_DIR="${PROJECT_ROOT}/reports/eval_experimental/backend_compare/${MODEL_TAG}/${RUN_ID}"

mkdir -p "${RUN_DIR}"/hf/{qa,gen}
mkdir -p "${RUN_DIR}"/vllm/{qa,gen}
mkdir -p "${RUN_DIR}"/logs
mkdir -p "${REPORT_DIR}"

GENERATED_AT="$(date -Iseconds)"

# Environment variables for both backends
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export CUDA_VISIBLE_DEVICES="${GPU_ID}"
# vLLM V1 engine has tokenizer incompatibility with Qwen3.5-2B + dev transformers;
# fall back to the legacy engine for this experimental comparison.
export VLLM_USE_V1=0

echo "=== HF vs vLLM backend_compare ==="
echo "Model tag: ${MODEL_TAG}"
echo "Model path: ${MODEL_PATH_ABS}"
echo "Limit: ${LIMIT}"
echo "Physical GPU: ${GPU_ID} (script internal device: cuda:0)"
echo "Run dir: ${RUN_DIR}"
echo ""

# ---------------------------------------------------------------------------
# HF runs
# ---------------------------------------------------------------------------
echo "=== Running HF QA (limit=${LIMIT}) ==="
HF_QA_START=$(date +%s)
cd "${DATA_DIR}"
${HF_PYTHON} -m lm_eval run \
    --model hf \
    --model_args "pretrained=${MODEL_PATH_ABS},trust_remote_code=True" \
    --tasks hsbqa,dsbqa \
    --device cuda:0 \
    --batch_size auto \
    --limit "${LIMIT}" \
    --output_path "${RUN_DIR}/hf/qa" \
    --log_samples 2>&1 | tee "${RUN_DIR}/logs/hf_qa.log"
HF_QA_END=$(date +%s)
HF_QA_TIME=$((HF_QA_END - HF_QA_START))

echo "=== Running HF Gen (limit=${LIMIT}) ==="
HF_GEN_START=$(date +%s)
cd "${DATA_DIR}"
${HF_PYTHON} -m lm_eval run \
    --model hf \
    --model_args "pretrained=${MODEL_PATH_ABS},trust_remote_code=True,enable_thinking=False" \
    --apply_chat_template \
    --tasks sorbian_dev \
    --device cuda:0 \
    --batch_size auto \
    --limit "${LIMIT}" \
    --output_path "${RUN_DIR}/hf/gen" \
    --log_samples 2>&1 | tee "${RUN_DIR}/logs/hf_gen.log"
HF_GEN_END=$(date +%s)
HF_GEN_TIME=$((HF_GEN_END - HF_GEN_START))

# ---------------------------------------------------------------------------
# vLLM runs
# ---------------------------------------------------------------------------
echo "=== Running vLLM QA (limit=${LIMIT}) ==="
VLLM_QA_START=$(date +%s)
cd "${DATA_DIR}"
${VLLM_PYTHON} -m lm_eval run \
    --model vllm \
    --model_args "pretrained=${MODEL_PATH_ABS},trust_remote_code=True,dtype=auto,gpu_memory_utilization=0.8" \
    --tasks hsbqa,dsbqa \
    --batch_size auto \
    --limit "${LIMIT}" \
    --output_path "${RUN_DIR}/vllm/qa" \
    --log_samples 2>&1 | tee "${RUN_DIR}/logs/vllm_qa.log"
VLLM_QA_END=$(date +%s)
VLLM_QA_TIME=$((VLLM_QA_END - VLLM_QA_START))

echo "=== Running vLLM Gen (limit=${LIMIT}) ==="
VLLM_GEN_START=$(date +%s)
cd "${DATA_DIR}"
${VLLM_PYTHON} -m lm_eval run \
    --model vllm \
    --model_args "pretrained=${MODEL_PATH_ABS},trust_remote_code=True,dtype=auto,gpu_memory_utilization=0.8,enable_thinking=False" \
    --apply_chat_template \
    --tasks sorbian_dev \
    --batch_size auto \
    --limit "${LIMIT}" \
    --output_path "${RUN_DIR}/vllm/gen" \
    --log_samples 2>&1 | tee "${RUN_DIR}/logs/vllm_gen.log"
VLLM_GEN_END=$(date +%s)
VLLM_GEN_TIME=$((VLLM_GEN_END - VLLM_GEN_START))

# ---------------------------------------------------------------------------
# Locate result files
# ---------------------------------------------------------------------------
HF_QA_RESULT=$(find "${RUN_DIR}/hf/qa" -name 'results_*.json' | head -1)
HF_GEN_RESULT=$(find "${RUN_DIR}/hf/gen" -name 'results_*.json' | head -1)
VLLM_QA_RESULT=$(find "${RUN_DIR}/vllm/qa" -name 'results_*.json' | head -1)
VLLM_GEN_RESULT=$(find "${RUN_DIR}/vllm/gen" -name 'results_*.json' | head -1)

for f in "${HF_QA_RESULT}" "${HF_GEN_RESULT}" "${VLLM_QA_RESULT}" "${VLLM_GEN_RESULT}"; do
    if [[ ! -f "${f}" ]]; then
        echo "Error: missing result file: ${f}" >&2
        exit 1
    fi
done

# ---------------------------------------------------------------------------
# Gather environment versions
# ---------------------------------------------------------------------------
HF_VERSIONS=$(${HF_PYTHON} - <<PY
import sys, torch, transformers, lm_eval
print(f"python={sys.version.split()[0]}; torch={torch.__version__}; cuda={torch.cuda.is_available()}; transformers={transformers.__version__}; lm_eval={lm_eval.__version__}")
PY
)

VLLM_VERSIONS=$(${VLLM_PYTHON} - <<PY
import sys, torch, transformers, lm_eval, vllm
print(f"python={sys.version.split()[0]}; torch={torch.__version__}; cuda={torch.cuda.is_available()}; transformers={transformers.__version__}; lm_eval={lm_eval.__version__}; vllm={vllm.__version__}")
PY
)

# ---------------------------------------------------------------------------
# Generate BACKEND_COMPARE.md
# ---------------------------------------------------------------------------
${VLLM_PYTHON} <<PYEOF
import json
import sys
from pathlib import Path

run_dir = Path("${RUN_DIR}")
report_dir = Path("${REPORT_DIR}")
limit = int("${LIMIT}")
gpu_id = "${GPU_ID}"

hf_qa = json.loads(Path("${HF_QA_RESULT}").read_text())
hf_gen = json.loads(Path("${HF_GEN_RESULT}").read_text())
vllm_qa = json.loads(Path("${VLLM_QA_RESULT}").read_text())
vllm_gen = json.loads(Path("${VLLM_GEN_RESULT}").read_text())

def extract_scores(result_json):
    return result_json.get("results", {})

hf_qa_scores = extract_scores(hf_qa)
vllm_qa_scores = extract_scores(vllm_qa)
hf_gen_scores = extract_scores(hf_gen)
vllm_gen_scores = extract_scores(vllm_gen)

# Flatten task -> metric -> value
qa_rows = []
for task in ["hsbqa", "dsbqa"]:
    hf_task = hf_qa_scores.get(task, {})
    vllm_task = vllm_qa_scores.get(task, {})
    for metric_key in hf_task:
        if not metric_key.endswith("_stderr") and metric_key not in ("alias",):
            hf_val = hf_task.get(metric_key)
            vllm_val = vllm_task.get(metric_key)
            diff = None
            if isinstance(hf_val, (int, float)) and isinstance(vllm_val, (int, float)):
                diff = vllm_val - hf_val
            qa_rows.append((task, metric_key, hf_val, vllm_val, diff))

gen_rows = []
for task in hf_gen_scores:
    if task == "sorbian_dev":
        continue
    hf_task = hf_gen_scores.get(task, {})
    vllm_task = vllm_gen_scores.get(task, {})
    for metric_key in hf_task:
        if not metric_key.endswith("_stderr") and metric_key not in ("alias", "name", "sample_len"):
            hf_val = hf_task.get(metric_key)
            vllm_val = vllm_task.get(metric_key)
            diff = None
            if isinstance(hf_val, (int, float)) and isinstance(vllm_val, (int, float)):
                diff = vllm_val - hf_val
            gen_rows.append((task, metric_key, hf_val, vllm_val, diff))

# Count invalid parses in samples files
def count_invalid(sample_dir):
    total = 0
    invalid = 0
    for p in Path(sample_dir).rglob("samples_*.jsonl"):
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            total += 1
            rec = json.loads(line)
            filtered = rec.get("filtered_resps", [])
            if filtered and isinstance(filtered, list):
                txt = str(filtered[0]).strip().lower()
                if txt in ("[invalid]", "invalid"):
                    invalid += 1
    return total, invalid

hf_gen_total, hf_gen_invalid = count_invalid(run_dir / "hf" / "gen")
vllm_gen_total, vllm_gen_invalid = count_invalid(run_dir / "vllm" / "gen")

lines = []
lines.append("# HF vs vLLM Backend Compare Report")
lines.append("")
lines.append("## Run Metadata")
lines.append("")
lines.append(f"- run_id: ${RUN_ID}")
lines.append(f"- model_tag: ${MODEL_TAG}")
lines.append(f"- model_path: ${MODEL_PATH_ABS}")
lines.append(f"- limit: {limit}")
lines.append(f"- physical_gpu: {gpu_id} (script internal device: cuda:0)")
lines.append(f"- eval_code_commit: ${EVAL_CODE_COMMIT}")
lines.append(f"- data_commit: ${DATA_COMMIT}")
lines.append(f"- generated_at: ${GENERATED_AT}")
lines.append(f"- run_dir: {run_dir}")
lines.append("")
lines.append("## Environment Versions")
lines.append("")
lines.append("| Backend | Versions |")
lines.append("|---|---|")
lines.append(f"| HF (`.venv`) | ${HF_VERSIONS} |")
lines.append(f"| vLLM (`.venvs/eval-vllm`) | ${VLLM_VERSIONS} |")
lines.append("")
lines.append("## Timing")
lines.append("")
lines.append("| Stage | HF (s) | vLLM (s) | Speedup |")
lines.append("|---|---:|---:|---:|")
hf_qa_t = ${HF_QA_TIME}
vllm_qa_t = ${VLLM_QA_TIME}
hf_gen_t = ${HF_GEN_TIME}
vllm_gen_t = ${VLLM_GEN_TIME}
qa_speedup = hf_qa_t / vllm_qa_t if vllm_qa_t else 0
gen_speedup = hf_gen_t / vllm_gen_t if vllm_gen_t else 0
total_speedup = (hf_qa_t + hf_gen_t) / (vllm_qa_t + vllm_gen_t) if (vllm_qa_t + vllm_gen_t) else 0
lines.append(f"| QA | {hf_qa_t} | {vllm_qa_t} | {qa_speedup:.2f}x |")
lines.append(f"| Gen | {hf_gen_t} | {vllm_gen_t} | {gen_speedup:.2f}x |")
lines.append(f"| Total | {hf_qa_t + hf_gen_t} | {vllm_qa_t + vllm_gen_t} | {total_speedup:.2f}x |")
lines.append("")
lines.append("## QA Scores")
lines.append("")
lines.append("| Task | Metric | HF | vLLM | Diff |")
lines.append("|---|---|---:|---:|---:|")
for task, metric, hf_val, vllm_val, diff in qa_rows:
    diff_str = f"{diff:.4f}" if diff is not None else "N/A"
    lines.append(f"| {task} | {metric} | {hf_val} | {vllm_val} | {diff_str} |")
lines.append("")
lines.append("## Generative Scores")
lines.append("")
lines.append("| Task | Metric | HF | vLLM | Diff |")
lines.append("|---|---|---:|---:|---:|")
for task, metric, hf_val, vllm_val, diff in gen_rows:
    diff_str = f"{diff:.4f}" if diff is not None else "N/A"
    lines.append(f"| {task} | {metric} | {hf_val} | {vllm_val} | {diff_str} |")
lines.append("")
lines.append("## Invalid Parse Rate (generative tasks)")
lines.append("")
lines.append("| Backend | Total Samples | Invalid Parses | Invalid Rate |")
lines.append("|---|---|---:|---:|")
hf_rate = hf_gen_invalid / hf_gen_total * 100 if hf_gen_total else 0
vllm_rate = vllm_gen_invalid / vllm_gen_total * 100 if vllm_gen_total else 0
lines.append(f"| HF | {hf_gen_total} | {hf_gen_invalid} | {hf_rate:.2f}% |")
lines.append(f"| vLLM | {vllm_gen_total} | {vllm_gen_invalid} | {vllm_rate:.2f}% |")
lines.append("")
lines.append("## Recommendation")
lines.append("")
max_abs_qa_diff = max((abs(d) for _, _, _, _, d in qa_rows if d is not None), default=0)
max_abs_gen_diff = max((abs(d) for _, _, _, _, d in gen_rows if d is not None), default=0)
invalid_increase = vllm_rate - hf_rate
speedup_ok = total_speedup >= 1.0

recommendations = []
if max_abs_qa_diff <= 0.01:
    recommendations.append("QA diff OK (≤1 pp).")
else:
    recommendations.append(f"QA diff too large ({max_abs_qa_diff:.4f}).")

if max_abs_gen_diff <= 0.05:
    recommendations.append("Gen diff OK (≤0.05).")
else:
    recommendations.append(f"Gen diff too large ({max_abs_gen_diff:.4f}).")

if invalid_increase <= 1.0:
    recommendations.append("Invalid parse rate OK.")
else:
    recommendations.append(f"Invalid parse rate increased by {invalid_increase:.2f} pp.")

if speedup_ok:
    recommendations.append(f"vLLM is faster ({total_speedup:.2f}x).")
else:
    recommendations.append(f"vLLM is not faster ({total_speedup:.2f}x).")

if max_abs_qa_diff <= 0.01 and max_abs_gen_diff <= 0.05 and invalid_increase <= 1.0 and speedup_ok:
    verdict = "PASS: vLLM is sufficiently close to HF reference, invalid parse rate is acceptable, and speedup is observed. Consider accepting vLLM as official backend after full-run confirmation."
else:
    verdict = "FAIL: " + " ".join(recommendations) + " Keep vLLM in experimental/backend_compare until resolved."
lines.append(verdict)
lines.append("")
lines.append("## Raw Result Files")
lines.append("")
lines.append(f"- HF QA: ${HF_QA_RESULT}")
lines.append(f"- HF Gen: ${HF_GEN_RESULT}")
lines.append(f"- vLLM QA: ${VLLM_QA_RESULT}")
lines.append(f"- vLLM Gen: ${VLLM_GEN_RESULT}")
lines.append("")

report_path = report_dir / "BACKEND_COMPARE.md"
report_path.write_text("\n".join(lines))
print(f"Wrote {report_path}")
PYEOF

# ---------------------------------------------------------------------------
# Write run.yaml metadata
# ---------------------------------------------------------------------------
cat > "${RUN_DIR}/run.yaml" <<EOF
model_tag: "${MODEL_TAG}"
model_path: "${MODEL_PATH_ABS}"
eval_setting: "backend_compare"
shot_setting: "zero_shot"
limit: ${LIMIT}
gpu_id: ${GPU_ID}
hf_backend: "hf"
vllm_backend: "vllm"
hf_python: "${HF_PYTHON}"
vllm_python: "${VLLM_PYTHON}"
eval_code_repo: "${EVAL_CODE_REPO}"
eval_code_commit: "${EVAL_CODE_COMMIT}"
data_repo: "${DATA_REPO}"
data_commit: "${DATA_COMMIT}"
official: false
source_run_dir: "${RUN_DIR}"
report_dir: "${REPORT_DIR}"
generated_at: "${GENERATED_AT}"
status: "completed"
notes: "Experimental HF vs vLLM backend_compare. Results are not official."
EOF

echo ""
echo "=== Backend compare complete ==="
echo "Run dir:    ${RUN_DIR}"
echo "Report:     ${REPORT_DIR}/BACKEND_COMPARE.md"
