# CPT V1 Official Plaintext DSB4X Status

## Data

- processed file: `data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl`
- line count: 3,824,702
- hsb repeat: 1
- dsb repeat: 4
- estimated tokens: 135,266,515 by 20k-row tokenizer sample; 134,934,277 by scaled interim exact token stats
- token ratio: hsb 59.98%, dsb 40.02% by scaled interim exact token stats
- manifest: `data/manifests/cpt_v1_official_plaintext_dsb4x_processed.yaml`
- build report: `docs/data/CPT_V1_OFFICIAL_PLAINTEXT_DSB4X_PROCESSED.md`
- filtering: removed empty/replacement-char/HTML-heavy/pure URL/path/symbol-only rows during processed construction

## LlamaFactory Dataset

- dataset_info path: `data/processed/llamafactory/dataset_info.json`
- dataset name: `cpt_v1_official_plaintext_dsb4x`
- dataset format: LlamaFactory `stage=pt` JSONL with one `text` field per row
- dataset entry:
  - `file_name`: `cpt/cpt_v1_official_plaintext_dsb4x.jsonl`
  - `columns.prompt`: `text`

## Training Configs

- smoke config: `configs/train/cpt/cpt_v1_official_plaintext_dsb4x_smoke.yaml`
- probe4096 config: `configs/train/cpt/cpt_v1_official_plaintext_dsb4x_probe4096.yaml`
- pilot config: `configs/train/cpt/cpt_v1_official_plaintext_dsb4x_pilot.yaml`
- full config: `configs/train/cpt/cpt_v1_official_plaintext_dsb4x_full.yaml`
- finetuning type: `full`
- stage: `pt`
- distributed strategy: DeepSpeed ZeRO-3
- smoke cutoff: 1024, reduced from 4096 after full DDP and non-sharded 1024 smoke hit GPU OOM on 24GB cards
- probe4096 cutoff: 4096, verifies that ZeRO-3 can fit the full sequence length before pilot/full
- pilot/full cutoff: 4096, left for manual review before longer runs

## Smoke Training

- status: success
- command: `bash scripts/train/run_cpt_v1_plaintext_dsb4x_smoke.sh`
- log path: `logs/train/cpt_v1_official_plaintext_dsb4x/smoke.log`
- output model path: `models/cpt/cpt_v1_official_plaintext_dsb4x_smoke`
- checkpoints: `checkpoint-10`, `checkpoint-20`, final output directory
- final loss: 4.086
- train runtime: 0:02:03.29
- train samples per second: 1.298
- train steps per second: 0.162

## Probe 4096 Training

- status: success
- cutoff_len: 4096
- max_steps: 50
- per_device_train_batch_size: 1
- gradient_accumulation_steps: 4
- deepspeed: ZeRO-3 (`repos/thunlp_opd/LlamaFactory/examples/deepspeed/ds_z3_config.json`)
- output model path: `models/cpt/cpt_v1_official_plaintext_dsb4x_probe4096`
- log path: `logs/train/cpt_v1_official_plaintext_dsb4x/probe4096.log`
- final loss: 3.4468
- runtime: 0:20:24.36 (1224.36 s)
- seconds per step: ~24.49 s/step; train_steps_per_second: 0.041
- checkpoint status: `checkpoint-25` and `checkpoint-50` saved; final model saved to output directory
- warnings/errors:
  - non-fatal: linear attention fast path libraries are not installed, falling back to torch implementation
  - non-fatal: tokenizer PAD/EOS values were aligned with tokenizer values during training
  - first launch attempt silently exited before step 1; re-launched in tmux with `overwrite_output_dir=true` and completed successfully

## Environment Notes

- fixed `torchaudio` in `.venvs/llamafactory` from incompatible `2.11.0` to `2.7.0+cu126` to match `torch==2.7.0+cu126`
- installed `deepspeed==0.18.4` from LlamaFactory requirements
- first smoke attempt failed before training because incompatible `torchaudio` required `libcudart.so.13`
- full DDP smoke attempts reached training but OOMed on 24GB GPUs; ZeRO-3 was required for full CPT

## Warnings / Errors

- non-fatal: `warmup_ratio` is deprecated and should eventually be replaced with `warmup_steps`
- non-fatal: linear attention fast path libraries are not installed, so training falls back to torch implementation
- non-fatal: tokenizer PAD/EOS values were aligned with tokenizer values during training
- non-fatal: no `eval_loss` was plotted because smoke has no eval split

## Full CPT Training

### Plan

- run_id: `cpt_v1_official_plaintext_dsb4x_full`
- base_model: `/home/zc/wmt26/models/base/Qwen3.5-2B`
- dataset: `cpt_v1_official_plaintext_dsb4x`
- processed_file: `data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl`
- estimated_tokens: ~135M (135,266,515 by tokenizer sample; 134,934,277 by scaled interim exact stats)
- hsb/dsb ratio: 59.98% / 40.02%
- cutoff_len: 4096
- packing: true
- deepspeed: ZeRO-3 (`repos/thunlp_opd/LlamaFactory/examples/deepspeed/ds_z3_config.json`)
- max_steps: 1000
- per_device_train_batch_size: 1
- gradient_accumulation_steps: 4
- global tokens per step estimate: 8 × 1 × 4 × 4096 = 131,072 tokens
- expected runtime: ~7–8 hours (1000 steps × ~25 s/step, plus checkpoint overhead)
- output_dir: `/home/zc/wmt26/models/cpt/cpt_v1_official_plaintext_dsb4x_full`
- log_path: `/home/zc/wmt26/logs/train/cpt_v1_official_plaintext_dsb4x/full.log`

### Launch Attempt 1 (automated)

- launch_time: 2026-06-20 05:21:46
- tmux_session: `cpt-v1-dsb4x-full`
- command: `tmux new -d -s cpt-v1-dsb4x-full "bash scripts/train/run_cpt_v1_plaintext_dsb4x_full.sh"`
- git_status_summary: `docs/train/CPT_V1_OFFICIAL_PLAINTEXT_DSB4X_STATUS.md` modified; `models/cpt/cpt_v1_official_plaintext_dsb4x_probe4096/` untracked
- preflight_checks:
  - processed data exists: 385M, 3,824,702 lines
  - config and script validated
  - output directory did not exist
  - 8× RTX 4090 idle, 1.4T disk available
- result: **failed / silently exited**
- completed_steps: 0 / 1000
- status: process initialized DeepSpeed ZeRO-3 and reached `Total optimization steps = 1,000`, then silently exited before step 1
- warnings/errors:
  - no OOM in `dmesg`
  - no Traceback/RuntimeError in log
  - likely tmux session instability related to `.tmux.conf` `allow-passthrough` incompatibility with tmux 3.2a

### Launch Attempt 2 (manual, user-run)

- status: **running**
- launch_time: 2026-06-20 16:39:47
- tmux_session: `cpt-v1-dsb4x-full`
- command: `cd /home/zc/wmt26 && bash scripts/train/run_cpt_v1_plaintext_dsb4x_full.sh`
- note: run inside tmux after fixing `.tmux.conf`; training passed step 0 and is progressing normally
- current_progress: step 12 / 1000, loss ~4.40, ~24 s/step

## Next Step

- Monitor full CPT to 1000 steps.
- Do not start evaluation until full CPT finishes and is reviewed.
