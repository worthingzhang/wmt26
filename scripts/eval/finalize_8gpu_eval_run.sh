#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/eval/finalize_8gpu_eval_run.sh \
    --source-run-dir <path> \
    --standard-run-dir <path> \
    --model-tag <tag> \
    --eval-setting <setting> \
    --shot-setting <shot_setting> \
    --parallel-setting <parallel_setting> \
    [--model-path <path>] \
    [--status <status>] \
    [--notes <text>] \
    [--index-path <path>] \
    [--no-symlink-artifacts] \
    [--overwrite]

Creates a standardized eval result directory by calling
scripts/eval/aggregate_eval_results.py. The source run is never deleted or moved.
USAGE
}

SOURCE_RUN_DIR=""
STANDARD_RUN_DIR=""
MODEL_TAG=""
EVAL_SETTING=""
SHOT_SETTING=""
PARALLEL_SETTING=""
MODEL_PATH=""
STATUS=""
NOTES=""
INDEX_PATH=""
NO_SYMLINK_ARTIFACTS=0
OVERWRITE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-run-dir)
      SOURCE_RUN_DIR="${2:-}"
      shift 2
      ;;
    --standard-run-dir)
      STANDARD_RUN_DIR="${2:-}"
      shift 2
      ;;
    --model-tag)
      MODEL_TAG="${2:-}"
      shift 2
      ;;
    --eval-setting)
      EVAL_SETTING="${2:-}"
      shift 2
      ;;
    --shot-setting)
      SHOT_SETTING="${2:-}"
      shift 2
      ;;
    --parallel-setting)
      PARALLEL_SETTING="${2:-}"
      shift 2
      ;;
    --model-path)
      MODEL_PATH="${2:-}"
      shift 2
      ;;
    --status)
      STATUS="${2:-}"
      shift 2
      ;;
    --notes)
      NOTES="${2:-}"
      shift 2
      ;;
    --index-path)
      INDEX_PATH="${2:-}"
      shift 2
      ;;
    --no-symlink-artifacts)
      NO_SYMLINK_ARTIFACTS=1
      shift
      ;;
    --overwrite)
      OVERWRITE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

missing=0
for name in SOURCE_RUN_DIR STANDARD_RUN_DIR MODEL_TAG EVAL_SETTING SHOT_SETTING PARALLEL_SETTING; do
  if [[ -z "${!name}" ]]; then
    echo "Missing required argument: ${name}" >&2
    missing=1
  fi
done
if [[ "$missing" -ne 0 ]]; then
  usage >&2
  exit 2
fi

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
else
  echo "Could not find python, python3, or .venv/bin/python" >&2
  exit 127
fi

cmd=(
  "$PYTHON_BIN" scripts/eval/aggregate_eval_results.py
  --source-run-dir "$SOURCE_RUN_DIR"
  --standard-run-dir "$STANDARD_RUN_DIR"
  --model-tag "$MODEL_TAG"
  --eval-setting "$EVAL_SETTING"
  --shot-setting "$SHOT_SETTING"
  --parallel-setting "$PARALLEL_SETTING"
)

if [[ -n "$MODEL_PATH" ]]; then
  cmd+=(--model-path "$MODEL_PATH")
fi
if [[ -n "$STATUS" ]]; then
  cmd+=(--status "$STATUS")
fi
if [[ -n "$NOTES" ]]; then
  cmd+=(--notes "$NOTES")
fi
if [[ -n "$INDEX_PATH" ]]; then
  cmd+=(--index-path "$INDEX_PATH")
fi
if [[ "$NO_SYMLINK_ARTIFACTS" -eq 1 ]]; then
  cmd+=(--no-symlink-artifacts)
fi
if [[ "$OVERWRITE" -eq 1 ]]; then
  cmd+=(--overwrite)
fi

"${cmd[@]}"
