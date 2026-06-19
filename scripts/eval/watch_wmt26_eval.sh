#!/usr/bin/env bash
# Show a human-readable dashboard for WMT26 task-sharded eval runs.
#
# Usage:
#   bash scripts/eval/watch_wmt26_eval.sh [RUN_DIR]
#   bash scripts/eval/watch_wmt26_eval.sh [RUN_DIR] --watch 30

set -euo pipefail

PROJECT_ROOT="/home/zc/wmt26"
DEFAULT_PARENT="${PROJECT_ROOT}/runs/eval/Qwen3.5-2B/devsplit_fewshot_v1_8gpu"
PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
    PYTHON_BIN="python3"
fi

RUN_DIR=""
WATCH_INTERVAL=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --watch)
            WATCH_INTERVAL="$2"
            shift 2
            ;;
        -h|--help)
            sed -n '1,12p' "$0"
            exit 0
            ;;
        *)
            if [[ -z "${RUN_DIR}" ]]; then
                RUN_DIR="$1"
                shift
            else
                echo "Unknown argument: $1" >&2
                exit 1
            fi
            ;;
    esac
done

if [[ -z "${RUN_DIR}" ]]; then
    RUN_DIR="$(find "${DEFAULT_PARENT}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -n 1)"
fi

if [[ -z "${RUN_DIR}" || ! -d "${RUN_DIR}" ]]; then
    echo "Error: run directory not found. Pass RUN_DIR explicitly." >&2
    exit 1
fi

