---
library_name: transformers
license: other
base_model: /home/zc/wmt26/models/base/Qwen3.5-2B
tags:
- llama-factory
- full
- generated_from_trainer
model-index:
- name: cpt_v1_official_plaintext_dsb4x_smoke
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# cpt_v1_official_plaintext_dsb4x_smoke

This model is a fine-tuned version of [/home/zc/wmt26/models/base/Qwen3.5-2B](https://huggingface.co//home/zc/wmt26/models/base/Qwen3.5-2B) on the cpt_v1_official_plaintext_dsb4x dataset.

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 1e-05
- train_batch_size: 1
- eval_batch_size: 8
- seed: 42
- distributed_type: multi-GPU
- num_devices: 8
- total_train_batch_size: 8
- total_eval_batch_size: 64
- optimizer: Use OptimizerNames.ADAMW_TORCH with betas=(0.9,0.999) and epsilon=1e-08 and optimizer_args=No additional optimizer arguments
- lr_scheduler_type: cosine
- lr_scheduler_warmup_steps: 0.03
- training_steps: 20

### Training results



### Framework versions

- Transformers 5.2.0
- Pytorch 2.7.0+cu126
- Datasets 4.0.0
- Tokenizers 0.22.2
