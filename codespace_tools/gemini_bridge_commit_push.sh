#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

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
git push origin main

echo "Pushed Gemini bridge update."
echo "Commit message: $MESSAGE"
echo "Files: ${FILES[*]}"
