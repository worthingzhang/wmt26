#!/usr/bin/env bash
set -euo pipefail

cd /home/zc/wmt26

source /home/zc/wmt26/.venvs/llamafactory/bin/activate
if [[ -f /home/zc/wmt26/configs/env/mirrors.env ]]; then
  set -a
  source /home/zc/wmt26/configs/env/mirrors.env
  set +a
fi

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

LOG_DIR=/home/zc/wmt26/logs/train/cpt_v1_official_plaintext_dsb4x
LOG_FILE="${LOG_DIR}/full.log"
mkdir -p "${LOG_DIR}"

FORCE_TORCHRUN=1 llamafactory-cli train /home/zc/wmt26/configs/train/cpt/cpt_v1_official_plaintext_dsb4x_full.yaml 2>&1 | tee "${LOG_FILE}"
