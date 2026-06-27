# WMT26 Sorbian Data Download Audit Report

**Generated**: 2026-06-27
**Scope**: Comprehensive audit of all downloaded data assets for WMT26 Sorbian project
**Method**: Read-only sampling (no files modified, no training launched, no data deleted)

---

## 1. Executive Summary

### Confirmed Present
- **WMT26 official data**: Complete — MT (3 dev directions + 3 train directions + 2 monolingual), QA, SC, GC, MR all present
- **WMT25 official data**: Complete — MT train/dev/test + monolingual + QA dev/test for both hsb and dsb
- **WMT22 historical data**: Complete — parallel (hsb-de 2020/2021/2022, dsb-de, hsb-dsb) + monolingual (hsb/dsb) + devtest
- **FineWeb2 hsb/dsb**: Present — 44,293 hsb + 6,798 dsb documents (streaming sample)
- **Wikipedia hsb/dsb**: Present — raw XML dumps (33,539 hsb pages, 9,839 dsb pages)
- **Instruction data**: Present — Magpie MT (50k), Aya (6.7k), OA2 (50k), FLAN v2 (50k)
- **CPT processed data**: Present — 3,824,702 lines, hash-filtered for heldout contamination

### Missing / Not Found
- **EuroBlocks**: Not found on HuggingFace Hub under any known variant
- **WMT26 MT train**: de-hsb, de-dsb, hsb-dsb train CSVs exist but hsb-de, dsb-de, dsb-hsb **train** files are absent (only dev JSONLs for these reverse directions)
- **Processed records with metadata**: `data/processed/records/` does not exist; CPT data is `{"text": ...}` only

### Highest Risk
- **Wikipedia data is raw XML** — needs WikiExtractor or equivalent cleaning before CPT use
- **FineWeb2 data is raw Common Crawl** — needs dedup and quality filtering before CPT use
- **WMT22 monolingual has significant overlap** with WMT25 data (acknowledged in WMT25 README)

---

## 2. Data Inventory Table

