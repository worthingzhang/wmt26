#!/usr/bin/env python3
"""Generate overlay YAML files for wmt26_sorbian_devsplit_fewshot_v2."""

from pathlib import Path

BASE = Path('/home/zc/wmt26/configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v2')
DEVSPLIT_DIR = '/home/zc/wmt26/configs/eval/devsplits/sorbian_devsplit_fewshot_v2/eval'

GC_SC_DOC_TO_TEXT = (
    "The following sentence contains at most one grammatically incorrect word. "
    "Respond with exactly these two tags and nothing else:\\n"
    "<wrong> incorrect word </wrong> <corrected> correct form </corrected>\\n"
    "If the sentence has no error, use the literal string CORRECT in both tags:\\n"
    "<wrong> CORRECT </wrong> <corrected> CORRECT </corrected>\\n"
    "<sentence> {{input_sentence}} </sentence>"
)

MR_DOC_TO_TEXT = (
    "Answer this mathematical reasoning question. "
    "Place your final answer, using LateX when appropriate, in this format: "
    "<answer> answer </answer> {{question}}"
)

QA_DOC_TO_TEXT = (
    "{{context.strip() if context else ''}}\\n\\n"
    "Question:\\n"
    "{{question.strip() if question else ''}}\\n\\n"
    "Possible answers:\\n"
    "{% for k, v in possible_answers|dictsort %}{{k}}: {{v}}\\n{% endfor %}\\n"
    "Answer:"
)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8')
    print(f'Wrote {path}')


def gc_sc_yaml(task_name: str, num_shots: int, loader: str, data_file: str) -> str:
    return f"""task: {task_name}
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: {DEVSPLIT_DIR}/{data_file}
test_split: test
num_fewshot: {num_shots}
fewshot_config:
  sampler: first_n
  samples: !function utils.{loader}
  doc_to_target: !function utils.target_wrong_corrected
fewshot_delimiter: "\\n\\n"
target_delimiter: " "
doc_to_text: "{GC_SC_DOC_TO_TEXT}"
doc_to_target: "{{{{incorrect_word}}}}, {{{{correct_word}}}}"
generation_kwargs:
  until:
    - "<|endoftext|>"
    - "<|im_end|>"
  max_gen_toks: 64
  temperature: 1
  top_p: 1.0
  top_k: 20
  min_p: 0.0
  repetition_penalty: 1.0
filter_list:
  - name: "none"
    filter:
      - function: "strip_thinking"
      - function: "take_first"
process_results: !function lm_eval.tasks.wmt26-lrl.utils.process_sc_results
metric_list:
  - metric: exact_match_wrong
    aggregation: mean
    higher_is_better: true
  - metric: exact_match_corrected
    aggregation: mean
    higher_is_better: true
metadata:
  version: 2.0
"""


def mr_yaml(task_name: str, num_shots: int, loader: str, data_file: str) -> str:
    return f"""task: {task_name}
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: {DEVSPLIT_DIR}/{data_file}
test_split: test
num_fewshot: {num_shots}
fewshot_config:
  sampler: first_n
  samples: !function utils.{loader}
  doc_to_target: !function utils.target_answer
fewshot_delimiter: "\\n\\n"
target_delimiter: " "
doc_to_text: "{MR_DOC_TO_TEXT}"
doc_to_target: "{{{{answer}}}}"
generation_kwargs:
  until:
    - "<|endoftext|>"
    - "<|im_end|>"
  max_gen_toks: 512
  temperature: 1
  top_p: 1.0
  top_k: 20
  min_p: 0.0
  repetition_penalty: 1.0
filter_list:
  - name: "remove_tags"
    filter:
      - function: "strip_thinking"
      - function: "regex"
        regex_pattern: "<answer>\\\\s*(.*?)\\\\s*</answer>"
      - function: "take_first"
metric_list:
  - metric: chrf
  - metric: exact_match
metadata:
  version: 2.0
"""


