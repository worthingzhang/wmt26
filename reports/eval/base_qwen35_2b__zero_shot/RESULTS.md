# base_qwen35_2b zero_shot

## Quick Summary

- model_tag: `base_qwen35_2b`
- model_path: `/home/zc/wmt26/models/base/Qwen3.5-2B`
- eval_setting: `zero_shot`
- shot_setting: `zero_shot`
- parallel_setting: `mixed`
- status: `aggregated`
- generated_at: `2026-06-19T22:47:37`
- parsed_result_files: `2`
- sample_files: `20`
- source_run_dir(s):
  - `runs/eval/eval_base_qwen35_2b_full`
- notes: Official base zero-shot full run aggregated from eval_base_qwen35_2b_full; smoke runs excluded.

## Main Scores

### MT

| task | metric | value | shard |
|---|---|---:|---|
| `deu-dsb` | `bleu,remove_tags` | 1.178904772 | `` |
| `deu-dsb` | `chrf_pp,remove_tags` | 11.05690737 | `` |
| `deu-hsb` | `bleu,remove_tags` | 1.106832888 | `` |
| `deu-hsb` | `chrf_pp,remove_tags` | 13.67917846 | `` |
| `dsb-deu` | `bleu,remove_tags` | 4.8406641 | `` |
| `dsb-deu` | `chrf_pp,remove_tags` | 23.50368317 | `` |
| `dsb-hsb` | `bleu,remove_tags` | 5.437873059 | `` |
| `dsb-hsb` | `chrf_pp,remove_tags` | 29.67224429 | `` |
| `hsb-deu` | `bleu,remove_tags` | 6.370682846 | `` |
| `hsb-deu` | `chrf_pp,remove_tags` | 26.58896618 | `` |
| `hsb-dsb` | `bleu,remove_tags` | 4.988803751 | `` |
| `hsb-dsb` | `chrf_pp,remove_tags` | 27.75631775 | `` |

### QA

| task | metric | value | shard |
|---|---|---:|---|
| `dsbqa` | `acc,none` | 0.4682359307 | `` |
| `dsbqa::dsbqa-a1` | `acc,none` | 0.7333333333 | `` |
| `dsbqa::dsbqa-a2` | `acc,none` | 0.6071428571 | `` |
| `dsbqa::dsbqa-b1` | `acc,none` | 0.3181818182 | `` |
| `dsbqa::dsbqa-b2` | `acc,none` | 0.2142857143 | `` |
| `hsbqa` | `acc,none` | 0.5159090909 | `` |
| `hsbqa::hsbqa-a1` | `acc,none` | 0.7 | `` |
| `hsbqa::hsbqa-a2` | `acc,none` | 0.6785714286 | `` |
| `hsbqa::hsbqa-b1` | `acc,none` | 0.3636363636 | `` |
| `hsbqa::hsbqa-b2` | `acc,none` | 0.3214285714 | `` |

### SC

| task | metric | value | shard |
|---|---|---:|---|
| `dsbsc` | `exact_match_corrected,none` | 0.074 | `` |
| `dsbsc` | `exact_match_wrong,none` | 0.0695 | `` |
| `hsbsc` | `exact_match_corrected,none` | 0.0945 | `` |
| `hsbsc` | `exact_match_wrong,none` | 0.096 | `` |

### GC

| task | metric | value | shard |
|---|---|---:|---|
| `dsbgc` | `exact_match_corrected,none` | 0.004 | `` |
| `dsbgc` | `exact_match_wrong,none` | 0.0288 | `` |
| `hsbgc` | `exact_match_corrected,none` | 0.0035 | `` |
| `hsbgc` | `exact_match_wrong,none` | 0.0295 | `` |

### MR

| task | metric | value | shard |
|---|---|---:|---|
| `dsbmr` | `chrf,remove_tags` | 1.793665792 | `` |
| `dsbmr` | `exact_match,remove_tags` | 0.04166666667 | `` |
| `hsbmr` | `chrf,remove_tags` | 1.916340158 | `` |
| `hsbmr` | `exact_match,remove_tags` | 0.04166666667 | `` |