| dataset_id | source | year | task_type | lang | direction | split | path | format | n_rows | size | license | usage | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| wmt26_mt_de-hsb_dev | TUM-NLP | 2026 | MT | hsb | de→hsb | dev | `data/raw/llms-limited-resources2026/Sorbian/MT/de-hsb_mt_dev.jsonl` | JSONL | 4,000 | 1.1M | (see README) | eval_only | columns: dataset_id, sent_id, de, hsb |
| wmt26_mt_de-dsb_dev | TUM-NLP | 2026 | MT | dsb | de→dsb | dev | `data/raw/llms-limited-resources2026/Sorbian/MT/de-dsb_mt_dev.jsonl` | JSONL | 4,000 | 947K | (see README) | eval_only | columns: dataset_id, sent_id, de, dsb |
| wmt26_mt_hsb-dsb_dev | TUM-NLP | 2026 | MT | hsb,dsb | hsb→dsb | dev | `data/raw/llms-limited-resources2026/Sorbian/MT/hsb-dsb_mt_dev.jsonl` | JSONL | 4,000 | 1.2M | (see README) | eval_only | columns: dataset_id, sent_id, hsb, dsb |
| wmt26_train_de-hsb | TUM-NLP | 2026 | MT | hsb | de→hsb | train | `data/raw/llms-limited-resources2026/Sorbian/MT/train_de-hsb_2026.csv` | CSV | 23,117 | 2.8M | (see README) | train | columns: de, hsb |
| wmt26_train_de-dsb | TUM-NLP | 2026 | MT | dsb | de→dsb | train | `data/raw/llms-limited-resources2026/Sorbian/MT/train_de-dsb_2026.csv` | CSV | 30,561 | 3.5M | (see README) | train | columns: de, dsb |
| wmt26_train_hsb-dsb | TUM-NLP | 2026 | MT | hsb,dsb | hsb→dsb | train | `data/raw/llms-limited-resources2026/Sorbian/MT/train_hsb-dsb_2026.csv` | CSV | 67,846 | 8.3M | (see README) | train | columns: hsb, dsb |
| wmt26_mono_hsb | TUM-NLP | 2026 | mono | hsb | — | train | `data/raw/llms-limited-resources2026/Sorbian/MT/hsb_monolingual_2026.csv` | CSV | 512,672 | 54M | (see README) | train | columns: id, year, hsb |
| wmt26_mono_dsb | TUM-NLP | 2026 | mono | dsb | — | train | `data/raw/llms-limited-resources2026/Sorbian/MT/dsb_monolingual_2026.csv` | CSV | 38,029 | 3.9M | (see README) | train | columns: id, year, dsb |
| wmt26_qa_hsb | TUM-NLP | 2026 | QA | hsb | — | dev | `data/raw/llms-limited-resources2026/Sorbian/QA/hsb_qa_dev.jsonl` | JSONL | 158 | 243K | (see README) | eval_only | levels: A1-B2 |
| wmt26_qa_dsb | TUM-NLP | 2026 | QA | dsb | — | dev | `data/raw/llms-limited-resources2026/Sorbian/QA/dsb_qa_dev.jsonl` | JSONL | 158 | 238K | (see README) | eval_only | levels: A1-B2 |
| wmt26_sc_hsb | TUM-NLP | 2026 | SC | hsb | — | dev | `data/raw/llms-limited-resources2026/Sorbian/SC/hsb_sc_dev.jsonl` | JSONL | 2,000 | 667K | (see README) | eval_only | spell checking |
| wmt26_sc_dsb | TUM-NLP | 2026 | SC | dsb | — | dev | `data/raw/llms-limited-resources2026/Sorbian/SC/dsb_sc_dev.jsonl` | JSONL | 2,000 | 648K | (see README) | eval_only | spell checking |
| wmt26_gc_hsb | TUM-NLP | 2026 | GC | hsb | — | dev | `data/raw/llms-limited-resources2026/Sorbian/GC/hsb_gc_dev.jsonl` | JSONL | 2,000 | 667K | (see README) | eval_only | grammar correction |
| wmt26_gc_dsb | TUM-NLP | 2026 | GC | dsb | — | dev | `data/raw/llms-limited-resources2026/Sorbian/GC/dsb_gc_dev.jsonl` | JSONL | 1,250 | 373K | (see README) | eval_only | grammar correction |
| wmt26_mr_hsb | TUM-NLP | 2026 | MR | hsb | — | dev | `data/raw/llms-limited-resources2026/Sorbian/MR/hsb_mr_dev.jsonl` | JSONL | 24 | 7.7K | (see README) | eval_only | math reasoning |
| wmt26_mr_dsb | TUM-NLP | 2026 | MR | dsb | — | dev | `data/raw/llms-limited-resources2026/Sorbian/MR/dsb_mr_dev.jsonl` | JSONL | 24 | 7.8K | (see README) | eval_only | math reasoning |
| wmt25_train_hsb | WITAJ | 2025 | MT | hsb | de→hsb | train | `data/raw/official/llms-limited-resources2025/Sorbian/hsb/MT/train.de-hsb.{hsb,de}` | TXT | 187,269 | 40M | CC BY-NC-SA 4.0 | train | parallel, one sentence/line |
| wmt25_train_dsb | WITAJ | 2025 | MT | dsb | de→dsb | train | `data/raw/official/llms-limited-resources2025/Sorbian/dsb/MT/train.de-dsb.{dsb,de}` | TXT | 171,963 | 31M | CC BY-NC-SA 4.0 | train | parallel, one sentence/line |
| wmt25_dev_hsb | WITAJ | 2025 | MT | hsb | de→hsb | dev | `data/raw/official/llms-limited-resources2025/Sorbian/hsb/MT/dev.de-hsb.{hsb,de}` | TXT | 3,999 | — | CC BY-NC-SA 4.0 | eval_only | |
| wmt25_dev_dsb | WITAJ | 2025 | MT | dsb | de→dsb | dev | `data/raw/official/llms-limited-resources2025/Sorbian/dsb/MT/dev.de-dsb.{dsb,de}` | TXT | 3,999 | — | CC BY-NC-SA 4.0 | eval_only | |
| wmt25_test_hsb | WITAJ | 2025 | MT | hsb | de→hsb | test | `data/raw/official/llms-limited-resources2025/Sorbian/hsb/MT/test.de-hsb.de` | TXT | 3,999 | — | CC BY-NC-SA 4.0 | eval_only | DO NOT use in training |
| wmt25_test_dsb | WITAJ | 2025 | MT | dsb | de→dsb | test | `data/raw/official/llms-limited-resources2025/Sorbian/dsb/MT/test.de-dsb.de` | TXT | 3,999 | — | CC BY-NC-SA 4.0 | eval_only | DO NOT use in training |
| wmt25_mono_witaj_hsb | WITAJ | 2025 | mono | hsb | — | train | `data/raw/official/llms-limited-resources2025/Sorbian/hsb/MT/witaj_hsb_monolingual.txt` | TXT | 1,071,722 | 100M | CC BY-NC-SA 4.0 | train | |
| wmt25_mono_wiki_hsb | WITAJ | 2025 | mono | hsb | — | train | `data/raw/official/llms-limited-resources2025/Sorbian/hsb/MT/wiki_hsb_monolingual.txt` | TXT | 47,758 | 4.5M | CC BY-NC-SA 4.0 | train | |
| wmt25_mono_witaj_dsb | WITAJ | 2025 | mono | dsb | — | train | `data/raw/official/llms-limited-resources2025/Sorbian/dsb/MT/witaj_dsb_monolingual.txt` | TXT | 120,500 | 11M | CC BY-NC-SA 4.0 | train | |
| wmt25_qa_hsb_dev | WITAJ | 2025 | QA | hsb | — | dev | `data/raw/official/llms-limited-resources2025/Sorbian/hsb/QA/HSB_{A1,A2,B1,B2}.{json,csv}` | JSON/CSV | 2,484 | — | CC BY-NC-SA 4.0 | eval_only | 4 levels |
| wmt25_qa_dsb_dev | WITAJ | 2025 | QA | dsb | — | dev | `data/raw/official/llms-limited-resources2025/Sorbian/dsb/QA/DSB_{A1,A2,B1,B2}.{json,csv}` | JSON/CSV | 2,484 | — | CC BY-NC-SA 4.0 | eval_only | 4 levels |
| wmt25_qa_hsb_test | WITAJ | 2025 | QA | hsb | — | test | `data/raw/official/llms-limited-resources2025/Sorbian/hsb/QA/test/test_HSB_{A1..C1}.{json,csv}` | JSON/CSV | — | — | CC BY-NC-SA 4.0 | eval_only | DO NOT use in training |
| wmt25_qa_dsb_test | WITAJ | 2025 | QA | dsb | — | test | `data/raw/official/llms-limited-resources2025/Sorbian/dsb/QA/test/test_DSB_{A1..C1}.{json,csv}` | JSON/CSV | — | — | CC BY-NC-SA 4.0 | eval_only | DO NOT use in training |
| wmt22_hsb-de_2020 | mariondimarco | 2020 | MT | hsb | hsb→de | train | `WMT22_UnsupVeryLowResMT_Data/train.hsb-de.{hsb,de}.gz` | TXT.gz | 60,000 | 3.8M | CC BY-NC-SA | train | |
| wmt22_hsb-de_2021 | mariondimarco | 2021 | MT | hsb | hsb→de | train | `WMT22_UnsupVeryLowResMT_Data/train2021.hsb-de.{hsb,de}.gz` | TXT.gz | 87,521 | 6.6M | CC BY-NC-SA | train | |
| wmt22_hsb-de_2022 | mariondimarco | 2022 | MT | hsb | hsb→de | train | `WMT22_UnsupVeryLowResMT_Data/HSB-DE_train.tsv.gz` | TSV.gz | 301,537 | 23M | CC BY-NC-SA | train | columns: hsb, de |
| wmt22_dsb-de | mariondimarco | 2022 | MT | dsb | dsb→de | train | `WMT22_UnsupVeryLowResMT_Data/40194_train_dsb_de.{dsb,de}.gz` | TXT.gz | 40,193 | 2.6M | CC BY-NC-SA | train | |
| wmt22_hsb-dsb | mariondimarco | 2022 | MT | hsb,dsb | hsb↔dsb | train | `WMT22_UnsupVeryLowResMT_Data/train_dsb_hsb_62564.{hsb,dsb}.gz` | TXT.gz | 62,564 | 3.4M | CC BY-NC-SA | train | |
| wmt22_devtest_hsb-de | mariondimarco | 2020 | MT | hsb | hsb→de | dev+test | `WMT22_UnsupVeryLowResMT_Data/devtest.tar.gz` | TXT.tar.gz | 4,000 | 262K | CC BY-NC-SA | eval_only | devel 2000 + test 2000 |
| wmt22_devtest_dsb-de | mariondimarco | 2022 | MT | dsb | dsb→de | dev+test | `WMT22_UnsupVeryLowResMT_Data/devtest.dsb-de.tgz` | TXT.tgz | — | 76K | CC BY-NC-SA | eval_only | |
| wmt22_devtest_hsb-dsb | mariondimarco | 2022 | MT | hsb,dsb | hsb↔dsb | dev+valid | `WMT22_UnsupVeryLowResMT_Data/devtest_dsb_hsb_2022.tar.gz` | TXT.tar.gz | — | 70K | CC BY-NC-SA | eval_only | |
| wmt22_valid_dsb-de | mariondimarco | 2022 | MT | dsb | dsb→de | valid | `WMT22_UnsupVeryLowResMT_Data/valid.{de,dsb}.gz` | TXT.gz | 1,353 | 47K | CC BY-NC-SA | eval_only | |
| wmt22_mono_hsb_1 | mariondimarco | ≤2022 | mono | hsb | — | train | `WMT22_UnsupVeryLowResMT_Data/HSB_monolingual.txt.gz` | TXT.gz | 436,579 | 18M | CC BY-NC-SA | train | |
| wmt22_mono_hsb_2 | mariondimarco | ≤2022 | mono | hsb | — | train | `WMT22_UnsupVeryLowResMT_Data/sorbian_institute_monolingual.hsb.gz` | TXT.gz | 339,822 | 16M | CC BY-NC-SA | train | |
| wmt22_mono_hsb_3 | mariondimarco | ≤2022 | mono | hsb | — | train | `WMT22_UnsupVeryLowResMT_Data/witaj_monolingual.hsb.gz` | TXT.gz | 222,027 | 8.1M | CC BY-NC-SA | train | |
| wmt22_mono_hsb_4 | mariondimarco | ≤2022 | mono | hsb | — | train | `WMT22_UnsupVeryLowResMT_Data/web_monolingual.hsb.gz` | TXT.gz | 134,422 | 4.1M | CC BY-NC-SA | train | |
| wmt22_mono_dsb_1 | mariondimarco | ≤2022 | mono | dsb | — | train | `WMT22_UnsupVeryLowResMT_Data/mono.dsb.gz` | TXT.gz | 145,198 | 5.7M | CC BY-NC-SA | train | |
| wmt22_mono_dsb_2 | mariondimarco | ≤2022 | mono | dsb | — | train | `WMT22_UnsupVeryLowResMT_Data/66408_DSB_monolingual.txt.gz` | TXT.gz | 66,407 | 2.4M | CC BY-NC-SA | train | |
| wmt22_mono_dsb_3 | mariondimarco | ≤2022 | mono | dsb | — | train | `WMT22_UnsupVeryLowResMT_Data/8815_DSB_wikipedia_2021.txt.gz` | TXT.gz | 8,814 | 254K | CC BY-NC-SA | train | |
| fineweb2_hsb | HuggingFaceFW | — | mono | hsb | — | train | `data/raw/external/fineweb2/fineweb2_hsb_raw_50000.jsonl` | JSONL | 44,293 | 118M | (HF license) | train | Common Crawl, needs cleaning |
| fineweb2_dsb | HuggingFaceFW | — | mono | dsb | — | train | `data/raw/external/fineweb2/fineweb2_dsb_raw_50000.jsonl` | JSONL | 6,798 | 17M | (HF license) | train | Common Crawl, needs cleaning |
| wiki_hsb | Wikimedia | latest | mono | hsb | — | raw | `data/raw/external/wikipedia/hsbwiki/hsbwiki-latest-pages-articles.xml.bz2` | XML.bz2 | 33,539 pages | 12M | CC BY-SA | train | raw XML, needs WikiExtractor |
| wiki_dsb | Wikimedia | latest | mono | dsb | — | raw | `data/raw/external/wikipedia/dsbwiki/dsbwiki-latest-pages-articles.xml.bz2` | XML.bz2 | 9,839 pages | 3.8M | CC BY-SA | train | raw XML, needs WikiExtractor |
| magpie_mt | Magpie-Align | — | instruction | multi | — | train | `data/raw/instruction/magpie_mt.jsonl` | JSONL | 50,000 | 368M | (HF license) | train | 99.9% eng, has lang field |
| aya | CohereForAI | — | instruction | multi | — | train | `data/raw/instruction/aya.jsonl` | JSONL | 6,765 | 5.3M | (HF license) | train | eng/pol/ukr/rus/deu/srp |
| oasst2 | OpenAssistant | — | instruction | multi | — | train | `data/raw/instruction/oasst2.jsonl` | JSONL | 50,000 | 44M | Apache 2.0 | train | eng/rus/deu/ukr/pol |
| flan_v2_en | Muennighoff | — | instruction | eng | — | train | `data/raw/instruction/flan_v2_en.jsonl` | JSONL | 50,000 | 29M | (Apache 2.0) | train | English only |
| cpt_v1_processed | internal | — | CPT | hsb,dsb | — | train | `data/processed/llamafactory/cpt/cpt_v1_official_plaintext_dsb4x.jsonl` | JSONL | 3,824,702 | 384M | mixed | train | {"text": ...} only, hash-filtered |