def mt_yaml(task_name: str, num_shots: int, loader: str, data_file: str,
            src_key: str, tgt_key: str, target_fn: str) -> str:
    src_display = {'de': 'German', 'hsb': 'Upper Sorbian', 'dsb': 'Lower Sorbian'}[src_key]
    tgt_display = {'de': 'German', 'hsb': 'Upper Sorbian', 'dsb': 'Lower Sorbian'}[tgt_key]
    doc_to_text = (
        f"Translate the following {src_display} text to {tgt_display}. "
        f"Put it in this format <{tgt_key}> {tgt_display} translation </{tgt_key}>.\\n"
        f"<{src_key}> {{{{{src_key}}}}} </{src_key}>"
    )
    return f"""task: {task_name}
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: {DEVSPLIT_DIR}/{data_file}
test_split: test
num_fewshot: {num_shots}
fewshot_config:
  sampler: first_n
  samples: !function utils.{loader}
  doc_to_target: !function utils.{target_fn}
fewshot_delimiter: "\\n\\n"
target_delimiter: " "
doc_to_text: "{doc_to_text}"
doc_to_target: "{{{{{tgt_key}}}}}"
generation_kwargs:
  until:
    - "<|endoftext|>"
    - "<|im_end|>"
  max_gen_toks: 256
  temperature: 1
  top_p: 1.0
  top_k: 20
  min_p: 0.0
  repetition_penalty: 1.0
filter_list:
  - name: "remove_tags"
    filter:
      - function: "strip_thinking"
      - function: "regex"
        regex_pattern: "<{tgt_key}>\\\\s*([\\\\s\\\\S]*?)\\\\s*(?:</{tgt_key}>|$)"
      - function: "take_first"
metric_list:
  - metric: bleu
  - metric: !function lm_eval.tasks.wmt26-lrl.utils.chrf_pp
    aggregation: chrf++
    higher_is_better: true
metadata:
  version: 2.0
"""


def qa_yaml(lang: str, loader: str, data_file: str) -> str:
    prefix = lang + 'qa'
    return f"""group: {prefix}_devsplit_fs3_v2
task:
  - task: {prefix}-a1_devsplit_fs3_v2
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_a1
  - task: {prefix}-a2_devsplit_fs3_v2
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_a2
  - task: {prefix}-b1_devsplit_fs3_v2
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_b1
  - task: {prefix}-b2_devsplit_fs3_v2
    process_docs: !function lm_eval.tasks.wmt26-lrl.utils.process_level_b2
dataset_path: json
dataset_name: null
dataset_kwargs:
  data_files:
    test: {DEVSPLIT_DIR}/{data_file}
test_split: test
num_fewshot: 3
fewshot_config:
  sampler: first_n
  samples: !function utils.{loader}
fewshot_delimiter: "\\n\\n"
target_delimiter: " "
output_type: multiple_choice
doc_to_text: "{QA_DOC_TO_TEXT}"
doc_to_choice: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
doc_to_target: "{{{{(correct_answer_num|int)-1}}}}"
metric_list:
  - metric: acc
    aggregation: mean
    higher_is_better: true
aggregate_metric_list:
  - metric: acc
    aggregation: mean
    weight_by_size: false
metadata:
  version: 2.0
"""