## All Scalar Metrics

| task | metric | value | shard | source_json |
|---|---|---:|---|---|
| `dsbgc` | `exact_match_corrected,none` | 0.004 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbgc` | `exact_match_corrected_stderr,none` | 0.001785987626 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbgc` | `exact_match_wrong,none` | 0.0288 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbgc` | `exact_match_wrong_stderr,none` | 0.004732268324 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbgc` | `exact_match_corrected,none` | 0.0035 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbgc` | `exact_match_corrected_stderr,none` | 0.001320888857 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbgc` | `exact_match_wrong,none` | 0.0295 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbgc` | `exact_match_wrong_stderr,none` | 0.003784446593 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbmr` | `chrf,remove_tags` | 1.793665792 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbmr` | `chrf_stderr,remove_tags` | 0.6226681065 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbmr` | `exact_match,remove_tags` | 0.04166666667 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbmr` | `exact_match_stderr,remove_tags` | 0.04166666667 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbmr` | `chrf,remove_tags` | 1.916340158 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbmr` | `chrf_stderr,remove_tags` | 0.6997797743 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbmr` | `exact_match,remove_tags` | 0.04166666667 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbmr` | `exact_match_stderr,remove_tags` | 0.04166666667 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `deu-dsb` | `bleu,remove_tags` | 1.178904772 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `deu-dsb` | `bleu_stderr,remove_tags` | 0.1931619515 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `deu-dsb` | `chrf_pp,remove_tags` | 11.05690737 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `deu-dsb` | `chrf_pp_stderr,remove_tags` | N/A | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `deu-hsb` | `bleu,remove_tags` | 1.106832888 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `deu-hsb` | `bleu_stderr,remove_tags` | 0.07719307967 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `deu-hsb` | `chrf_pp,remove_tags` | 13.67917846 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `deu-hsb` | `chrf_pp_stderr,remove_tags` | N/A | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsb-deu` | `bleu,remove_tags` | 4.8406641 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsb-deu` | `bleu_stderr,remove_tags` | 0.179359098 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsb-deu` | `chrf_pp,remove_tags` | 23.50368317 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsb-deu` | `chrf_pp_stderr,remove_tags` | N/A | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsb-hsb` | `bleu,remove_tags` | 5.437873059 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsb-hsb` | `bleu_stderr,remove_tags` | 0.1846316274 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsb-hsb` | `chrf_pp,remove_tags` | 29.67224429 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsb-hsb` | `chrf_pp_stderr,remove_tags` | N/A | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsb-deu` | `bleu,remove_tags` | 6.370682846 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsb-deu` | `bleu_stderr,remove_tags` | 0.217319213 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsb-deu` | `chrf_pp,remove_tags` | 26.58896618 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsb-deu` | `chrf_pp_stderr,remove_tags` | N/A | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsb-dsb` | `bleu,remove_tags` | 4.988803751 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsb-dsb` | `bleu_stderr,remove_tags` | 0.1481670489 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsb-dsb` | `chrf_pp,remove_tags` | 27.75631775 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsb-dsb` | `chrf_pp_stderr,remove_tags` | N/A | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbqa` | `acc,none` | 0.4682359307 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa` | `acc_stderr,none` | 0.03599143234 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa::dsbqa-a1` | `acc,none` | 0.7333333333 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa::dsbqa-a1` | `acc_stderr,none` | 0.08211756827 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa::dsbqa-a2` | `acc,none` | 0.6071428571 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa::dsbqa-a2` | `acc_stderr,none` | 0.09398983557 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa::dsbqa-b1` | `acc,none` | 0.3181818182 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa::dsbqa-b1` | `acc_stderr,none` | 0.07102933373 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa::dsbqa-b2` | `acc,none` | 0.2142857143 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbqa::dsbqa-b2` | `acc_stderr,none` | 0.05532833352 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa` | `acc,none` | 0.5159090909 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa` | `acc_stderr,none` | 0.03781995227 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa::hsbqa-a1` | `acc,none` | 0.7 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa::hsbqa-a1` | `acc_stderr,none` | 0.08509629434 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa::hsbqa-a2` | `acc,none` | 0.6785714286 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa::hsbqa-a2` | `acc_stderr,none` | 0.08987898137 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa::hsbqa-b1` | `acc,none` | 0.3636363636 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa::hsbqa-b1` | `acc_stderr,none` | 0.07335878044 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa::hsbqa-b2` | `acc,none` | 0.3214285714 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `hsbqa::hsbqa-b2` | `acc_stderr,none` | 0.06297362289 | `` | `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json` |
| `dsbsc` | `exact_match_corrected,none` | 0.074 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbsc` | `exact_match_corrected_stderr,none` | 0.005854838988 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbsc` | `exact_match_wrong,none` | 0.0695 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `dsbsc` | `exact_match_wrong_stderr,none` | 0.00568779839 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbsc` | `exact_match_corrected,none` | 0.0945 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbsc` | `exact_match_corrected_stderr,none` | 0.006542650697 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbsc` | `exact_match_wrong,none` | 0.096 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |
| `hsbsc` | `exact_match_wrong_stderr,none` | 0.006588907865 | `` | `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json` |

## Parsed Files

- `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T19-02-45.151488.json`
- `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/results_2026-06-15T03-25-23.017814.json`

## Sample Files

| path | lines | size_bytes | shard |
|---|---:|---:|---|
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_deu-dsb_2026-06-15T19-02-45.151488.jsonl` | 4000 | 6869794 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_deu-hsb_2026-06-15T19-02-45.151488.jsonl` | 4000 | 7643147 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsb-deu_2026-06-15T19-02-45.151488.jsonl` | 4000 | 6893283 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsb-hsb_2026-06-15T19-02-45.151488.jsonl` | 4000 | 8131769 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbgc_2026-06-15T19-02-45.151488.jsonl` | 1250 | 2042424 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbmr_2026-06-15T19-02-45.151488.jsonl` | 24 | 64268 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbsc_2026-06-15T19-02-45.151488.jsonl` | 2000 | 3402903 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsb-deu_2026-06-15T19-02-45.151488.jsonl` | 4000 | 7648844 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsb-dsb_2026-06-15T19-02-45.151488.jsonl` | 4000 | 8009601 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbgc_2026-06-15T19-02-45.151488.jsonl` | 2000 | 3384380 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbmr_2026-06-15T19-02-45.151488.jsonl` | 24 | 65088 | `` |
| `runs/eval/eval_base_qwen35_2b_full/gen_fixed/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbsc_2026-06-15T19-02-45.151488.jsonl` | 2000 | 3438585 | `` |
| `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbqa::dsbqa-a1_2026-06-15T03-25-23.017814.jsonl` | 30 | 202994 | `` |
| `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbqa::dsbqa-a2_2026-06-15T03-25-23.017814.jsonl` | 28 | 343385 | `` |
| `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbqa::dsbqa-b1_2026-06-15T03-25-23.017814.jsonl` | 44 | 1024920 | `` |
| `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_dsbqa::dsbqa-b2_2026-06-15T03-25-23.017814.jsonl` | 56 | 2453595 | `` |
| `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbqa::hsbqa-a1_2026-06-15T03-25-23.017814.jsonl` | 30 | 200857 | `` |
| `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbqa::hsbqa-a2_2026-06-15T03-25-23.017814.jsonl` | 28 | 343879 | `` |
| `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbqa::hsbqa-b1_2026-06-15T03-25-23.017814.jsonl` | 44 | 1011633 | `` |
| `runs/eval/eval_base_qwen35_2b_full/qa/__home__zc__wmt26__models__base__Qwen3.5-2B/samples_hsbqa::hsbqa-b2_2026-06-15T03-25-23.017814.jsonl` | 56 | 2569462 | `` |

## Warnings / Limitations

- None
