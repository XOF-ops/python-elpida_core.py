#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

show_help() {
  cat <<'EOF'
Usage:
  bash codespace_tools/gemini_bridge_commit_push.sh [options] [message]

Options:
  --include-request   Always include .claude/bridge/for_gemini.md with from_gemini.md
  --from-only         Commit only .claude/bridge/from_gemini.md (no auto-include)
  --sync-first        Rebase onto origin/main before staging (recommended in active relay windows)
  --dry-run           Print what would happen without committing/pushing
  -h, --help          Show this help

Behavior:
  - Default target is .claude/bridge/from_gemini.md
  - If --from-only is NOT set and for_gemini.md has changes, it is auto-included
  - On push rejection, script rebases with autostash and retries once
EOF
}

retry_push_after_rebase() {
  local msg="${1:-}"
  local dry_run="${2:-0}"

  if [[ "$dry_run" -eq 1 ]]; then
    echo "[dry-run] git push origin main"
    echo "[dry-run] on failure: git pull --rebase --autostash origin main && git push origin main"
    return 0
  fi

  if git push origin main; then
    return 0
  fi

  echo "Initial push failed. Attempting rebase onto origin/main and retry..."

  if ! git pull --rebase --autostash origin main; then
    echo "Rebase failed. Resolve conflicts, then push manually."
    if [[ -n "$msg" ]]; then
      echo "Last intended commit message: $msg"
    fi
    exit 1
  fi

  git push origin main
}

INCLUDE_REQUEST=0
FROM_ONLY=0
SYNC_FIRST=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --include-request)
      INCLUDE_REQUEST=1
      shift
      ;;
    --from-only)
      FROM_ONLY=1
      shift
      ;;
    --sync-first)
      SYNC_FIRST=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

FILES=(".claude/bridge/from_gemini.md")
if [[ "$INCLUDE_REQUEST" -eq 1 ]]; then
  FILES+=(".claude/bridge/for_gemini.md")
elif [[ "$FROM_ONLY" -eq 0 ]]; then
  if ! git diff --quiet -- .claude/bridge/for_gemini.md || ! git diff --cached --quiet -- .claude/bridge/for_gemini.md; then
    FILES+=(".claude/bridge/for_gemini.md")
  fi
fi

if [[ "$SYNC_FIRST" -eq 1 ]]; then
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] git pull --rebase --autostash origin main"
  else
    git pull --rebase --autostash origin main
  fi
fi

for file in "${FILES[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "Missing $file. Ask Gemini/Copilot to write it first."
    exit 1
  fi
done

HAS_CHANGES=0
for file in "${FILES[@]}"; do
  if ! git diff --quiet -- "$file" || ! git diff --cached --quiet -- "$file"; then
    HAS_CHANGES=1
    break
  fi
done

if [[ "$HAS_CHANGES" -eq 0 ]]; then
  echo "No bridge changes to commit for ${FILES[*]}"
  exit 0
fi

MESSAGE="${1:-gemini hop update: $(date -u +%Y-%m-%dT%H:%M:%SZ)}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[dry-run] files: ${FILES[*]}"
  echo "[dry-run] commit message: $MESSAGE"
  exit 0
fi

git add "${FILES[@]}"

if git diff --cached --quiet; then
  echo "Nothing staged after git add."
  exit 0
fi

git commit -m "$MESSAGE"
retry_push_after_rebase "$MESSAGE" "$DRY_RUN"

echo "Pushed Gemini bridge update."
echo "Commit message: $MESSAGE"
echo "Files: ${FILES[*]}"
