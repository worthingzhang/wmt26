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
| OPD / verl / vLLM / sglang | `.conda/envs/verl` | 3.12.13 | 2.8.0+cu128 | 12.8 | ✅ True | verl 0.7.0.dev, vllm 0.11.0, sglang 0.5.2, math-verify 0.9.0 | ✅ ready |

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
- **verl installation**: installed in editable mode from source with `pip install -e . --no-deps` inside `/home/zc/wmt26/repos/thunlp_opd/verl`. This avoids re-resolving or overwriting the already-installed `torch`, `vllm`, `sglang`, and other heavy dependencies.
- Checked imports:
  - `verl` 0.7.0.dev ✅
  - `vllm` 0.11.0 ✅
  - `sglang` 0.5.2 ✅
  - `math_verify` (math-verify 0.9.0) ✅
- `torch.cuda.is_available()` remains `True` after the verl install.

### FlashAttention Wheel Cleanup

The prebuilt FlashAttention wheel that was originally placed at `repos/thunlp_opd/verl/flash_attn-2.8.1+cu12torch2.8cxx11abiFALSE-cp312-cp312-linux_x86_64.whl` has been moved to `data/cache/wheels/`. The root `.gitignore` now includes `*.whl` to prevent future wheel files from being tracked.

### Known Warnings / Issues

| Issue | Severity | Details |
|---|---|---|
| `verl` not importable | ✅ resolved | Installed `verl` from source with `--no-deps`; `import verl` now succeeds and reports version `0.7.0.dev`. |
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
- `repos/thunlp_opd` working tree is clean; the previously untracked `flash_attn-*.whl` has been moved out of the external repo.

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
import verl, vllm, sglang, math_verify
print("imports ok")
PY
```

## Baseline Evaluation

### Smoke Evaluation

A baseline smoke evaluation was successfully run on the base model using the official_eval backend.

| Item | Value |
|---|---|
| eval_id | `eval_base_qwen35_2b_smoke` |
| model_id | `base_qwen35_2b` |
| model_path | `/home/zc/wmt26/models/base/Qwen3.5-2B` |
| task | `hsbqa` (Upper Sorbian QA group) |
| limit | 5 samples per subtask |
| batch_size | 1 |
| device | `cuda:0` |
| dtype | `bfloat16` |
| result path | `runs/eval/eval_base_qwen35_2b_smoke/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-07-47.986261.json` |
| status | ✅ success |

#### Smoke Results (limit=5)

| Task / Group | acc |
|---|---|
| hsbqa (group) | 0.85 |
| hsbqa::hsbqa-a1 | 1.00 |
| hsbqa::hsbqa-a2 | 1.00 |
| hsbqa::hsbqa-b1 | 0.60 |
| hsbqa::hsbqa-b2 | 0.80 |

### Full Baseline Evaluation

A full baseline evaluation was attempted on all Sorbian tasks. The QA portion completed successfully, but the generative portion failed due to a metric aggregation bug in official_eval.

| Item | Value |
|---|---|
| eval_id | `eval_base_qwen35_2b_full` |
| model_id | `base_qwen35_2b` |
| model_path | `/home/zc/wmt26/models/base/Qwen3.5-2B` |
| QA tasks | `hsbqa`, `dsbqa` |
| Generative tasks | `sorbian_dev` (failed) |
| batch_size | 1 |
| device | `cuda:0` (single GPU; `parallelize=True` incompatible) |
| dtype | `bfloat16` |
| enable_thinking | `False` for generative tasks |
| QA result path | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| status | ⚠️ partial: QA success, generative failed |

#### Full QA Results (no limit)

| Group | acc |
|---|---|
| hsbqa | 0.5159 |
| dsbqa | 0.4682 |

#### Generative Failure

- **Failed task group**: `sorbian_dev`
- **Error**: `TypeError: unsupported operand type(s) for +: 'int' and 'list'`
- **Location**: `repos/official_eval/lm_eval/api/metrics.py:36` (`mean` aggregation)
- **Root cause**: The custom `chrf_pp` metric returns a list instead of a scalar for some samples, causing aggregation to fail.
- **Log**: `runs/eval/eval_base_qwen35_2b_full/gen.log`

### Notes

- The base model loaded successfully with `trust_remote_code=True` and `dtype=bfloat16`.
- RTX 4000 series NCCL issue was avoided by setting `NCCL_P2P_DISABLE=1` and `NCCL_IB_DISABLE=1`.
- `parallelize=True` is incompatible with Qwen3.5-2B's custom attention (device mismatch error), so the full baseline ran on a single GPU.
- The official evaluation data repo (`TUM-NLP/llms-limited-resources2026`) was cloned to `data/raw/llms-limited-resources2026` so the relative paths in task configs resolve correctly.
- Scripts saved at:
  - `scripts/eval/eval_base_smoke.sh`
  - `scripts/eval/eval_base_full.sh`

## Next Steps

1. ✅ `verl` import fixed.
2. ✅ FlashAttention wheel moved out of `repos/thunlp_opd/`.
3. ✅ Baseline official_eval smoke completed successfully.
4. ⚠️ Full baseline QA completed; generative tasks blocked by official_eval `chrf_pp` metric bug.
5. **Decide whether to patch `repos/official_eval/lm_eval/api/metrics.py` or report upstream** to unblock generative baseline.
6. **Proceed to CPT/SFT data format checks and smoke training**.
7. **OPD smoke training** can now be attempted when ready.

No environments were reinstalled, no models were downloaded, and no training was performed.
