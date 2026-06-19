# Raw Data Download Status

Execution time: 2026-06-18T19:23:24+08:00

Project path: `/home/zc/wmt26`

## Scope

This stage only created raw-data directories, downloaded or registered raw
sources, and recorded integrity metadata.

No data cleaning was performed. No `interim` or `processed` training files were
generated. No LlamaFactory command was run. No model training was started.

## Created Directories

- `data/raw/official`
- `data/raw/external/fineweb2`
- `data/raw/external/wikipedia`
- `data/raw/instruction`
- `data/manifests`
- `scripts/data/download`
- `logs/data_download`
- `docs/data`

## Official Git Repositories

| Source | Local path | Commit | Size | Status |
| --- | --- | --- | --- | --- |
| llms-limited-resources2026 | `data/raw/official/llms-limited-resources2026` | `cc3579a45ae17a62b77e7b119b88749c6f41f7db` | 138M | downloaded |
| llms-limited-resources2025 | `data/raw/official/llms-limited-resources2025` | `9310fa5b6e791dcba1613842dd03c9fde67ef620` | 282M | downloaded |
| WMT22_UnsupVeryLowResMT_Data | `data/raw/official/WMT22_UnsupVeryLowResMT_Data` | `3c71b5147b52adb9c2c8ab752babe53fa6690d5b` | 185M | downloaded |

Git LFS was checked for each repository by the download script. No LFS files
were detected in the completed run.

Official download log:

- `logs/data_download/official_wmt_raw_20260618_190102.log`

## Wikipedia Dumps

| Source | Local path | Bytes | SHA256 | Status |
| --- | --- | ---: | --- | --- |
| hsbwiki latest pages-articles | `data/raw/external/wikipedia/hsbwiki/hsbwiki-latest-pages-articles.xml.bz2` | 11672324 | `d060e510ce4b3aed5e033b367c21f0628f5daac06a9d9527910157e8918a667e` | downloaded |
| dsbwiki latest pages-articles | `data/raw/external/wikipedia/dsbwiki/dsbwiki-latest-pages-articles.xml.bz2` | 3933467 | `0027f1b85a204e10cb14a32e81edd0dd312462551ef00c074136c7210b57c7a5` | downloaded |

The dumps were not decompressed and WikiExtractor was not run.

Wikipedia download log:

- `logs/data_download/wikipedia_sorbian_raw_20260618_190324.log`

## FineWeb-2

Dataset: `HuggingFaceFW/fineweb-2`

Status: dry-run only. No documents were exported.

The dry-run found explicit Sorbian candidate configs:

- Upper Sorbian: `hsb_Latn`
- Lower Sorbian: `dsb_Latn`

Candidate list:

- `data/manifests/fineweb2_config_candidates.txt`

Future non-dry-run exports should use streaming with an explicit limit, for
example `--max-docs 50000 --no-dry-run`, and should not full-download the
dataset.

## Instruction Data

Status: registered only. No instruction dataset was downloaded.

Candidate registry:

- `data/manifests/instruction_source_candidates.yaml`

Sources still requiring verification:

- Magpie
- Aya
- EuroBlocks
- OpenAssistant2
- FLAN v2

Before any instruction export, verify exact dataset id, license, language
fields, conversation format, and sampling plan.

## Manifests

- `data/manifests/raw_sources.yaml`
- `data/manifests/raw_checksums.sha256`
- `data/manifests/fineweb2_config_candidates.txt`
- `data/manifests/instruction_source_candidates.yaml`

## Raw Data Size

Current raw-data size by top-level area:

- `data/raw/official`: 605M
- `data/raw/external`: 15M
- `data/raw/instruction`: 8.0K

Total apparent raw-data size: 737M.

## Next Steps

- Design interim cleaning scripts without mutating raw data.
- Define dev/test leakage filtering before generating CPT training data.
- Decide whether FineWeb-2 Sorbian samples enter only `tartu_like_full` or also
  another controlled experiment.
- Verify instruction dataset IDs and licenses before sampling instruction data.
