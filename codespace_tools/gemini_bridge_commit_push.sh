#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

retry_push_after_rebase() {
  local msg="${1:-}"

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
if [[ "${1:-}" == "--include-request" ]]; then
  INCLUDE_REQUEST=1
  shift
fi

FILES=(".claude/bridge/from_gemini.md")
if [[ "$INCLUDE_REQUEST" -eq 1 ]]; then
  FILES+=(".claude/bridge/for_gemini.md")
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

git add "${FILES[@]}"

if git diff --cached --quiet; then
  echo "Nothing staged after git add."
  exit 0
fi

git commit -m "$MESSAGE"
retry_push_after_rebase "$MESSAGE"

echo "Pushed Gemini bridge update."
echo "Commit message: $MESSAGE"
echo "Files: ${FILES[*]}"
