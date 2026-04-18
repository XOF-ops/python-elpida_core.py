#!/usr/bin/env bash
set -euo pipefail

# Print latest D13 checkpoint evidence by layer using S3 seed objects + anchor metadata.
# Usage:
#   source .env
#   export AWS_EC2_METADATA_DISABLED=true
#   scripts/d13_checkpoint_audit.sh
#   scripts/d13_checkpoint_audit.sh --format json
#   scripts/d13_checkpoint_audit.sh --format csv mind world
#   scripts/d13_checkpoint_audit.sh mind world

EXTERNAL_BUCKET="elpida-external-interfaces"
FEDERATION_BUCKET="elpida-body-evolution"
ANCHOR_PREFIX="federation/seed_anchors"

FORMAT="text"
LAYERS=()

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

print_usage() {
  cat <<'USAGE'
Usage:
  scripts/d13_checkpoint_audit.sh [--format text|json|csv] [mind] [body] [world] [full]

Examples:
  scripts/d13_checkpoint_audit.sh
  scripts/d13_checkpoint_audit.sh --format json
  scripts/d13_checkpoint_audit.sh --format csv mind world
USAGE
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --format)
        if [[ $# -lt 2 ]]; then
          echo "ERROR: --format requires a value" >&2
          exit 1
        fi
        FORMAT="$2"
        shift 2
        ;;
      --format=*)
        FORMAT="${1#*=}"
        shift
        ;;
      -h|--help)
        print_usage
        exit 0
        ;;
      mind|body|world|full)
        LAYERS+=("$1")
        shift
        ;;
      *)
        echo "ERROR: unsupported argument '$1'" >&2
        print_usage >&2
        exit 1
        ;;
    esac
  done

  case "$FORMAT" in
    text|json|csv) ;;
    *)
      echo "ERROR: unsupported format '$FORMAT' (allowed: text json csv)" >&2
      exit 1
      ;;
  esac

  if [[ ${#LAYERS[@]} -eq 0 ]]; then
    LAYERS=(mind body world full)
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

collect_layer_row() {
  local layer="$1"

  local seed_key
  seed_key="$(latest_seed_key_for_layer "$layer")"

  local checkpoint_id=""
  local anchor_key=""
  local world_size=""
  local world_last_modified=""
  local anchor_size=""
  local anchor_last_modified=""
  local source_event=""
  local source_component=""
  local git_commit=""
  local created_at=""

  if [[ -z "$seed_key" || "$seed_key" == "None" ]]; then
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$layer" "$checkpoint_id" "$seed_key" "$anchor_key" "$world_size" "$world_last_modified" \
      "$anchor_size" "$anchor_last_modified" "$source_event" "$source_component" "$git_commit" "$created_at"
    return
  fi

  checkpoint_id="$(basename "$seed_key" .tar.gz)"
  anchor_key="${ANCHOR_PREFIX}/${checkpoint_id}.json"

  local seed_head
  seed_head="$(head_object_json "$EXTERNAL_BUCKET" "$seed_key")"
  world_size="$(json_field "$seed_head" Size)"
  world_last_modified="$(json_field "$seed_head" LastModified)"

  local anchor_head=""
  local anchor_exists="false"
  if anchor_head="$(head_object_json "$FEDERATION_BUCKET" "$anchor_key" 2>/dev/null)"; then
    anchor_exists="true"
    anchor_size="$(json_field "$anchor_head" Size)"
    anchor_last_modified="$(json_field "$anchor_head" LastModified)"
  fi

  if [[ "$anchor_exists" == "true" ]]; then
    local anchor_json
    anchor_json="$(aws s3 cp "s3://${FEDERATION_BUCKET}/${anchor_key}" - --no-progress)"
    source_event="$(json_field "$anchor_json" source_event)"
    source_component="$(json_field "$anchor_json" source_component)"
    git_commit="$(json_field "$anchor_json" git_commit)"
    created_at="$(json_field "$anchor_json" created_at)"
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$layer" "$checkpoint_id" "$seed_key" "$anchor_key" "$world_size" "$world_last_modified" \
    "$anchor_size" "$anchor_last_modified" "$source_event" "$source_component" "$git_commit" "$created_at"
}

csv_escape() {
  local value="$1"
  value="${value//\"/\"\"}"
  printf '"%s"' "$value"
}

emit_text() {
  local row
  for row in "${ROWS[@]}"; do
    IFS=$'\t' read -r layer checkpoint_id seed_key anchor_key world_size world_last_modified anchor_size anchor_last_modified source_event source_component git_commit created_at <<< "$row"

    echo "=== LAYER: ${layer} ==="
    if [[ -z "$seed_key" || "$seed_key" == "None" ]]; then
      echo "seed_key: MISSING"
      echo
      continue
    fi

    echo "checkpoint_id: ${checkpoint_id}"
    echo "world_key: ${seed_key}"
    echo "anchor_key: ${anchor_key}"
    echo "world_head: {\"Size\":${world_size:-0},\"LastModified\":\"${world_last_modified}\"}"
    if [[ -n "$anchor_size" || -n "$anchor_last_modified" ]]; then
      echo "anchor_head: {\"Size\":${anchor_size:-0},\"LastModified\":\"${anchor_last_modified}\"}"
    else
      echo "anchor_head: MISSING"
    fi

    if [[ -n "$source_event" || -n "$source_component" || -n "$git_commit" || -n "$created_at" ]]; then
      echo "anchor_meta: {\"source_event\":\"${source_event}\",\"source_component\":\"${source_component}\",\"git_commit\":\"${git_commit}\",\"created_at\":\"${created_at}\"}"
    fi

    echo
  done
}

emit_csv() {
  echo "layer,checkpoint_id,world_key,anchor_key,world_size,world_last_modified,anchor_size,anchor_last_modified,source_event,source_component,git_commit,created_at"
  local row
  for row in "${ROWS[@]}"; do
    IFS=$'\t' read -r layer checkpoint_id seed_key anchor_key world_size world_last_modified anchor_size anchor_last_modified source_event source_component git_commit created_at <<< "$row"
    csv_escape "$layer"; echo -n ","
    csv_escape "$checkpoint_id"; echo -n ","
    csv_escape "$seed_key"; echo -n ","
    csv_escape "$anchor_key"; echo -n ","
    csv_escape "$world_size"; echo -n ","
    csv_escape "$world_last_modified"; echo -n ","
    csv_escape "$anchor_size"; echo -n ","
    csv_escape "$anchor_last_modified"; echo -n ","
    csv_escape "$source_event"; echo -n ","
    csv_escape "$source_component"; echo -n ","
    csv_escape "$git_commit"; echo -n ","
    csv_escape "$created_at"
    echo
  done
}

emit_json() {
  printf '%s\n' "${ROWS[@]}" | python3 - <<'PY'
import json
import sys

fields = [
    "layer",
    "checkpoint_id",
    "world_key",
    "anchor_key",
    "world_size",
    "world_last_modified",
    "anchor_size",
    "anchor_last_modified",
    "source_event",
    "source_component",
    "git_commit",
    "created_at",
]

rows = []
for line in sys.stdin:
    line = line.rstrip("\n")
    if not line:
        continue
    parts = line.split("\t")
    if len(parts) < len(fields):
        parts.extend([""] * (len(fields) - len(parts)))
    rows.append(dict(zip(fields, parts[: len(fields)])))

print(json.dumps(rows, indent=2, ensure_ascii=False))
PY
}

require_tools
parse_args "$@"

ROWS=()

for layer in "${LAYERS[@]}"; do
  case "$layer" in
    mind|body|world|full)
      ROWS+=("$(collect_layer_row "$layer")")
      ;;
    *)
      echo "ERROR: unsupported layer '$layer' (allowed: mind body world full)" >&2
      exit 1
      ;;
  esac
done

case "$FORMAT" in
  text)
    emit_text
    ;;
  csv)
    emit_csv
    ;;
  json)
    emit_json
    ;;
esac
