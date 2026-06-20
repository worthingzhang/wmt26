#!/usr/bin/env bash
# Setup script for the lab cluster with 48GB GPUs.
# Run this on the new cluster after cloning the repo to /data1/zc/wmt26.
# Assumes: Ubuntu 22.04, NVIDIA driver 570+, CUDA 12.8 capable.

set -euo pipefail

PROJECT_ROOT="/data1/zc/wmt26"
OLD_PROJECT_ROOT="/home/zc/wmt26"
MIRRORS_ENV="${PROJECT_ROOT}/configs/env/mirrors.env"
CONDA_INSTALL_DIR="${HOME}/miniconda3"

if [[ "$(pwd)" != "${PROJECT_ROOT}" ]]; then
    echo "Please run this script from ${PROJECT_ROOT}"
    exit 1
fi

echo "=== Project root: ${PROJECT_ROOT} ==="

echo ""
echo "=== Step 1: Install uv ==="
if ! command -v uv &> /dev/null; then
    echo "uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${PATH}"
else
    echo "uv already installed: $(uv --version)"
fi

echo ""
echo "=== Step 2: Install Miniconda ==="
if [[ ! -x "${CONDA_INSTALL_DIR}/bin/conda" ]]; then
    echo "Installing Miniconda to ${CONDA_INSTALL_DIR}..."
    curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p "${CONDA_INSTALL_DIR}"
    rm -f /tmp/miniconda.sh
else
    echo "Miniconda already installed: ${CONDA_INSTALL_DIR}"
fi

# Update mirrors.env path
echo ""
echo "=== Step 3: Update mirror config paths ==="
if [[ -f "${MIRRORS_ENV}" ]]; then
    sed -i "s|${OLD_PROJECT_ROOT}|${PROJECT_ROOT}|g" "${MIRRORS_ENV}"
    echo "Updated HF_HOME path in ${MIRRORS_ENV}"
fi

# Update hardcoded paths in scripts and configs
echo ""
echo "=== Step 4: Update hardcoded paths in scripts/configs ==="
find scripts configs -type f \( -name "*.sh" -o -name "*.yaml" -o -o -name "*.py" -o -name "*.md" \) \
    -exec grep -l "${OLD_PROJECT_ROOT}" {} \; | while read -r f; do
    echo "Updating paths in: $f"
    sed -i "s|${OLD_PROJECT_ROOT}|${PROJECT_ROOT}|g" "$f"
done

# Update conda path in setup script
sed -i "s|/data/wyt/miniconda3/bin/conda|${CONDA_INSTALL_DIR}/bin/conda|g" \
    "${PROJECT_ROOT}/scripts/setup/setup_opd_verl_conda_env.sh"

echo ""
echo "=== Step 5: Clone external backend repos ==="
if [[ ! -d "${PROJECT_ROOT}/repos/thunlp_opd/LlamaFactory" ]]; then
    echo "Cloning OPD repo..."
    git clone https://github.com/worthingzhang/OPD.git "${PROJECT_ROOT}/repos/thunlp_opd"
else
    echo "OPD repo already exists"
fi

if [[ ! -d "${PROJECT_ROOT}/repos/official_eval" ]]; then
    echo "Cloning official_eval repo..."
    git clone https://github.com/worthingzhang/llms-lim-res-eval-2026.git "${PROJECT_ROOT}/repos/official_eval"
else
    echo "official_eval repo already exists"
fi

echo ""
echo "=== Step 6: Apply Sorbian MR metric patch ==="
cd "${PROJECT_ROOT}/repos/official_eval"
if git merge-base --is-ancestor 1e6ab97b005464fc0e4581cc850499eac4dc2bc9 HEAD 2>/dev/null; then
    echo "Patch already included"
else
    echo "Checking out patched commit..."
    git checkout 1e6ab97b005464fc0e4581cc850499eac4dc2bc9
fi
cd "${PROJECT_ROOT}"

echo ""
echo "=== Step 7: Setup main/eval environment (.venv) ==="
if [[ ! -d "${PROJECT_ROOT}/.venv" ]]; then
    uv venv --python 3.12 "${PROJECT_ROOT}/.venv"
fi
source "${PROJECT_ROOT}/.venv/bin/activate"
uv pip install --upgrade pip setuptools wheel
uv pip install pandas pyyaml tqdm rich jsonlines
uv pip install -e "${PROJECT_ROOT}/repos/official_eval[hf]"
python - <<'PY'
import torch, lm_eval
print("torch:", torch.__version__)
print("cuda_available:", torch.cuda.is_available())
print("lm_eval:", lm_eval.__version__)
PY

echo ""
echo "=== Step 8: Setup LlamaFactory environment ==="
# Adapt torch CUDA version to the new cluster (CUDA 12.8 driver)
# The original script uses cu126; cu126/cu128 both work on CUDA 12.8.
# We keep cu126 to match proven config, but you can change to cu128 if needed.
bash "${PROJECT_ROOT}/scripts/setup/setup_llamafactory_env.sh"

echo ""
echo "=== Step 9: Setup OPD/verl environment (optional) ==="
bash "${PROJECT_ROOT}/scripts/setup/setup_opd_verl_conda_env.sh"

echo ""
echo "=== Step 10: Verify large assets ==="
MISSING=0
for path in \
    "${PROJECT_ROOT}/models/base/Qwen3.5-2B/config.json" \
    "${PROJECT_ROOT}/data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl"; do
    if [[ ! -f "${path}" ]]; then
        echo "MISSING: ${path}"
        MISSING=1
    else
        echo "OK: ${path}"
    fi
done

if [[ ${MISSING} -eq 1 ]]; then
    echo ""
    echo "Some large assets are missing. Copy them from the old cluster with:"
    echo "  rsync -avP /home/zc/wmt26/models/base/Qwen3.5-2B/         ${PROJECT_ROOT}/models/base/Qwen3.5-2B/"
    echo "  rsync -avP /home/zc/wmt26/data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl ${PROJECT_ROOT}/data/processed/llamafactory/cpt/"
    echo "  rsync -avP /home/zc/wmt26/data/processed/llamafactory/dataset_info.json ${PROJECT_ROOT}/data/processed/llamafactory/"
fi

echo ""
echo "=== Setup complete ==="
echo "Activate main env: source ${PROJECT_ROOT}/.venv/bin/activate"
echo "Activate LLF env:  source ${PROJECT_ROOT}/.venvs/llamafactory/bin/activate"
echo "Activate verl env: conda activate ${PROJECT_ROOT}/.conda/envs/verl"
