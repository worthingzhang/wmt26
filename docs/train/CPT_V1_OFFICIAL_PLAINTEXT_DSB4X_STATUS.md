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
- pilot config: `configs/train/cpt/cpt_v1_official_plaintext_dsb4x_pilot.yaml`
- full config: `configs/train/cpt/cpt_v1_official_plaintext_dsb4x_full.yaml`
- finetuning type: `full`
- stage: `pt`
- distributed strategy: DeepSpeed ZeRO-3
- smoke cutoff: 1024, reduced from 4096 after full DDP and non-sharded 1024 smoke hit GPU OOM on 24GB cards
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

## Next Step

- If smoke succeeded, run pilot with `bash scripts/train/run_cpt_v1_plaintext_dsb4x_pilot.sh`.
- Before pilot/full, review whether `cutoff_len: 4096` fits with ZeRO-3 on 8x RTX 4090; reduce pilot cutoff or add more memory optimization if needed.
- Do not start full CPT until the pilot run is reviewed.
