# base_qwen35_2b fewshot_devsplit_v1

## Quick Summary

- model_tag: `base_qwen35_2b`
- model_path: `/home/zc/wmt26/models/base/Qwen3.5-2B`
- eval_setting: `fewshot_devsplit_v1`
- shot_setting: `fewshot`
- parallel_setting: `8gpu`
- status: `aggregated`
- generated_at: `2026-06-19T22:47:37`
- parsed_result_files: `8`
- sample_files: `20`
- source_run_dir(s):
  - `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149`
- notes: Latest fixed 8GPU devsplit few-shot run aggregated from 20260618_162149.

## Main Scores

### MT

| task | metric | value | shard |
|---|---|---:|---|
| `deu-dsb_devsplit_fs5_v1` | `bleu,remove_tags` | 1.768507542 | `gpu5_mt_de_dsb` |
| `deu-dsb_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 15.48959922 | `gpu5_mt_de_dsb` |
| `deu-hsb_devsplit_fs5_v1` | `bleu,remove_tags` | 2.012442296 | `gpu4_mt_de_hsb` |
| `deu-hsb_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 19.03655992 | `gpu4_mt_de_hsb` |
| `dsb-deu_devsplit_fs5_v1` | `bleu,remove_tags` | 5.987816551 | `gpu5_mt_de_dsb` |
| `dsb-deu_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 28.88825337 | `gpu5_mt_de_dsb` |
| `dsb-hsb_devsplit_fs5_v1` | `bleu,remove_tags` | 7.520309161 | `gpu6_mt_dsb_hsb` |
| `dsb-hsb_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 36.88676906 | `gpu6_mt_dsb_hsb` |
| `hsb-deu_devsplit_fs5_v1` | `bleu,remove_tags` | 8.273664424 | `gpu4_mt_de_hsb` |
| `hsb-deu_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 33.66538465 | `gpu4_mt_de_hsb` |
| `hsb-dsb_devsplit_fs5_v1` | `bleu,remove_tags` | 6.278665447 | `gpu7_mt_hsb_dsb` |
| `hsb-dsb_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 35.09154373 | `gpu7_mt_hsb_dsb` |

### QA

| task | metric | value | shard |
|---|---|---:|---|
| `dsbqa_devsplit_fs1_v1` | `acc,none` | 0.4637259292 | `gpu0_qa` |
| `dsbqa_devsplit_fs1_v1::dsbqa-a1_devsplit_fs1_v1` | `acc,none` | 0.5172413793 | `gpu0_qa` |
| `dsbqa_devsplit_fs1_v1::dsbqa-a2_devsplit_fs1_v1` | `acc,none` | 0.6071428571 | `gpu0_qa` |
| `dsbqa_devsplit_fs1_v1::dsbqa-b1_devsplit_fs1_v1` | `acc,none` | 0.4090909091 | `gpu0_qa` |
| `dsbqa_devsplit_fs1_v1::dsbqa-b2_devsplit_fs1_v1` | `acc,none` | 0.3214285714 | `gpu0_qa` |
| `hsbqa_devsplit_fs1_v1` | `acc,none` | 0.4565186968 | `gpu0_qa` |
| `hsbqa_devsplit_fs1_v1::hsbqa-a1_devsplit_fs1_v1` | `acc,none` | 0.5517241379 | `gpu0_qa` |
| `hsbqa_devsplit_fs1_v1::hsbqa-a2_devsplit_fs1_v1` | `acc,none` | 0.5714285714 | `gpu0_qa` |
| `hsbqa_devsplit_fs1_v1::hsbqa-b1_devsplit_fs1_v1` | `acc,none` | 0.3636363636 | `gpu0_qa` |
| `hsbqa_devsplit_fs1_v1::hsbqa-b2_devsplit_fs1_v1` | `acc,none` | 0.3392857143 | `gpu0_qa` |

### SC