---

## 3. TartuNLP Reproduction Coverage

| Component | Status | Evidence | Next Action |
|---|---|---|---|
| WMT25 current Sorbian mono (hsb) | **present** | witaj: 1,071,722 lines; wiki: 47,758 lines | Already in CPT v1 |
| WMT25 current Sorbian mono (dsb) | **present** | witaj: 120,500 lines | Already in CPT v1 |
| WMT25 current Sorbian parallel (de-hsb) | **present** | 187,269 pairs train | Already in CPT v1 (target side) |
| WMT25 current Sorbian parallel (de-dsb) | **present** | 171,963 pairs train | Already in CPT v1 (target side) |
| previous WMT20/21/22 Sorbian data | **present** | WMT22 repo: hsb-de 2020(60k)+2021(87k)+2022(301k), dsb-de(40k), hsb-dsb(62k), mono hsb(1.1M)+dsb(220k) | Already in CPT v1 |
| FineWeb2 hsb/dsb | **present** | hsb: 44,293 docs; dsb: 6,798 docs | Raw CC data. Needs dedup + quality filter before adding to CPT |
| Wikipedia hsb/dsb | **present** | hsb: 33,539 pages (12M); dsb: 9,839 pages (3.8M) | Raw XML dump. Needs WikiExtractor + cleaning |
| MT instructions de-hsb | **partial** | Magpie MT has minimal DE/HSB data | Need to generate from train pairs |
| MT instructions de-dsb | **partial** | Magpie MT has minimal DE/DSB data | Need to generate from train pairs |
| MT instructions hsb-dsb/dsb-hsb | **missing** | No instruction data for Sorbian-Sorbian MT | Need to generate from train pairs |
| MTrev hsb-de/dsb-de | **missing** | WMT22 has hsb-de pairs but no instruction format | Need to generate reverse-direction instructions |
| general instruction Magpie | **present** | 50,000 rows, 99.9% English | Usable as-is for English SFT |
| general instruction FLAN v2 | **present** | 50,000 rows, English only | Usable as-is |
| general instruction OASST2 | **present** | 50,000 rows, multi-lang (eng/rus/deu/ukr/pol) | Usable, filter by target lang |
| general instruction Aya | **present** | 6,765 rows, multi-lang | Usable, already filtered |
| general instruction EuroBlocks | **missing** | Not found on HuggingFace Hub | Skip or find alternative |
| Stopes-style normalization | **unknown** | No evidence of sentence-level normalization pipeline | Verify if TartuNLP used Stopes; implement if needed |
| dedup | **present** | CPT v1 interim: 996,873 duplicates removed | Done for CPT v1 |
| held-out/dev/test removal | **present** | 72,120 heldout hashes; 7,217 lines removed; 0 leakage in final | Done for CPT v1 |
| assistant-only loss mask | **unknown** | Not yet needed (CPT uses full-text loss) | Implement for SFT stage |
| 4096 packing | **unknown** | CPT training config uses max_seq_len=4096 | Verify packing strategy in LlamaFactory |

