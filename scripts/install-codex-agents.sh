#!/usr/bin/env bash
set -euo pipefail

mode="link"
force=0
target_home="${HOME}/.codex"

usage() {
  cat <<'EOF'
Install generated Codex custom agents and prompts from this repo into ~/.codex.

Usage:
  ./scripts/install-codex-agents.sh [--link|--copy] [--force] [--target-dir PATH]

Options:
  --link        Install symlinks into ~/.codex (default)
  --copy        Copy files instead of symlinking
  --force       Replace existing files at the destination
  --target-dir  Override the Codex home directory
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
      target_home="${1:-}"
      if [[ -z "${target_home}" ]]; then
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
agents_source_dir="${repo_root}/.codex/agents"
prompts_source_dir="${repo_root}/.codex/prompts"
agents_target_dir="${target_home}/agents"
prompts_target_dir="${target_home}/prompts"

install_group() {
  local label="$1"
  local source_dir="$2"
  local target_dir="$3"
  local glob_pattern="$4"
  local managed_pattern="$5"
  local -a sources

  if [[ ! -d "${source_dir}" ]]; then
    echo "Missing generated Codex ${label}s at ${source_dir}" >&2
    echo "Run: uv run python scripts/generate_codex_agents.py" >&2
    exit 1
  fi

  shopt -s nullglob
  sources=("${source_dir}"/${glob_pattern})
  shopt -u nullglob

  if [[ ${#sources[@]} -eq 0 ]]; then
    echo "No generated Codex ${label} files found in ${source_dir}" >&2
    exit 1
  fi

  mkdir -p "${target_dir}"

  for src in "${sources[@]}"; do
    local dest="${target_dir}/$(basename "${src}")"
    local managed=0

    if [[ -L "${dest}" ]] && [[ "$(readlink "${dest}")" == "${src}" ]]; then
      echo "Already installed: ${dest}"
      continue
    fi

    if [[ -e "${dest}" || -L "${dest}" ]]; then
      if [[ -L "${dest}" ]] && [[ "$(readlink "${dest}")" == "${src}" ]]; then
        managed=1
      elif [[ -f "${dest}" ]] && grep -q "${managed_pattern}" "${dest}"; then
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
}

install_group "agent" "${agents_source_dir}" "${agents_target_dir}" "*.toml" '^# Generated from '
install_group "prompt" "${prompts_source_dir}" "${prompts_target_dir}" "*.md" '<!-- Generated from '