| task | metric | value | shard |
|---|---|---:|---|
| `dsbsc_devsplit_fs1_v1` | `exact_match_corrected,none` | 0.3756878439 | `gpu1_sc` |
| `dsbsc_devsplit_fs1_v1` | `exact_match_wrong,none` | 0.3716858429 | `gpu1_sc` |
| `hsbsc_devsplit_fs1_v1` | `exact_match_corrected,none` | 0.3901950975 | `gpu1_sc` |
| `hsbsc_devsplit_fs1_v1` | `exact_match_wrong,none` | 0.3886943472 | `gpu1_sc` |

### GC

| task | metric | value | shard |
|---|---|---:|---|
| `dsbgc_devsplit_fs1_v1` | `exact_match_corrected,none` | 0.2121697358 | `gpu2_gc` |
| `dsbgc_devsplit_fs1_v1` | `exact_match_wrong,none` | 0.2137710168 | `gpu2_gc` |
| `hsbgc_devsplit_fs1_v1` | `exact_match_corrected,none` | 0.001500750375 | `gpu2_gc` |
| `hsbgc_devsplit_fs1_v1` | `exact_match_wrong,none` | 0.04152076038 | `gpu2_gc` |

### MR

| task | metric | value | shard |
|---|---|---:|---|
| `dsbmr_devsplit_fs1_v1` | `chrf,remove_tags` | 2.14086363 | `gpu3_mr` |
| `dsbmr_devsplit_fs1_v1` | `exact_match,remove_tags` | 0.04347826087 | `gpu3_mr` |
| `hsbmr_devsplit_fs1_v1` | `chrf,remove_tags` | 1.386466584 | `gpu3_mr` |
| `hsbmr_devsplit_fs1_v1` | `exact_match,remove_tags` | 0.04347826087 | `gpu3_mr` |

## All Scalar Metrics

