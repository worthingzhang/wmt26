#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/zc/wmt26"
OUT_DIR="${ROOT_DIR}/data/raw/external/wikipedia"
LOG_DIR="${ROOT_DIR}/logs/data_download"
LOG_FILE="${LOG_DIR}/wikipedia_sorbian_raw_$(date +%Y%m%d_%H%M%S).log"
FORCE="${FORCE:-0}"

mkdir -p "${OUT_DIR}/hsbwiki" "${OUT_DIR}/dsbwiki" "${LOG_DIR}"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "${LOG_FILE}"
}

download_one() {
  local wiki="$1"
  local url="$2"
  local file="${OUT_DIR}/${wiki}/${wiki}-latest-pages-articles.xml.bz2"

  log "Checking ${wiki}: ${file}"
  if [[ -s "${file}" && "${FORCE}" != "1" ]]; then
    log "File exists; skipping download. Set FORCE=1 to redownload/resume explicitly."
  else
    log "Downloading ${url}"
    if command -v wget >/dev/null 2>&1; then
      wget -c -O "${file}" "${url}" 2>&1 | tee -a "${LOG_FILE}"
    elif command -v curl >/dev/null 2>&1; then
      curl -L -C - -o "${file}" "${url}" 2>&1 | tee -a "${LOG_FILE}"
    else
      log "Neither wget nor curl is available"
      return 1
    fi
  fi

  if [[ -f "${file}" ]]; then
    local bytes
    bytes="$(stat -c '%s' "${file}")"
    local sum
    sum="$(sha256sum "${file}" | awk '{print $1}')"
    log "Downloaded/skipped ${wiki}: bytes=${bytes} sha256=${sum}"
  else
    log "Missing file after download attempt: ${file}"
    return 1
  fi
}

download_one "hsbwiki" "https://dumps.wikimedia.org/hsbwiki/latest/hsbwiki-latest-pages-articles.xml.bz2"
download_one "dsbwiki" "https://dumps.wikimedia.org/dsbwiki/latest/dsbwiki-latest-pages-articles.xml.bz2"

log "Done. Log saved to ${LOG_FILE}"
