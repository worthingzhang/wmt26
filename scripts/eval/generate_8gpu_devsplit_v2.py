#!/usr/bin/env python3
"""Generate 8-GPU sharded eval commands for devsplit_fewshot_v2.

This mirrors the ad-hoc sharding used for devsplit_fewshot_v1_8gpu but is
checked in so the v2 profile can be reproduced.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path("/home/zc/wmt26")
OFFICIAL_EVAL_DIR = PROJECT_ROOT / "repos/official_eval"
TASKS_DIR = PROJECT_ROOT / "configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v2"

SHARDS = [
    ("gpu0_qa", 0, ["hsbqa_devsplit_fs3_v2", "dsbqa_devsplit_fs3_v2"]),
    ("gpu1_sc", 1, ["hsbsc_devsplit_fs2_v2", "dsbsc_devsplit_fs2_v2"]),
    ("gpu2_gc", 2, ["hsbgc_devsplit_fs2_v2", "dsbgc_devsplit_fs2_v2"]),
    ("gpu3_mr", 3, ["hsbmr_devsplit_fs2_v2", "dsbmr_devsplit_fs2_v2"]),
    ("gpu4_mt_de_hsb", 4, ["deu-hsb_devsplit_fs5_v2", "hsb-deu_devsplit_fs5_v2"]),
    ("gpu5_mt_de_dsb", 5, ["deu-dsb_devsplit_fs5_v2", "dsb-deu_devsplit_fs5_v2"]),
    ("gpu6_mt_dsb_hsb", 6, ["dsb-hsb_devsplit_fs5_v2"]),
    ("gpu7_mt_hsb_dsb", 7, ["hsb-dsb_devsplit_fs5_v2"]),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", default="/home/zc/wmt26/models/base/Qwen3.5-2B")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--timestamp", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    commands_dir = output_dir / "commands"
    logs_dir = output_dir / "logs"
    status_dir = output_dir / "status"
    shards_dir = output_dir / "shards"

    for d in (commands_dir, logs_dir, status_dir, shards_dir):
        d.mkdir(parents=True, exist_ok=True)

    for shard_name, gpu_id, tasks in SHARDS:
        task_list = " ".join(tasks)
        shard_out = shards_dir / shard_name
        shard_out.mkdir(parents=True, exist_ok=True)

        script = f"""#!/usr/bin/env bash
set -o pipefail
cd "{OFFICIAL_EVAL_DIR}"
source "{PROJECT_ROOT}/configs/env/mirrors.env"
source "{PROJECT_ROOT}/.venv/bin/activate"
export CUDA_VISIBLE_DEVICES={gpu_id}
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
python -m lm_eval run \
  --model hf \
  --model_args "pretrained={args.model_path},trust_remote_code=True,dtype=bfloat16,enable_thinking=False" \
  --include_path "{TASKS_DIR}" \
  --tasks {task_list} \
  --apply_chat_template \
  --batch_size 1 \
  --device cuda:0 \
  --output_path "{shard_out}" \
  --log_samples \
  2>&1 | tee "{logs_dir / shard_name}.log"
status=${{PIPESTATUS[0]}}
echo ${{status}} > "{status_dir / shard_name}.status"
exit ${{status}}
"""
        (commands_dir / f"{shard_name}.sh").write_text(script)
        print(f"Wrote {commands_dir / shard_name}.sh")

    # README
    readme = f"""Monitor:
  bash {PROJECT_ROOT}/scripts/eval/watch_wmt26_eval.sh {output_dir}
  bash {PROJECT_ROOT}/scripts/eval/watch_wmt26_eval.sh {output_dir} --watch 30
Attach:
  tmux attach -t wmt26-fs8-{args.timestamp}
"""
    (output_dir / "README.txt").write_text(readme)

    # Save manifest
    import json
    manifest = {
        "eval_id": f"Qwen3.5-2B_devsplit_fewshot_v2_8gpu_{args.timestamp}",
        "model_id": Path(args.model_path).name,
        "model_path": args.model_path,
        "profile": "devsplit_fewshot_v2",
        "run_profile": "devsplit_fewshot_v2_8gpu",
        "timestamp": args.timestamp,
        "tmux_session": f"wmt26-fs8-{args.timestamp}",
        "output_dir": str(output_dir),
        "tasks_dir": str(TASKS_DIR),
        "official_eval_dir": str(OFFICIAL_EVAL_DIR),
        "notes": "8 GPU task-sharded devsplit_fewshot_v2 eval",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"\nRun all shards with:")
    print(f"  bash {commands_dir}/*.sh")


if __name__ == "__main__":
    main()