---

## 4. Compared with TartuNLP, What Is Still Missing?

### Need to Download
- **EuroBlocks**: Not found on HuggingFace Hub. Search alternative spellings or skip — it may be a private/internal dataset from TartuNLP.
- **German FineWeb2**: TartuNLP may have used German FineWeb2 for mixed CPT. Currently not downloaded. Can be deferred if strictly following TartuNLP's final model.

### Need to Clean/Transform
- **Wikipedia hsb/dsb**: Raw XML dumps present. Need WikiExtractor (or `python -m wikiextractor.WikiExtractor`) to extract clean text. Estimated ~33k hsb + ~10k dsb articles.
- **FineWeb2 hsb/dsb**: Raw Common Crawl data. Needs: (1) language verification, (2) dedup against existing data, (3) quality filtering (language_score threshold), (4) format conversion to CPT JSONL.
- **MT instruction data**: Need to generate instruction-format data from existing WMT25/WMT26/WMT22 parallel train pairs for all 6 directions (de-hsb, hsb-de, de-dsb, dsb-de, hsb-dsb, dsb-hsb).
- **SFT data mix**: No `data/processed/records/` or `data/processed/mixes/` exists. Need to build standardized records with per-row metadata for SFT stage.

### Not Needed (Can Skip)
- **German FineWeb2**: Only needed if following TartuNLP's mixed-language CPT variant. Can be deferred.
- **WMT20/21 separate download**: WMT22 repo already contains 2020 and 2021 data files. No separate download needed.
- **EuroBlocks**: Unavailable. Alternative: use Magpie MT + Aya + OA2 + generated Sorbian instructions.

