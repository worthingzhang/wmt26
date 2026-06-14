# Base Model Status

Report generated: 2026-06-15  
Last updated: 2026-06-15

## Target Base Model

- **Model ID**: `Qwen/Qwen3.5-2B`
- **Project standard path**: `/home/zc/wmt26/models/base/Qwen3.5-2B`

## Status Summary

✅ **Model is available at the project standard path.**

The model was copied from the local Hugging Face cache to `/home/zc/wmt26/models/base/Qwen3.5-2B`. All subsequent environments (main/eval, LlamaFactory CPT/SFT, future OPD) should reference this standard path.

## 1. Standard Model Directory

```text
/home/zc/wmt26/models/base/Qwen3.5-2B
```

**Status**: directory exists and contains the full model files (real files, not symlinks).

Key files present:

- `config.json`
- `tokenizer.json`
- `tokenizer_config.json`
- `model.safetensors.index.json`
- `model.safetensors-00001-of-00001.safetensors` (single shard, ~4.3 GB)
- `preprocessor_config.json`
- `chat_template.jinja`
- `vocab.json`, `merges.txt`
- `README.md`, `LICENSE`, `.gitattributes`

Total size: ~4.3 GB.

## 2. Copy Details

- **Source**: `/home/zc/.cache/huggingface/hub/models--Qwen--Qwen3.5-2B/snapshots/15852e8c16360a2fea060d615a32b45270f8a8fc`
- **Target**: `/home/zc/wmt26/models/base/Qwen3.5-2B`
- **Command used**: `cp -aL "$SOURCE"/. "$TARGET"/`
- **Rationale**: `-L` dereferences HF cache symlinks so the target contains real files independent of the HF cache lifetime.

## 3. Lightweight Load Check

Loaded only `AutoConfig` and `AutoTokenizer` from the standard path (no model weights, no GPU):

```text
model_path: /home/zc/wmt26/models/base/Qwen3.5-2B
model_type: qwen3_5
vocab_size: None
tokenizer: Qwen2Tokenizer
OK: config/tokenizer loaded
```

## 4. Registry

Registered in `models/registry/models.jsonl` as `base_qwen35_2b`.

## 5. Notes

- Do **not** add model weights to git (they are already ignored by `.gitignore`).
- Do **not** move or delete the HF cache unless disk space is required; the project now uses the copied files at the standard path.
- All training and evaluation scripts should use `/home/zc/wmt26/models/base/Qwen3.5-2B`.

## 6. Quick Verification

```bash
source /home/zc/wmt26/.venv/bin/activate
python - <<'PY'
from pathlib import Path
from transformers import AutoConfig, AutoTokenizer

model_path = Path("/home/zc/wmt26/models/base/Qwen3.5-2B")
assert model_path.exists(), "model path missing"
assert (model_path / "config.json").exists(), "config.json missing"
assert (model_path / "tokenizer.json").exists(), "tokenizer.json missing"

cfg = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
tok = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
print("model_type:", getattr(cfg, "model_type", None))
print("tokenizer:", type(tok).__name__)
print("OK")
PY
```
