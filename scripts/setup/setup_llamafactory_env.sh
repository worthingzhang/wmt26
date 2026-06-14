#!/usr/bin/env bash
# Setup LlamaFactory environment for CPT/SFT.
# This script does NOT download models, run training, or run evaluation.

set -euo pipefail

PROJECT_ROOT="/home/zc/wmt26"
VENV_DIR="${PROJECT_ROOT}/.venvs/llamafactory"
MIRRORS_ENV="${PROJECT_ROOT}/configs/env/mirrors.env"
LLAMAFACTORY_DIR="${PROJECT_ROOT}/repos/thunlp_opd/LlamaFactory"

echo "=== Entering project root: ${PROJECT_ROOT} ==="
cd "${PROJECT_ROOT}"

echo "=== Loading mirror/env configuration: ${MIRRORS_ENV} ==="
if [[ -f "${MIRRORS_ENV}" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "${MIRRORS_ENV}"
    set +a
    echo "Loaded mirror/env configuration."
else
    echo "Error: mirror/env configuration not found: ${MIRRORS_ENV}"
    exit 1
fi

echo "=== Verifying LlamaFactory source directory ==="
if [[ ! -d "${LLAMAFACTORY_DIR}" ]]; then
    echo "Error: LlamaFactory directory not found: ${LLAMAFACTORY_DIR}"
    exit 1
fi

echo "=== Setting up LlamaFactory venv: ${VENV_DIR} ==="
if [[ ! -d "${VENV_DIR}" ]]; then
    echo "Creating Python 3.11 venv with uv..."
    uv venv --python 3.11 "${VENV_DIR}"
else
    echo "Using existing venv: ${VENV_DIR}"
fi

PYTHON="${VENV_DIR}/bin/python"

echo "=== Upgrading base tooling inside venv ==="
uv pip install --python "${PYTHON}" --upgrade pip setuptools wheel

echo "=== Installing torch (CUDA 12.6) separately ==="
echo "If this step times out, stop and report the error instead of silently falling back to CPU."
uv pip install --python "${PYTHON}" torch==2.7.0 torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu126

echo "=== Installing LlamaFactory from ${LLAMAFACTORY_DIR} ==="
uv pip install --python "${PYTHON}" -e "${LLAMAFACTORY_DIR}"

echo "=== Verifying CUDA availability ==="
"${PYTHON}" - <<'PY'
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

echo "=== Verifying llamafactory-cli ==="
LLAMAFACTORY_CLI="${VENV_DIR}/bin/llamafactory-cli"
if [[ ! -x "${LLAMAFACTORY_CLI}" ]]; then
    echo "ERROR: llamafactory-cli not found or not executable: ${LLAMAFACTORY_CLI}"
    exit 1
fi
"${LLAMAFACTORY_CLI}" version

echo ""
echo "=== LlamaFactory environment setup complete ==="
echo "Activate with: source ${VENV_DIR}/bin/activate"
echo "Verify with:    llamafactory-cli version"