---

## 5. Recommended Next Steps

### P0 — Must Do Now
1. **Verify CPT v1 contamination-free**: The hash-based filtering shows 0 leakage, but confirm no German text leaked from parallel target-side extraction. Check `data/manifests/cpt_v1_official_mono_file_map.yaml` to verify only `.hsb`/`.dsb` files were used.
2. **Clean Wikipedia dumps**: Run WikiExtractor on hsbwiki + dsbwiki XML to produce clean text for CPT.
3. **Resolve WMT22/WMT25 data overlap**: The WMT25 README explicitly states "there are also a few overlapping sentence pairs" with WMT22. The CPT pipeline's dedup should have handled this, but verify the overlap count.

### P1 — TartuNLP Reproduction
4. **Clean FineWeb2 data**: Apply quality filter (language_score ≥ 0.5), dedup against existing CPT data, convert to CPT format.
5. **Generate MT instruction data**: Script to convert WMT parallel pairs → instruction JSONL for all 6 directions.
6. **Build SFT data records**: Create `data/processed/records/` with per-row metadata (uid, source, task_type, lang, direction, split, license, usage, loss_policy).
7. **Verify Stopes normalization**: Research whether TartuNLP used Stopes or similar sentence-level normalization. Implement if needed.

### P2 — Enhancement
8. **Generate reverse-direction MT instructions** (hsb-de, dsb-de, dsb-hsb) from existing parallel data.
9. **Evaluate instruction data quality**: Sample-check Aya/OA2 records for Sorbian-proximate languages (Polish, Czech, Ukrainian).
10. **Generate standalone contamination report** from interim pipeline JSONs for audit traceability.
11. **Add per-row provenance** to future SFT/OPD processed data.