def main() -> None:
    for subdir in ['gc', 'sc', 'mr', 'qa', 'mt']:
        (BASE / subdir).mkdir(parents=True, exist_ok=True)

    # GC
    write_text(BASE / 'gc' / 'hsbgc.yaml', gc_sc_yaml('hsbgc_devsplit_fs2_v2', 2, 'hsbgc_shots', 'hsbgc.jsonl'))
    write_text(BASE / 'gc' / 'dsbgc.yaml', gc_sc_yaml('dsbgc_devsplit_fs2_v2', 2, 'dsbgc_shots', 'dsbgc.jsonl'))

    # SC
    write_text(BASE / 'sc' / 'hsbsc.yaml', gc_sc_yaml('hsbsc_devsplit_fs2_v2', 2, 'hsbsc_shots', 'hsbsc.jsonl'))
    write_text(BASE / 'sc' / 'dsbsc.yaml', gc_sc_yaml('dsbsc_devsplit_fs2_v2', 2, 'dsbsc_shots', 'dsbsc.jsonl'))

    # MR
    write_text(BASE / 'mr' / 'hsbmr.yaml', mr_yaml('hsbmr_devsplit_fs2_v2', 2, 'hsbmr_shots', 'hsbmr.jsonl'))
    write_text(BASE / 'mr' / 'dsbmr.yaml', mr_yaml('dsbmr_devsplit_fs2_v2', 2, 'dsbmr_shots', 'dsbmr.jsonl'))

    # MT
    mt_tasks = [
        ('deu-hsb.yaml', 'deu-hsb_devsplit_fs5_v2', 'de_hsb_mt_shots', 'de-hsb_mt.jsonl', 'de', 'hsb', 'target_hsb'),
        ('hsb-deu.yaml', 'hsb-deu_devsplit_fs5_v2', 'de_hsb_mt_shots', 'de-hsb_mt.jsonl', 'hsb', 'de', 'target_deu'),
        ('deu-dsb.yaml', 'deu-dsb_devsplit_fs5_v2', 'de_dsb_mt_shots', 'de-dsb_mt.jsonl', 'de', 'dsb', 'target_dsb'),
        ('dsb-deu.yaml', 'dsb-deu_devsplit_fs5_v2', 'de_dsb_mt_shots', 'de-dsb_mt.jsonl', 'dsb', 'de', 'target_deu'),
        ('dsb-hsb.yaml', 'dsb-hsb_devsplit_fs5_v2', 'hsb_dsb_mt_shots', 'hsb-dsb_mt.jsonl', 'dsb', 'hsb', 'target_hsb'),
        ('hsb-dsb.yaml', 'hsb-dsb_devsplit_fs5_v2', 'hsb_dsb_mt_shots', 'hsb-dsb_mt.jsonl', 'hsb', 'dsb', 'target_dsb'),
    ]
    for fname, task_name, loader, data_file, src, tgt, target_fn in mt_tasks:
        write_text(BASE / 'mt' / fname, mt_yaml(task_name, 5, loader, data_file, src, tgt, target_fn))

    # QA
    write_text(BASE / 'qa' / 'hsbqa.yaml', qa_yaml('hsb', 'hsbqa_shots', 'hsbqa.jsonl'))
    write_text(BASE / 'qa' / 'dsbqa.yaml', qa_yaml('dsb', 'dsbqa_shots', 'dsbqa.jsonl'))

    # Group
    group = """group: wmt26_sorbian_devsplit_fewshot_v2
task:
  - deu-hsb_devsplit_fs5_v2
  - hsb-deu_devsplit_fs5_v2
  - deu-dsb_devsplit_fs5_v2
  - dsb-deu_devsplit_fs5_v2
  - dsb-hsb_devsplit_fs5_v2
  - hsb-dsb_devsplit_fs5_v2
  - hsbqa_devsplit_fs3_v2
  - dsbqa_devsplit_fs3_v2
  - hsbsc_devsplit_fs2_v2
  - dsbsc_devsplit_fs2_v2
  - hsbgc_devsplit_fs2_v2
  - dsbgc_devsplit_fs2_v2
  - hsbmr_devsplit_fs2_v2
  - dsbmr_devsplit_fs2_v2
metadata:
  version: 2.0
"""
    write_text(BASE / 'group.yaml', group)

    # Symlink utils.py into each subdir
    utils_path = (BASE / 'utils.py').resolve()
    for subdir in ['gc', 'sc', 'mr', 'qa', 'mt']:
        target = BASE / subdir / 'utils.py'
        if target.exists() or target.is_symlink():
            target.unlink()
        target.symlink_to(utils_path)
        print(f'Symlinked {target}')


if __name__ == '__main__':
    main()
