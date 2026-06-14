#!/usr/bin/env bash
# Setup OPD/verl/vLLM/sglang environment using conda prefix.
# This script does NOT train, evaluate, or download models.

set -euo pipefail

PROJECT_ROOT="/home/zc/wmt26"
CONDA_BIN="/data/wyt/miniconda3/bin/conda"
ENV_PREFIX="${PROJECT_ROOT}/.conda/envs/verl"
MIRRORS_ENV="${PROJECT_ROOT}/configs/env/mirrors.env"
VERL_DIR="${PROJECT_ROOT}/repos/thunlp_opd/verl"
INSTALL_SCRIPT="${VERL_DIR}/scripts/install_vllm_sglang_mcore.sh"

echo "=== Entering project root: ${PROJECT_ROOT} ==="
cd "${PROJECT_ROOT}"

echo "=== Loading mirror/env configuration ==="
if [[ -f "${MIRRORS_ENV}" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "${MIRRORS_ENV}"
    set +a
    echo "Loaded: ${MIRRORS_ENV}"
else
    echo "Warning: mirror/env configuration not found: ${MIRRORS_ENV}"
fi

echo "=== Checking conda availability ==="
if [[ ! -x "${CONDA_BIN}" ]]; then
    echo "Error: conda not found or not executable: ${CONDA_BIN}"
    exit 1
fi
"${CONDA_BIN}" --version

echo "=== Initializing conda shell hooks ==="
eval "$("${CONDA_BIN}" shell.bash hook)"

echo "=== Setting up conda prefix environment: ${ENV_PREFIX} ==="
if [[ -d "${ENV_PREFIX}" ]]; then
    echo "Environment already exists, reusing: ${ENV_PREFIX}"
else
    echo "Creating conda prefix environment with Python 3.12..."
    conda create -y -p "${ENV_PREFIX}" python=3.12
fi

echo "=== Activating environment ==="
conda activate "${ENV_PREFIX}"

echo "=== Verifying Python path ==="
which python
python --version

EXPECTED_PYTHON="${ENV_PREFIX}/bin/python"
CURRENT_PYTHON="$(which python)"
if [[ "${CURRENT_PYTHON}" != "${EXPECTED_PYTHON}" ]]; then
    echo "Error: python does not point to the expected environment binary."
    echo "Expected: ${EXPECTED_PYTHON}"
    echo "Got:      ${CURRENT_PYTHON}"
    exit 1
fi

echo "=== Checking verl install script ==="
if [[ ! -f "${INSTALL_SCRIPT}" ]]; then
    echo "Error: install script not found: ${INSTALL_SCRIPT}"
    exit 1
fi
echo "Install script: ${INSTALL_SCRIPT}"
echo "It will install vLLM/sglang dependencies and FlashAttention; it does not start training."

echo "=== Running OPD/verl dependency install ==="
cd "${VERL_DIR}"
USE_MEGATRON=0 bash "${INSTALL_SCRIPT}"

echo "=== Installing math-verify ==="
pip install math-verify

echo "=== Verifying CUDA availability ==="
python - <<'PY'
import torch
import sys

print("torch:", torch.__version__)
print("cuda_available:", torch.cuda.is_available())
print("cuda_runtime:", torch.version.cuda)
print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CUDA not available")

if not torch.cuda.is_available():
    print("ERROR: torch.cuda.is_available() is False. Installation rejected.")
    sys.exit(1)
PY

echo "=== Verifying package imports ==="
python - <<'PY'
mods = ["verl", "vllm", "sglang"]
for m in mods:
    try:
        mod = __import__(m)
        print(m, "OK", getattr(mod, "__version__", "unknown"))
    except Exception as e:
        print(m, "FAILED:", repr(e))

import math_verify
print("math_verify OK")
PY

echo ""
echo "=== OPD/verl environment setup complete ==="
echo "Activate with: conda activate ${ENV_PREFIX}"