| task | metric | value | shard | source_json |
|---|---|---:|---|---|
| `dsbgc_devsplit_fs1_v1` | `exact_match_corrected,none` | 0.2121697358 | `gpu2_gc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json` |
| `dsbgc_devsplit_fs1_v1` | `exact_match_corrected_stderr,none` | 0.01157312796 | `gpu2_gc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json` |
| `dsbgc_devsplit_fs1_v1` | `exact_match_wrong,none` | 0.2137710168 | `gpu2_gc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json` |
| `dsbgc_devsplit_fs1_v1` | `exact_match_wrong_stderr,none` | 0.01160490644 | `gpu2_gc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json` |
| `hsbgc_devsplit_fs1_v1` | `exact_match_corrected,none` | 0.001500750375 | `gpu2_gc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json` |
| `hsbgc_devsplit_fs1_v1` | `exact_match_corrected_stderr,none` | 0.0008660248615 | `gpu2_gc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json` |
| `hsbgc_devsplit_fs1_v1` | `exact_match_wrong,none` | 0.04152076038 | `gpu2_gc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json` |
| `hsbgc_devsplit_fs1_v1` | `exact_match_wrong_stderr,none` | 0.004462993584 | `gpu2_gc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json` |
| `dsbmr_devsplit_fs1_v1` | `chrf,remove_tags` | 2.14086363 | `gpu3_mr` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json` |
| `dsbmr_devsplit_fs1_v1` | `chrf_stderr,remove_tags` | 0.9709252352 | `gpu3_mr` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json` |
| `dsbmr_devsplit_fs1_v1` | `exact_match,remove_tags` | 0.04347826087 | `gpu3_mr` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json` |
| `dsbmr_devsplit_fs1_v1` | `exact_match_stderr,remove_tags` | 0.04347826087 | `gpu3_mr` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json` |
| `hsbmr_devsplit_fs1_v1` | `chrf,remove_tags` | 1.386466584 | `gpu3_mr` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json` |
| `hsbmr_devsplit_fs1_v1` | `chrf_stderr,remove_tags` | 0.3852867268 | `gpu3_mr` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json` |
| `hsbmr_devsplit_fs1_v1` | `exact_match,remove_tags` | 0.04347826087 | `gpu3_mr` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json` |
| `hsbmr_devsplit_fs1_v1` | `exact_match_stderr,remove_tags` | 0.04347826087 | `gpu3_mr` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json` |
| `deu-dsb_devsplit_fs5_v1` | `bleu,remove_tags` | 1.768507542 | `gpu5_mt_de_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json` |
| `deu-dsb_devsplit_fs5_v1` | `bleu_stderr,remove_tags` | 0.2188951695 | `gpu5_mt_de_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json` |
| `deu-dsb_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 15.48959922 | `gpu5_mt_de_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json` |
| `deu-dsb_devsplit_fs5_v1` | `chrf_pp_stderr,remove_tags` | N/A | `gpu5_mt_de_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json` |
| `deu-hsb_devsplit_fs5_v1` | `bleu,remove_tags` | 2.012442296 | `gpu4_mt_de_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json` |
| `deu-hsb_devsplit_fs5_v1` | `bleu_stderr,remove_tags` | 0.1228927729 | `gpu4_mt_de_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json` |
| `deu-hsb_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 19.03655992 | `gpu4_mt_de_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json` |
| `deu-hsb_devsplit_fs5_v1` | `chrf_pp_stderr,remove_tags` | N/A | `gpu4_mt_de_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json` |
| `dsb-deu_devsplit_fs5_v1` | `bleu,remove_tags` | 5.987816551 | `gpu5_mt_de_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json` |
| `dsb-deu_devsplit_fs5_v1` | `bleu_stderr,remove_tags` | 0.2265019095 | `gpu5_mt_de_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json` |
| `dsb-deu_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 28.88825337 | `gpu5_mt_de_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json` |
| `dsb-deu_devsplit_fs5_v1` | `chrf_pp_stderr,remove_tags` | N/A | `gpu5_mt_de_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json` |
| `dsb-hsb_devsplit_fs5_v1` | `bleu,remove_tags` | 7.520309161 | `gpu6_mt_dsb_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu6_mt_dsb_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-10-36.519447.json` |
| `dsb-hsb_devsplit_fs5_v1` | `bleu_stderr,remove_tags` | 0.167697465 | `gpu6_mt_dsb_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu6_mt_dsb_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-10-36.519447.json` |
| `dsb-hsb_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 36.88676906 | `gpu6_mt_dsb_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu6_mt_dsb_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-10-36.519447.json` |
| `dsb-hsb_devsplit_fs5_v1` | `chrf_pp_stderr,remove_tags` | N/A | `gpu6_mt_dsb_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu6_mt_dsb_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-10-36.519447.json` |
| `hsb-deu_devsplit_fs5_v1` | `bleu,remove_tags` | 8.273664424 | `gpu4_mt_de_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json` |
| `hsb-deu_devsplit_fs5_v1` | `bleu_stderr,remove_tags` | 0.2126213838 | `gpu4_mt_de_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json` |
| `hsb-deu_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 33.66538465 | `gpu4_mt_de_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json` |
| `hsb-deu_devsplit_fs5_v1` | `chrf_pp_stderr,remove_tags` | N/A | `gpu4_mt_de_hsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json` |
| `hsb-dsb_devsplit_fs5_v1` | `bleu,remove_tags` | 6.278665447 | `gpu7_mt_hsb_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu7_mt_hsb_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-05-42.958650.json` |
| `hsb-dsb_devsplit_fs5_v1` | `bleu_stderr,remove_tags` | 0.1761469266 | `gpu7_mt_hsb_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu7_mt_hsb_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-05-42.958650.json` |
| `hsb-dsb_devsplit_fs5_v1` | `chrf_pp,remove_tags` | 35.09154373 | `gpu7_mt_hsb_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu7_mt_hsb_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-05-42.958650.json` |
| `hsb-dsb_devsplit_fs5_v1` | `chrf_pp_stderr,remove_tags` | N/A | `gpu7_mt_hsb_dsb` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu7_mt_hsb_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-05-42.958650.json` |
| `dsbqa_devsplit_fs1_v1` | `acc,none` | 0.4637259292 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1` | `acc_stderr,none` | 0.03912504204 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1::dsbqa-a1_devsplit_fs1_v1` | `acc,none` | 0.5172413793 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1::dsbqa-a1_devsplit_fs1_v1` | `acc_stderr,none` | 0.09443492371 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1::dsbqa-a2_devsplit_fs1_v1` | `acc,none` | 0.6071428571 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1::dsbqa-a2_devsplit_fs1_v1` | `acc_stderr,none` | 0.09398983557 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1::dsbqa-b1_devsplit_fs1_v1` | `acc,none` | 0.4090909091 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1::dsbqa-b1_devsplit_fs1_v1` | `acc_stderr,none` | 0.07497837474 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1::dsbqa-b2_devsplit_fs1_v1` | `acc,none` | 0.3214285714 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbqa_devsplit_fs1_v1::dsbqa-b2_devsplit_fs1_v1` | `acc_stderr,none` | 0.06297362289 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1` | `acc,none` | 0.4565186968 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1` | `acc_stderr,none` | 0.039122034 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1::hsbqa-a1_devsplit_fs1_v1` | `acc,none` | 0.5517241379 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1::hsbqa-a1_devsplit_fs1_v1` | `acc_stderr,none` | 0.09398415778 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1::hsbqa-a2_devsplit_fs1_v1` | `acc,none` | 0.5714285714 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1::hsbqa-a2_devsplit_fs1_v1` | `acc_stderr,none` | 0.09523809524 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1::hsbqa-b1_devsplit_fs1_v1` | `acc,none` | 0.3636363636 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1::hsbqa-b1_devsplit_fs1_v1` | `acc_stderr,none` | 0.07335878044 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1::hsbqa-b2_devsplit_fs1_v1` | `acc,none` | 0.3392857143 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `hsbqa_devsplit_fs1_v1::hsbqa-b2_devsplit_fs1_v1` | `acc_stderr,none` | 0.06384226562 | `gpu0_qa` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json` |
| `dsbsc_devsplit_fs1_v1` | `exact_match_corrected,none` | 0.3756878439 | `gpu1_sc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json` |
| `dsbsc_devsplit_fs1_v1` | `exact_match_corrected_stderr,none` | 0.01083469587 | `gpu1_sc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json` |
| `dsbsc_devsplit_fs1_v1` | `exact_match_wrong,none` | 0.3716858429 | `gpu1_sc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json` |
| `dsbsc_devsplit_fs1_v1` | `exact_match_wrong_stderr,none` | 0.01081131922 | `gpu1_sc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json` |
| `hsbsc_devsplit_fs1_v1` | `exact_match_corrected,none` | 0.3901950975 | `gpu1_sc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json` |
| `hsbsc_devsplit_fs1_v1` | `exact_match_corrected_stderr,none` | 0.01091286086 | `gpu1_sc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json` |
| `hsbsc_devsplit_fs1_v1` | `exact_match_wrong,none` | 0.3886943472 | `gpu1_sc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json` |
| `hsbsc_devsplit_fs1_v1` | `exact_match_wrong_stderr,none` | 0.01090524875 | `gpu1_sc` | `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json` |

## Parsed Files

- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-23-58.984302.json`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-06-48.563686.json`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T17-01-41.000561.json`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T16-31-36.561326.json`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T19-29-33.399739.json`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-59-51.868706.json`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu6_mt_dsb_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-10-36.519447.json`
- `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu7_mt_hsb_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-18T18-05-42.958650.json`

