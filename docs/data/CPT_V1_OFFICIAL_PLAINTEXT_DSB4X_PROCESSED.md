# CPT V1 Official Plaintext DSB4X Processed Data

- created_at: 2026-06-19T16:29:57.622365+00:00
- output: `data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl`
- hsb_input: `data/interim/sorbian/cpt_v1_official_mono/mono_hsb_clean.jsonl`
- dsb_input: `data/interim/sorbian/cpt_v1_official_mono/mono_dsb_clean.jsonl`
- hsb_repeat: 1
- dsb_repeat: 4
- shuffle: true
- seed: 202606

## Counts

- hsb unique kept: 2279050
- dsb unique kept: 386413
- hsb output rows: 2279050
- dsb output rows: 1545652
- total output rows: 3824702

## Token Estimate

- tokenizer: `/home/zc/wmt26/models/base/Qwen3.5-2B`
- method: global reservoir sample
- sample size: 20000
- estimated total tokens: 135266515
- sample avg tokens / row: 35.37
- sample token length distribution: `{'p50': 31, 'p90': 62, 'p95': 74, 'p99': 103, 'max': 547}`
- scaled interim exact tokens: 134934277
- scaled hsb tokens: 80928065 (59.98%)
- scaled dsb tokens: 54006212 (40.02%)

## Filtering

Light filtering was applied during processed-data construction: empty text, replacement character rows, HTML/XML-heavy rows, pure URL/path rows, and symbol-only rows were removed.

Filtered counts are recorded in the manifest. Final training JSONL contains only the `text` field for LlamaFactory `stage=pt`.

## Notes

- Input interim data had already been exact-deduplicated before this stage.
- DSB repeat is intentional sampling, so no repeat-after-dedup was run.
- This dataset uses only official Sorbian plaintext CPT data: hsb/dsb monolingual train plus hsb/dsb target-side parallel train text.