render_once() {
    "${PYTHON_BIN}" - "${RUN_DIR}" <<'PY'
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path


run_dir = Path(sys.argv[1]).resolve()
logs_dir = run_dir / "logs"
commands_dir = run_dir / "commands"
status_dir = run_dir / "status"

TERM_WIDTH = shutil.get_terminal_size((120, 24)).columns
BAR_WIDTH = 28 if TERM_WIDTH >= 110 else 18
USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def color(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def get_gpu_stats() -> dict[str, dict[str, str]]:
    if shutil.which("nvidia-smi") is None:
        return {}
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return {}

    stats: dict[str, dict[str, str]] = {}
    for line in out.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            continue
        idx, mem_used, mem_total, util = parts
        stats[idx] = {
            "mem": f"{mem_used}/{mem_total} MiB",
            "util": f"{util}%",
        }
    return stats


def parse_command(name: str) -> tuple[str, str]:
    path = commands_dir / f"{name}.sh"
    if not path.exists():
        return "?", "?"
    text = path.read_text(encoding="utf-8", errors="replace")

    gpu_match = re.search(r"CUDA_VISIBLE_DEVICES=([^\s]+)", text)
    gpu = gpu_match.group(1) if gpu_match else "?"

    task_match = re.search(r"\s--tasks\s+(.+?)\s+--apply_chat_template", text, re.S)
    tasks = " ".join(task_match.group(1).split()) if task_match else "?"
    return gpu, tasks


def parse_status(name: str) -> str:
    path = status_dir / f"{name}.status"
    if not path.exists():
        return "RUNNING"
    code = path.read_text(encoding="utf-8", errors="replace").strip()
    if code == "0":
        return "DONE"
    if not code:
        return "DONE?"
    return f"FAILED({code})"


def parse_progress(log_path: Path) -> dict[str, str | int | None]:
    text = log_path.read_text(encoding="utf-8", errors="replace").replace("\r", "\n")
    matches = re.findall(
        r"Running (generate_until|loglikelihood) requests:\s*"
        r"(\d+)%.*?\|\s*(\d+)/(\d+)\s*\[([^\]]+)\]",
        text,
    )
    if not matches:
        return {
            "request": "-",
            "pct": None,
            "current": None,
            "total": None,
            "elapsed": "?",
            "eta": "?",
            "speed": "starting",
        }

    req_type, pct, current, total, bracket = matches[-1]
    parts = [p.strip() for p in bracket.split(",")]
    elapsed_eta = parts[0] if len(parts) > 0 else "?"
    if "<" in elapsed_eta:
        elapsed, eta = [p.strip() for p in elapsed_eta.split("<", 1)]
    else:
        elapsed, eta = elapsed_eta, "?"
    speed = parts[1] if len(parts) > 1 else "?"
    return {
        "request": req_type,
        "pct": int(pct),
        "current": int(current),
        "total": int(total),
        "elapsed": elapsed,
        "eta": eta,
        "speed": speed,
    }


def shorten(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    return text[: max(0, width - 1)] + "…"


def progress_bar(pct: int | None, width: int = BAR_WIDTH) -> str:
    if pct is None:
        return "[" + "." * width + "]"
    pct = max(0, min(100, pct))
    filled = round(width * pct / 100)
    return "[" + "#" * filled + "." * (width - filled) + "]"


def state_label(state: str) -> str:
    if state == "DONE":
        return color(state, "32;1")
    if state.startswith("FAILED"):
        return color(state, "31;1")
    if state == "RUNNING":
        return color(state, "36;1")
    return state


def pct_label(pct: int | None) -> str:
    if pct is None:
        return "  ?%"
    return f"{pct:3d}%"


gpu_stats = get_gpu_stats()
log_files = sorted(logs_dir.glob("*.log"))
session = "unknown"
manifest_path = run_dir / "manifest.json"
if manifest_path.exists():
    try:
        session = json.loads(manifest_path.read_text(encoding="utf-8")).get("tmux_session", session)
    except Exception:
        pass

if not log_files:
    print(f"WMT26 eval monitor  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"RUN_DIR: {run_dir}")
    print()
    print("No logs found yet.")
    sys.exit(0)

rows = []
for log_path in log_files:
    name = log_path.stem
    gpu, tasks = parse_command(name)
    state = parse_status(name)
    progress = parse_progress(log_path)
    stats = gpu_stats.get(gpu, {"mem": "?", "util": "?"})
    rows.append(
        {
            "name": name,
            "gpu": gpu,
            "tasks": tasks,
            "state": state,
            "stats": stats,
            "progress": progress,
        }
    )

done_count = sum(1 for row in rows if row["state"] == "DONE")
failed_count = sum(1 for row in rows if str(row["state"]).startswith("FAILED"))
running_count = sum(1 for row in rows if row["state"] == "RUNNING")
known_totals = [row["progress"] for row in rows if row["progress"]["current"] is not None]
current_sum = sum(int(p["current"]) for p in known_totals)
total_sum = sum(int(p["total"]) for p in known_totals)
overall_pct = round(current_sum * 100 / total_sum) if total_sum else None

print(color("WMT26 Eval Monitor", "1"))
print(f"Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Run dir: {run_dir}")
print(
    "Shards:  "
    f"{state_label('RUNNING')} {running_count}   "
    f"{state_label('DONE')} {done_count}   "
    f"{state_label('FAILED(0)').replace('(0)', '')} {failed_count}"
)
if total_sum:
    print(f"Overall: {progress_bar(overall_pct)} {pct_label(overall_pct)}  {current_sum}/{total_sum} requests")
print()

print(color("GPU / shard progress", "1"))
for row in rows:
    p = row["progress"]
    current = p["current"]
    total = p["total"]
    counts = f"{current}/{total}" if current is not None and total is not None else "starting"
    left = p["eta"] if p["eta"] not in (None, "?") else "?"
    elapsed = p["elapsed"] if p["elapsed"] not in (None, "?") else "?"
    speed = p["speed"] or "?"
    tasks = shorten(str(row["tasks"]), max(32, TERM_WIDTH - 92))
    if USE_COLOR:
        title = f"GPU {row['gpu']:<2} {state_label(str(row['state']))}"
    else:
        title = f"GPU {row['gpu']:<2} {str(row['state']):<10}"
    print(
        f"{title}  "
        f"{shorten(str(row['name']), 18):<18}  "
        f"{progress_bar(p['pct'])} {pct_label(p['pct'])}  "
        f"{counts:<11}  "
        f"ETA {left:<9}  "
        f"elapsed {elapsed:<8}  "
        f"{row['stats']['util']:<4} {row['stats']['mem']:<16}"
    )
    print(f"      task: {tasks}")
    print(f"      req:  {p['request']}  speed: {speed}")
print()

print("Legend: DONE means status code 0. FAILED(n) means the shard exited with code n.")
print(f"Attach: tmux attach -t {session}")
PY
}

if [[ -n "${WATCH_INTERVAL}" ]]; then
    while true; do
        clear
        render_once
        sleep "${WATCH_INTERVAL}"
    done
else
    render_once
fi
