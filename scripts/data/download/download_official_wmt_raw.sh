#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/zc/wmt26"
RAW_DIR="${ROOT_DIR}/data/raw/official"
LOG_DIR="${ROOT_DIR}/logs/data_download"
LOG_FILE="${LOG_DIR}/official_wmt_raw_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "${RAW_DIR}" "${LOG_DIR}"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "${LOG_FILE}"
}

check_lfs() {
  local repo_dir="$1"
  if ! git lfs version >/dev/null 2>&1; then
    log "git-lfs not available; skipping LFS pull for ${repo_dir}"
    return 0
  fi

  if git -C "${repo_dir}" lfs ls-files >/tmp/wmt26_lfs_files.$$ 2>/dev/null; then
    if [[ -s /tmp/wmt26_lfs_files.$$ ]]; then
      log "LFS files detected in ${repo_dir}; running git lfs pull"
      git -C "${repo_dir}" lfs pull 2>&1 | tee -a "${LOG_FILE}"
    else
      log "No LFS files detected in ${repo_dir}"
    fi
  else
    log "Could not inspect LFS files in ${repo_dir}; continuing"
  fi
  rm -f /tmp/wmt26_lfs_files.$$
}

ensure_repo() {
  local name="$1"
  local url="$2"
  local target="${RAW_DIR}/${name}"

  log "Checking ${name}"
  if [[ -d "${target}/.git" ]]; then
    log "Repository exists: ${target}"
    git -C "${target}" status --short 2>&1 | tee -a "${LOG_FILE}"
    git -C "${target}" rev-parse HEAD 2>&1 | tee -a "${LOG_FILE}"
    git -C "${target}" remote -v 2>&1 | tee -a "${LOG_FILE}"
    log "Fetching refs and tags without changing worktree: ${name}"
    git -C "${target}" fetch --all --tags 2>&1 | tee -a "${LOG_FILE}" || log "Fetch failed for ${name}; continuing"
  elif [[ -e "${target}" ]]; then
    log "Path exists but is not a git repository: ${target}"
  else
    log "Cloning ${url} -> ${target}"
    git clone "${url}" "${target}" 2>&1 | tee -a "${LOG_FILE}"
  fi

  if [[ -d "${target}/.git" ]]; then
    check_lfs "${target}"
  fi
}

ensure_repo "llms-limited-resources2026" "https://github.com/TUM-NLP/llms-limited-resources2026"
ensure_repo "llms-limited-resources2025" "https://github.com/TUM-NLP/llms-limited-resources2025"
ensure_repo "WMT22_UnsupVeryLowResMT_Data" "https://github.com/mariondimarco/WMT22_UnsupVeryLowResMT_Data"

log "Done. Log saved to ${LOG_FILE}"
