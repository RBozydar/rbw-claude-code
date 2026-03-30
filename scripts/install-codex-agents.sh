#!/usr/bin/env bash
set -euo pipefail

mode="link"
force=0
target_dir="${HOME}/.codex/agents"

usage() {
  cat <<'EOF'
Install generated Codex custom agents from this repo into ~/.codex/agents.

Usage:
  ./scripts/install-codex-agents.sh [--link|--copy] [--force] [--target-dir PATH]

Options:
  --link        Install symlinks into ~/.codex/agents (default)
  --copy        Copy files instead of symlinking
  --force       Replace existing files at the destination
  --target-dir  Override the destination directory
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --link)
      mode="link"
      ;;
    --copy)
      mode="copy"
      ;;
    --force)
      force=1
      ;;
    --target-dir)
      shift
      target_dir="${1:-}"
      if [[ -z "${target_dir}" ]]; then
        echo "Missing value for --target-dir" >&2
        exit 1
      fi
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
source_dir="${repo_root}/.codex/agents"

if [[ ! -d "${source_dir}" ]]; then
  echo "Missing generated Codex agents at ${source_dir}" >&2
  echo "Run: uv run python scripts/generate_codex_agents.py" >&2
  exit 1
fi

shopt -s nullglob
sources=("${source_dir}"/*.toml)
if [[ ${#sources[@]} -eq 0 ]]; then
  echo "No generated Codex agent files found in ${source_dir}" >&2
  exit 1
fi

mkdir -p "${target_dir}"

for src in "${sources[@]}"; do
  dest="${target_dir}/$(basename "${src}")"

  if [[ -L "${dest}" ]] && [[ "$(readlink "${dest}")" == "${src}" ]]; then
    echo "Already installed: ${dest}"
    continue
  fi

  if [[ -e "${dest}" || -L "${dest}" ]]; then
    managed=0
    if [[ -L "${dest}" ]] && [[ "$(readlink "${dest}")" == "${src}" ]]; then
      managed=1
    elif [[ -f "${dest}" ]] && grep -q '^# Generated from ' "${dest}"; then
      managed=1
    fi

    if [[ ${force} -ne 1 && ${managed} -ne 1 ]]; then
      echo "Refusing to overwrite unmanaged file: ${dest}" >&2
      echo "Re-run with --force if you want to replace it." >&2
      exit 1
    fi

    rm -f "${dest}"
  fi

  if [[ "${mode}" == "link" ]]; then
    ln -s "${src}" "${dest}"
    echo "Linked ${dest} -> ${src}"
  else
    cp "${src}" "${dest}"
    echo "Copied ${src} -> ${dest}"
  fi
done
