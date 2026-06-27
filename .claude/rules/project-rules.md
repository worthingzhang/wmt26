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
- **Don't treat `repos/official_eval`'s `upstream` as the data repo.** `upstream` = official **eval-code** `TUM-NLP/llms-lim-res-eval-2026`; `data` = official **data** repo `TUM-NLP/llms-limited-resources2026`. Two different repos.
- **Don't keep local metric forks in `official_eval`** — follow official `upstream` (pure official 口径). The old MR patch `1e6ab97b` is superseded by official `8be394d6` and was dropped (tag `pre-align-1e6ab97b`).
- **Don't use devsplit few-shot v1/v2 as an official baseline** — they are experimental; v2's MT→deu / SC / GC are invalid/regressed. Official mainline = zero-shot via `repos/official_eval` (`sorbian_dev` group + QA).

## Pitfalls

- **PyTorch CUDA version mismatch**: uv may install `torch+cu130` which is incompatible with NVIDIA driver 535 / CUDA 12.2. Always pin torch to CUDA 12.4 via `--index-url https://download.pytorch.org/whl/cu124`.
- **Environment mix-ups**: `.venv` is for main project + official eval; `.venvs/llamafactory` is for CPT/SFT; `.conda/envs/verl` is for OPD/verl/vLLM/sglang. Don't install packages into the wrong environment.
- **LlamaFactory dataset path**: The factory reads datasets from paths configured in the training YAML; keep `dataset_dir` pointing to `data/processed/` and maintain `dataset_info.json` there.
- **Network timeouts**: Large packages (torch, triton) may time out. Use `configs/env/mirrors.env` timeouts and retry.
- **HF cache path mismatch**: `configs/env/mirrors.env` sets `HF_HOME`, but if the file is not sourced, HuggingFace tools may use the default `~/.cache/huggingface`. Always source the mirror config or let project scripts auto-load it.
- **OPD/verl dependency conflicts**: The official install script may produce pip dependency conflicts (especially numpy versions). Verify imports and `torch.cuda.is_available()` after install, but don't blindly reinstall unless a runtime error occurs.
- **`parallelize=True` incompatible with custom architectures**: Qwen3.5-2B's custom attention causes device mismatch with `parallelize=True`. Use single-GPU `cuda:0` and tune `batch_size` instead.
- **RTX 4000 series NCCL**: Set `NCCL_P2P_DISABLE=1` and `NCCL_IB_DISABLE=1` when running multi-GPU-aware frameworks on RTX 4090s to avoid the "RTX 4000 series doesn't support faster communication broadband" error.
- **tmux config compatibility on Ubuntu**: `allow-passthrough` is only available in tmux >= 3.3. On tmux 3.2a (default on this system) it causes tmux to error/restart and can silently kill attached training sessions. Keep it commented out in `~/.tmux.conf` for long-running training sessions.
- **`.gitignore` for a symlinked dir needs NO trailing slash**: `repos/official_eval/llms-limited-resources2026` is a symlink (→ `data/raw/...`), not a real dir; pattern `foo/` won't match a symlink — use bare `llms-limited-resources2026`.
- **Dev-server GitHub is reachable but flaky**: direct `git`/`curl` to github.com usually works (~1s) but occasionally spikes/times out; retry with `--connect-timeout`. Fallback proxy = Windows reverse tunnel: run `ssh -N -T WMT-codex-tunnel` on Windows (exposes server `127.0.0.1:17890` → Windows Clash `7897`), then `git -c http.https://github.com/.proxy=http://127.0.0.1:17890 ...` (github-only; leaves pip/hf mirrors alone). Never `export http_proxy` globally.
- **eval baselines are only comparable at fixed (eval-code, data) commits**: record both in `run.yaml`. Current alignment: eval-code `711a2b4f`, data `2b712ac6`.