## Sample Files

| path | lines | size_bytes | shard |
|---|---:|---:|---|
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbqa_devsplit_fs1_v1::dsbqa-a1_devsplit_fs1_v1_2026-06-18T16-23-58.984302.jsonl` | 29 | 377589 | `gpu0_qa` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbqa_devsplit_fs1_v1::dsbqa-a2_devsplit_fs1_v1_2026-06-18T16-23-58.984302.jsonl` | 28 | 517877 | `gpu0_qa` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbqa_devsplit_fs1_v1::dsbqa-b1_devsplit_fs1_v1_2026-06-18T16-23-58.984302.jsonl` | 44 | 1299174 | `gpu0_qa` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbqa_devsplit_fs1_v1::dsbqa-b2_devsplit_fs1_v1_2026-06-18T16-23-58.984302.jsonl` | 56 | 2802915 | `gpu0_qa` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbqa_devsplit_fs1_v1::hsbqa-a1_devsplit_fs1_v1_2026-06-18T16-23-58.984302.jsonl` | 29 | 373995 | `gpu0_qa` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbqa_devsplit_fs1_v1::hsbqa-a2_devsplit_fs1_v1_2026-06-18T16-23-58.984302.jsonl` | 28 | 517005 | `gpu0_qa` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbqa_devsplit_fs1_v1::hsbqa-b1_devsplit_fs1_v1_2026-06-18T16-23-58.984302.jsonl` | 44 | 1283943 | `gpu0_qa` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu0_qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbqa_devsplit_fs1_v1::hsbqa-b2_devsplit_fs1_v1_2026-06-18T16-23-58.984302.jsonl` | 56 | 2916012 | `gpu0_qa` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbsc_devsplit_fs1_v1_2026-06-18T17-06-48.563686.jsonl` | 1999 | 4450334 | `gpu1_sc` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu1_sc/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbsc_devsplit_fs1_v1_2026-06-18T17-06-48.563686.jsonl` | 1999 | 4465236 | `gpu1_sc` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbgc_devsplit_fs1_v1_2026-06-18T17-01-41.000561.jsonl` | 1249 | 2776700 | `gpu2_gc` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu2_gc/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbgc_devsplit_fs1_v1_2026-06-18T17-01-41.000561.jsonl` | 1999 | 4519313 | `gpu2_gc` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbmr_devsplit_fs1_v1_2026-06-18T16-31-36.561326.jsonl` | 23 | 69896 | `gpu3_mr` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu3_mr/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbmr_devsplit_fs1_v1_2026-06-18T16-31-36.561326.jsonl` | 23 | 74117 | `gpu3_mr` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_deu-hsb_devsplit_fs5_v1_2026-06-18T19-29-33.399739.jsonl` | 3995 | 15094322 | `gpu4_mt_de_hsb` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu4_mt_de_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsb-deu_devsplit_fs5_v1_2026-06-18T19-29-33.399739.jsonl` | 3995 | 15142838 | `gpu4_mt_de_hsb` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_deu-dsb_devsplit_fs5_v1_2026-06-18T18-59-51.868706.jsonl` | 3995 | 14024202 | `gpu5_mt_de_dsb` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu5_mt_de_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsb-deu_devsplit_fs5_v1_2026-06-18T18-59-51.868706.jsonl` | 3995 | 14063759 | `gpu5_mt_de_dsb` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu6_mt_dsb_hsb/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsb-hsb_devsplit_fs5_v1_2026-06-18T18-10-36.519447.jsonl` | 3995 | 17669544 | `gpu6_mt_dsb_hsb` |
| `runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu/20260618_162149/shards/gpu7_mt_hsb_dsb/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsb-dsb_devsplit_fs5_v1_2026-06-18T18-05-42.958650.jsonl` | 3995 | 17665013 | `gpu7_mt_hsb_dsb` |

## Warnings / Limitations

- None