---

## 6. WMT22 Historical Data Summary

### Parallel Data by Direction

| Direction | Year(s) | File(s) | n_sentence_pairs | Format |
|---|---|---|---|---|
| hsb→de | 2020 | `train.hsb-de.{hsb,de}.gz` | 60,000 | TXT.gz, aligned lines |
| hsb→de | 2021 | `train2021.hsb-de.{hsb,de}.gz` | 87,521 | TXT.gz, aligned lines |
| hsb→de | 2022 | `HSB-DE_train.tsv.gz` | 301,537 | TSV.gz (hsb\tde) |
| **hsb→de total** | | | **449,058** | |
| dsb→de | 2022 | `40194_train_dsb_de.{dsb,de}.gz` | 40,193 | TXT.gz, aligned lines |
| **dsb→de total** | | | **40,193** | |
| hsb↔dsb | 2022 | `train_dsb_hsb_62564.{hsb,dsb}.gz` | 62,564 | TXT.gz, aligned lines |
| **hsb↔dsb total** | | | **62,564** | |
| de→hsb | — | (reverse of hsb→de) | 449,058 | derivable |
| de→dsb | — | (reverse of dsb→de) | 40,193 | derivable |
| dsb→hsb | — | (reverse of hsb↔dsb) | 62,564 | derivable |

### Monolingual Data

