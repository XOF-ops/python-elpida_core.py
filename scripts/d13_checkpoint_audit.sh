#!/usr/bin/env bash
set -euo pipefail

# Print latest D13 checkpoint evidence by layer using S3 seed objects + anchor metadata.
# Usage:
#   source .env
#   export AWS_EC2_METADATA_DISABLED=true
#   scripts/d13_checkpoint_audit.sh
#   scripts/d13_checkpoint_audit.sh mind world

EXTERNAL_BUCKET="elpida-external-interfaces"
FEDERATION_BUCKET="elpida-body-evolution"
ANCHOR_PREFIX="federation/seed_anchors"

if [[ $# -gt 0 ]]; then
  LAYERS=("$@")
else
  LAYERS=(mind body world full)
fi

have_python3() {
  command -v python3 >/dev/null 2>&1
}

json_field() {
  local json="$1"
  local field="$2"
  python3 - "$field" <<'PY' <<<"$json"
import json
import sys
field = sys.argv[1]
obj = json.load(sys.stdin)
print(obj.get(field, ""))
PY
}

require_tools() {
  if ! command -v aws >/dev/null 2>&1; then
    echo "ERROR: aws CLI not found" >&2
    exit 1
  fi
  if ! have_python3; then
    echo "ERROR: python3 is required" >&2
    exit 1
  fi
}

latest_seed_key_for_layer() {
  local layer="$1"
  aws s3api list-objects-v2 \
    --bucket "$EXTERNAL_BUCKET" \
    --prefix "seeds/${layer}/" \
    --query 'reverse(sort_by(Contents,&LastModified))[0].Key' \
    --output text
}

head_object_json() {
  local bucket="$1"
  local key="$2"
  aws s3api head-object \
    --bucket "$bucket" \
    --key "$key" \
    --query '{Size:ContentLength,LastModified:LastModified}' \
    --output json
}

print_layer_report() {
  local layer="$1"

  echo "=== LAYER: ${layer} ==="

  local seed_key
  seed_key="$(latest_seed_key_for_layer "$layer")"

  if [[ -z "$seed_key" || "$seed_key" == "None" ]]; then
    echo "seed_key: MISSING"
    echo
    return
  fi

  local checkpoint_id
  checkpoint_id="$(basename "$seed_key" .tar.gz)"

  local anchor_key="${ANCHOR_PREFIX}/${checkpoint_id}.json"

  local seed_head
  seed_head="$(head_object_json "$EXTERNAL_BUCKET" "$seed_key")"

  local anchor_head=""
  local anchor_exists="false"
  if anchor_head="$(head_object_json "$FEDERATION_BUCKET" "$anchor_key" 2>/dev/null)"; then
    anchor_exists="true"
  fi

  local source_event=""
  local source_component=""
  local git_commit=""
  local created_at=""

  if [[ "$anchor_exists" == "true" ]]; then
    local anchor_json
    anchor_json="$(aws s3 cp "s3://${FEDERATION_BUCKET}/${anchor_key}" - --no-progress)"
    source_event="$(json_field "$anchor_json" source_event)"
    source_component="$(json_field "$anchor_json" source_component)"
    git_commit="$(json_field "$anchor_json" git_commit)"
    created_at="$(json_field "$anchor_json" created_at)"
  fi

  echo "checkpoint_id: ${checkpoint_id}"
  echo "world_key: ${seed_key}"
  echo "anchor_key: ${anchor_key}"
  echo "world_head: ${seed_head}"
  if [[ "$anchor_exists" == "true" ]]; then
    echo "anchor_head: ${anchor_head}"
  else
    echo "anchor_head: MISSING"
  fi

  if [[ -n "$source_event" || -n "$source_component" || -n "$git_commit" || -n "$created_at" ]]; then
    echo "anchor_meta: {\"source_event\":\"${source_event}\",\"source_component\":\"${source_component}\",\"git_commit\":\"${git_commit}\",\"created_at\":\"${created_at}\"}"
  fi

  echo
}

require_tools

for layer in "${LAYERS[@]}"; do
  case "$layer" in
    mind|body|world|full)
      print_layer_report "$layer"
      ;;
    *)
      echo "ERROR: unsupported layer '$layer' (allowed: mind body world full)" >&2
      exit 1
      ;;
  esac
done
