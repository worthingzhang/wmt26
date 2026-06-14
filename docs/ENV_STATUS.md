# Environment Status

Report generated: 2026-06-15

## System Information

| Item | Value |
|---|---|
| Hostname | `ubun` |
| OS | Ubuntu 22.04.5 LTS (Jammy) |
| NVIDIA Driver | 535.183.01 |
| CUDA Version (driver) | 12.2 |
| GPUs | 8 × NVIDIA GeForce RTX 4090 (24 GB each) |
| tmux | 3.2a ✅ |
| git | 2.34.1 |
| uv | 0.10.7 |
| conda binary | `/data/wyt/miniconda3/bin/conda` (not in default `PATH`) |
| Project root | `/home/zc/wmt26` |
| Working tree | clean (no uncommitted project changes) |

## Python Environments

| Environment | Path | Python | torch | CUDA runtime | CUDA available | Key packages | Status |
|---|---|---|---|---|---|---|---|
| Main / Eval | `.venv` | 3.12.12 | 2.6.0+cu124 | 12.4 | ✅ True | lm_eval 0.4.12.dev0, transformers 5.12.0, datasets 5.0.0, pandas 3.0.3 | ✅ ready |
| LlamaFactory CPT/SFT | `.venvs/llamafactory` | 3.11.14 | 2.7.0+cu126 | 12.6 | ✅ True | llamafactory-cli 0.9.5.dev0 | ✅ ready |
| OPD / verl / vLLM / sglang | `.conda/envs/verl` | 3.12.13 | 2.8.0+cu128 | 12.8 | ✅ True | vllm 0.11.0, sglang 0.5.2, math-verify 0.9.0 | ⚠️ see verl note below |

### Main / Eval Environment Details

- **Activation**: `source /home/zc/wmt26/.venv/bin/activate`
- All checked imports succeeded:
  - `torch` 2.6.0+cu124
  - `transformers` 5.12.0
  - `datasets` 5.0.0
  - `lm_eval` 0.4.12.dev0
  - `pandas` 3.0.3
  - `yaml`, `tqdm`, `rich`, `jsonlines`

### LlamaFactory Environment Details

- **Activation**: `source /home/zc/wmt26/.venvs/llamafactory/bin/activate`
- `llamafactory-cli` is available at `/home/zc/wmt26/.venvs/llamafactory/bin/llamafactory-cli`
- Note: `llamafactory-cli --help` is not a valid subcommand, but the CLI prints usage and `llamafactory-cli version` / `llamafactory-cli train` work.

### OPD / verl / vLLM / sglang Environment Details

- **Activation**: `source /data/wyt/miniconda3/etc/profile.d/conda.sh && conda activate /home/zc/wmt26/.conda/envs/verl`
- Checked imports:
  - `vllm` 0.11.0 ✅
  - `sglang` 0.5.2 ✅
  - `math_verify` (math-verify 0.9.0) ✅
  - `verl` ❌ `ModuleNotFoundError: No module named 'verl'`

### Known Warnings / Issues

| Issue | Severity | Details |
|---|---|---|
| `verl` not importable | 🔴 needs fix | The `verl` package is present as source code under `repos/thunlp_opd/verl` but is not installed into the conda environment. `pip show verl` reports "not installed". OPD smoke training will fail until this is resolved. Likely need to install verl from source (`pip install -e repos/thunlp_opd/verl`) or ensure the install script did so. |
| `pynvml` deprecation warning | 🟡 low | OPD/verl env prints `FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead.` when importing `torch.cuda`. Import still succeeds; can be ignored for now. |
| numpy dependency conflicts | 🟡 low | pip resolver previously reported numpy version mismatches between opencv, cupy-cuda12x, outlines, numba, mistral-common. Current imports pass; may surface at OPD runtime. |

## Base Model

| Item | Value |
|---|---|
| Standard path | `/home/zc/wmt26/models/base/Qwen3.5-2B` |
| Size | ~4.3 GB (`model.safetensors-00001-of-00001.safetensors`) |
| `model_type` | `qwen3_5` |
| Tokenizer | `Qwen2Tokenizer` |
| Status | ✅ config and tokenizer load successfully |

## External Repositories

| Repository | Path | origin | upstream | HEAD |
|---|---|---|---|---|
| official_eval | `repos/official_eval` | `worthingzhang/llms-lim-res-eval-2026` | `TUM-NLP/llms-limited-resources2026` | `3e2bd75cc6b1c153b7a9418a6bbb118c71f543e5` |
| thunlp_opd | `repos/thunlp_opd` | `worthingzhang/OPD` | `thunlp/OPD` | `1fd6cca846126af90d82ef122e8af261f59d2d37` |

### Repository Notes

- Both repositories have the expected `origin` and `upstream` remotes configured.
- `repos/official_eval` working tree is clean.
- `repos/thunlp_opd` has an untracked file: `verl/flash_attn-2.8.1+cu12torch2.8cxx11abiFALSE-cp312-cp312-linux_x86_64.whl`. This is a prebuilt FlashAttention wheel placed inside the external repo during setup. Per project rules, large binary artifacts should not live in `repos/`; consider moving it to `data/cache/` or another ignored location.

## Project Structure

All expected top-level directories are present:

```text
configs/      data/         docs/         models/       repos/
runs/         scripts/      submissions/  .venv/        .venvs/
.conda/       .claude/
```

Git working tree is clean (no uncommitted changes in tracked project files).

## Verification Commands

### Main / Eval

```bash
source /home/zc/wmt26/.venv/bin/activate
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda_available:", torch.cuda.is_available())
print("cuda_runtime:", torch.version.cuda)
print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CUDA not available")
PY
```

### LlamaFactory

```bash
source /home/zc/wmt26/.venvs/llamafactory/bin/activate
llamafactory-cli version
```

### OPD / verl

```bash
source /data/wyt/miniconda3/etc/profile.d/conda.sh
conda activate /home/zc/wmt26/.conda/envs/verl
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda_available:", torch.cuda.is_available())
import vllm, sglang, math_verify
print("imports ok")
import verl  # currently fails
print("verl ok")
PY
```

## Next Steps

1. **Fix `verl` import** before any OPD smoke training. Options:
   - Install verl from source: `pip install -e /home/zc/wmt26/repos/thunlp_opd/verl`
   - Or re-run the OPD setup script and verify the install step actually installs verl.
2. **Clean up `repos/thunlp_opd/verl/flash_attn-*.whl`** by moving it to an ignored cache directory.
3. **Confirm official evaluation task names** in `configs/eval/official_all_tasks.yaml`.
4. **Proceed to CPT/SFT data format checks and smoke training** once the above are resolved.