| Language | Source | File | n_lines | Format |
|---|---|---|---|---|
| hsb | generic | `HSB_monolingual.txt.gz` | 436,579 | TXT.gz |
| hsb | Sorbian Institute | `sorbian_institute_monolingual.hsb.gz` | 339,822 | TXT.gz |
| hsb | WITAJ | `witaj_monolingual.hsb.gz` | 222,027 | TXT.gz |
| hsb | web | `web_monolingual.hsb.gz` | 134,422 | TXT.gz |
| **hsb total** | | | **1,132,850** | |
| dsb | generic | `mono.dsb.gz` | 145,198 | TXT.gz |
| dsb | generic | `66408_DSB_monolingual.txt.gz` | 66,407 | TXT.gz |
| dsb | Wikipedia 2021 | `8815_DSB_wikipedia_2021.txt.gz` | 8,814 | TXT.gz |
| **dsb total** | | | **220,419** | |

### Dev/Test Data (heldout)

| Direction | Type | Archive | Contents |
|---|---|---|---|
| hsb→de | dev+test | `devtest.tar.gz` | devel 2000 + test 2000 lines |
| dsb→de | dev+test | `devtest.dsb-de.tgz` | devel + test |
| hsb↔dsb | dev+valid | `devtest_dsb_hsb_2022.tar.gz` | dev + valid |
| dsb→de | valid | `valid.{de,dsb}.gz` | 1,353 lines |

**Note**: WMT22 data already contains 2020 + 2021 files. No separate WMT20/21 download needed.

---

## 7. Contamination Risk Table

| Risk Level | Issue | Evidence | Recommendation |
|---|---|---|---|
| **LOW** | Hash-based heldout filtering applied | `heldout_report.json`: 72,120 hashes; `quality_audit_report.json`: leakage=0 | No action needed |
| **LOW** | All 43 heldout files excluded from CPT candidates | `raw_file_inventory.tsv`: 0 heldout with `include=True` | No action needed |
| **LOW** | CPT configs reference only clean processed data | 5 configs in `configs/train/cpt/` inspected | No action needed |
| **LOW** | WMT25 test files exist but correctly marked heldout | 26 test files under `data/raw/official/llms-limited-resources2025/` | No action needed |
| **MEDIUM** | No per-row provenance in CPT JSONL | Processed data is `{"text": ...}` only | Acceptable for CPT; add metadata for SFT |
| **MEDIUM** | Wikipedia raw XML may contain template/nav text | Raw mediawiki XML with full namespace markup | Must clean with WikiExtractor before use |
| **MEDIUM** | FineWeb2 is raw Common Crawl | Contains URL, date, language_score fields | Must filter + dedup before adding to CPT |
| **LOW** | PolyMath concern in DATA_PLAN.md | No PolyMath data exists in repo | No action needed |
| **LOW** | `data/processed/records/` missing | Expected by audit checklist but absent | Create for SFT stage |

---

## 8. Aggregate Statistics

### Monolingual Data Available for CPT (train-eligible)

| Source | hsb lines | dsb lines | Notes |
|---|---|---|---|
| WMT25 witaj | 1,071,722 | 120,500 | |
| WMT25 wiki | 47,758 | — | |
| WMT22 monolingual | 1,132,850 | 220,419 | Overlaps with WMT25 |
| WMT26 monolingual | 512,672 | 38,029 | New 2026 data |
| FineWeb2 | 44,293 docs | 6,798 docs | Raw, needs cleaning |
| Wikipedia | 33,539 pages | 9,839 pages | Raw XML, needs extraction |
| **CPT v1 processed** | **2,279,050** | **1,545,652** (×4) | Already deduped + filtered |

### Parallel Data Available for SFT

| Direction | WMT22 | WMT25 | WMT26 | Total |
|---|---|---|---|---|
| de→hsb | 449,058 | 187,269 | 23,117 | 659,444 |
| de→dsb | 40,193 | 171,963 | 30,561 | 242,717 |
| hsb→dsb | 62,564 | — | 67,846 | 130,410 |

### Instruction Data

| Dataset | Total Rows | eng | deu | pol | ukr | rus | srp | ces |
|---|---|---|---|---|---|---|---|---|
| Magpie MT | 50,000 | 49,927 | 51 | 8 | 3 | 6 | — | 5 |
| Aya | 6,765 | 3,944 | 241 | 1,483 | 522 | 423 | 152 | — |
| OA2 | 50,000 | 37,830 | 3,506 | 286 | 534 | 7,844 | — | — |
| FLAN v2 | 50,000 | 50,000 | — | — | — | — | — | — |
| **Total** | **156,765** | **141,701** | **3,798** | **1,777** | **1,059** | **8,273** | **152** | **5** |
