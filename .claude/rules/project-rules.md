# Project Rules & Pitfalls

## Do

- Treat CPT, SFT, and OPD as **parallel training operators**, not a fixed pipeline.
- Keep data in `data/`, models in `models/`, and run artifacts in `runs/`.
- Register every produced model in `models/registry/models.jsonl`.
- Register every train/eval run in `runs/train_registry.csv` and `runs/eval_registry.csv`.
- Load `configs/env/mirrors.env` automatically in scripts; only `source` it manually when debugging.
- Use absolute paths when passing data/model paths to external backends.

## Don't

- Don't copy data or model checkpoints into `repos/thunlp_opd/` or `repos/official_eval/`.
- Don't modify `repos/thunlp_opd/` or `repos/official_eval/` source code unless absolutely necessary; prefer passing args via `scripts/` and `configs/`.
- Don't commit large files (`.pt`, `.bin`, `.safetensors`, `.parquet`, logs, raw/interim/processed data, model weights, run outputs).
- Don't auto-push git commits; ask first.
- Don't install OPD/verl, vLLM, or sglang unless explicitly requested.
- **When patching an external backend, prefer task-specific YAML/utils fixes over global framework changes**, and record the reason + commit hash in `docs/EXTERNAL_REPOS.md`.
- **Never use `acc` as a metric for `generate_until` tasks**; use `exact_match` or another metric that returns a scalar per sample.

## Pitfalls

- **PyTorch CUDA version mismatch**: uv may install `torch+cu130` which is incompatible with NVIDIA driver 535 / CUDA 12.2. Always pin torch to CUDA 12.4 via `--index-url https://download.pytorch.org/whl/cu124`.
- **Environment mix-ups**: `.venv` is for main project + official eval; `.venvs/llamafactory` is for CPT/SFT; `.conda/envs/verl` is for OPD/verl/vLLM/sglang. Don't install packages into the wrong environment.
- **LlamaFactory dataset path**: The factory reads datasets from paths configured in the training YAML; keep `dataset_dir` pointing to `data/processed/` and maintain `dataset_info.json` there.
- **Network timeouts**: Large packages (torch, triton) may time out. Use `configs/env/mirrors.env` timeouts and retry.
- **HF cache path mismatch**: `configs/env/mirrors.env` sets `HF_HOME`, but if the file is not sourced, HuggingFace tools may use the default `~/.cache/huggingface`. Always source the mirror config or let project scripts auto-load it.
- **OPD/verl dependency conflicts**: The official install script may produce pip dependency conflicts (especially numpy versions). Verify imports and `torch.cuda.is_available()` after install, but don't blindly reinstall unless a runtime error occurs.
- **`parallelize=True` incompatible with custom architectures**: Qwen3.5-2B's custom attention causes device mismatch with `parallelize=True`. Use single-GPU `cuda:0` and tune `batch_size` instead.
- **RTX 4000 series NCCL**: Set `NCCL_P2P_DISABLE=1` and `NCCL_IB_DISABLE=1` when running multi-GPU-aware frameworks on RTX 4090s to avoid the "RTX 4000 series doesn't support faster communication broadband" error.
