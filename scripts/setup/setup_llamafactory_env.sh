#!/usr/bin/env bash
# Setup LlamaFactory environment for CPT/SFT.
# This script auto-loads mirror/env config and creates/updates the venv.

set -euo pipefail

PROJECT_ROOT="/home/zc/wmt26"
LLAMAFACTORY_DIR="${PROJECT_ROOT}/repos/thunlp_opd/LlamaFactory"
VENV_DIR="${PROJECT_ROOT}/.venvs/llamafactory"
MIRRORS_ENV="${PROJECT_ROOT}/configs/env/mirrors.env"

# Load mirror/env configuration
if [[ -f "${MIRRORS_ENV}" ]]; then
    set -a
    source "${MIRRORS_ENV}"
    set +a
    echo "Loaded env config: ${MIRRORS_ENV}"
else
    echo "Warning: env config not found: ${MIRRORS_ENV}"
fi

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Setup the LlamaFactory environment for CPT/SFT.

Options:
  --force-recreate    Delete existing venv and recreate it.
  -h, --help          Show this help.
EOF
}

FORCE_RECREATE=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force-recreate) FORCE_RECREATE=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1"; usage; exit 1 ;;
    esac
done

# Validate LlamaFactory directory
if [[ ! -d "${LLAMAFACTORY_DIR}" ]]; then
    echo "Error: LlamaFactory directory not found: ${LLAMAFACTORY_DIR}"
    echo "Please clone repos/thunlp_opd first."
    exit 1
fi

# Create or recreate venv
if [[ "${FORCE_RECREATE}" == true && -d "${VENV_DIR}" ]]; then
    echo "Force recreating venv..."
    rm -rf "${VENV_DIR}"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
    echo "Creating venv at ${VENV_DIR} with Python 3.11..."
    uv venv --python 3.11 "${VENV_DIR}"
else
    echo "Using existing venv: ${VENV_DIR}"
fi

PYTHON="${VENV_DIR}/bin/python"

# Install base packages
echo "Installing base packages..."
uv pip install --python "${PYTHON}" pip setuptools wheel

# Install torch separately with PyTorch CUDA 12.4 index.
# This prevents LlamaFactory from pulling a wrong torch build.
echo "Installing torch (CUDA 12.4)..."
uv pip install --python "${PYTHON}" torch --index-url https://download.pytorch.org/whl/cu124

# Install LlamaFactory in editable mode
echo "Installing LlamaFactory from ${LLAMAFACTORY_DIR}..."
uv pip install --python "${PYTHON}" -e "${LLAMAFACTORY_DIR}"

# Install extra metrics requirements if present
METRICS_REQ="${LLAMAFACTORY_DIR}/requirements/metrics.txt"
if [[ -f "${METRICS_REQ}" ]]; then
    echo "Installing metrics requirements..."
    uv pip install --python "${PYTHON}" -r "${METRICS_REQ}"
else
    echo "No metrics requirements found at ${METRICS_REQ}, skipping."
fi

echo ""
echo "=== LlamaFactory environment setup complete ==="
echo "Activate with: source ${VENV_DIR}/bin/activate"
echo "Verify with:    llamafactory-cli version"
