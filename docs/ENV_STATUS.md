# Environment Status

Report generated: 2026-06-15

## Main / Eval Environment

- **Path**: `/home/zc/wmt26/.venv`
- **Python**: 3.12
- **Purpose**: project tooling, pandas, official_eval / lm_eval
- **Status**: ready (not modified in this step)

## LlamaFactory Environment (CPT/SFT)

- **Path**: `/home/zc/wmt26/.venvs/llamafactory`
- **Python**: 3.11.14
- **torch**: 2.7.0+cu126
- **CUDA available**: `True`
- **CUDA runtime**: 12.6
- **GPU**: NVIDIA GeForce RTX 4090
- **llamafactory-cli**: available at `/home/zc/wmt26/.venvs/llamafactory/bin/llamafactory-cli`
- **Version**: 0.9.5.dev0
- **Status**: ✅ ready

### Verification Commands

```bash
source /home/zc/wmt26/.venvs/llamafactory/bin/activate
python --version
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda_available:", torch.cuda.is_available())
print("cuda_runtime:", torch.version.cuda)
print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CUDA not available")
PY
llamafactory-cli version
```

## Base Model

- **Standard path**: `/home/zc/wmt26/models/base/Qwen3.5-2B`
- **Status**: ✅ exists and contains `config.json`, `tokenizer.json`, and `*.safetensors`

## OPD / verl / vLLM / sglang Environment

- **Path**: `/home/zc/wmt26/.conda/envs/verl`
- **Type**: conda prefix environment
- **Python**: 3.12.13
- **torch**: 2.8.0+cu128
- **CUDA available**: `True`
- **CUDA runtime**: 12.8
- **GPU**: NVIDIA GeForce RTX 4090
- **Status**: ✅ ready

### How it was installed

Following the local `repos/thunlp_opd/README.md`:

```bash
conda create -y -p /home/zc/wmt26/.conda/envs/verl python=3.12
conda activate /home/zc/wmt26/.conda/envs/verl
cd /home/zc/wmt26/repos/thunlp_opd/verl
USE_MEGATRON=0 bash scripts/install_vllm_sglang_mcore.sh
pip install math-verify
```

The install script:

- Installed `sglang[all]==0.5.2`, `torch-memory-saver`
- Installed `vllm==0.11.0`
- Installed verl base dependencies (transformers, accelerate, datasets, ray, tensordict, etc.)
- Downloaded and installed prebuilt FlashAttention wheel (`flash_attn-2.8.1+cu12torch2.8...`)
- Installed `flashinfer-python==0.3.1`
- Skipped Megatron/TransformerEngine (`USE_MEGATRON=0`)

No training or model download was performed.

### Verification

```text
torch: 2.8.0+cu128
cuda_available: True
cuda_runtime: 12.8
gpu: NVIDIA GeForce RTX 4090
verl OK 0.7.0.dev
vllm OK 0.11.0
sglang OK 0.5.2
math_verify OK
```

### Known dependency conflicts

pip's resolver reported some conflicts (numpy version mismatches between opencv, cupy-cuda12x, outlines, numba, mistral-common). The install completed and all required imports succeed, but these may need attention if OPD smoke runs hit runtime errors.

### OPD / verl scripts found

Key launch scripts for OPD:

- `/home/zc/wmt26/repos/thunlp_opd/on_policy_distillation.sh`
- `/home/zc/wmt26/repos/thunlp_opd/grpo.sh`
- `/home/zc/wmt26/repos/thunlp_opd/verl_example/opd.sh`

Helper scripts:

- `/home/zc/wmt26/repos/thunlp_opd/scripts/infer/vllm_rollout.py`
- `/home/zc/wmt26/repos/thunlp_opd/scripts/infer/dedup_deepmath.py`

### Activation

```bash
conda activate /home/zc/wmt26/.conda/envs/verl
```

## tmux

- **Status**: ✅ installed
- **Version**: 3.2a
- **Needs admin install**: no

### Usage for long-running tasks

```bash
# Create a new session
tmux new -s cpt_smoke

# Run your command inside the session
bash scripts/train/train_cpt.sh ...

# Detach: Ctrl+B, then D
# Re-attach later: tmux attach -t cpt_smoke
```

## Not Installed (by design)

None — all three environments are now ready.
