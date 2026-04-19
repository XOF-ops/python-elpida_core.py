#!/usr/bin/env bash
set -euo pipefail

# Print latest D13 checkpoint evidence by layer using S3 seed objects + anchor metadata.
# Usage:
#   source .env
#   export AWS_EC2_METADATA_DISABLED=true
#   scripts/d13_checkpoint_audit.sh
#   scripts/d13_checkpoint_audit.sh --format json
#   scripts/d13_checkpoint_audit.sh --latest-n 3 --format json
#   scripts/d13_checkpoint_audit.sh --since-hours 24 --format csv
#   scripts/d13_checkpoint_audit.sh --summary --format json
#   scripts/d13_checkpoint_audit.sh --fail-on-missing-anchor --latest-n 5
#   scripts/d13_checkpoint_audit.sh --format csv mind world
#   scripts/d13_checkpoint_audit.sh mind world

EXTERNAL_BUCKET="elpida-external-interfaces"
FEDERATION_BUCKET="elpida-body-evolution"
ANCHOR_PREFIX="federation/seed_anchors"

FORMAT="text"
LATEST_N=1
SINCE_HOURS=""
SUMMARY="false"
FAIL_ON_MISSING_ANCHOR="false"
LAYERS=()

have_python3() {
  command -v python3 >/dev/null 2>&1
}

json_field() {
  local json="$1"
  local field="$2"
  python3 - "$field" "$json" <<'PY'
import json
import sys
field = sys.argv[1]
raw = sys.argv[2]
obj = json.loads(raw)
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
  scripts/d13_checkpoint_audit.sh [--format text|json|csv] [--latest-n N] [--since-hours H] [--summary] [--fail-on-missing-anchor] [mind] [body] [world] [full]

Examples:
  scripts/d13_checkpoint_audit.sh
  scripts/d13_checkpoint_audit.sh --format json
  scripts/d13_checkpoint_audit.sh --latest-n 3 --format json
  scripts/d13_checkpoint_audit.sh --since-hours 24 --format csv
  scripts/d13_checkpoint_audit.sh --summary --format json
  scripts/d13_checkpoint_audit.sh --fail-on-missing-anchor --latest-n 5
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
      --latest-n)
        if [[ $# -lt 2 ]]; then
          echo "ERROR: --latest-n requires a value" >&2
          exit 1
        fi
        LATEST_N="$2"
        shift 2
        ;;
      --latest-n=*)
        LATEST_N="${1#*=}"
        shift
        ;;
      --since-hours)
        if [[ $# -lt 2 ]]; then
          echo "ERROR: --since-hours requires a value" >&2
          exit 1
        fi
        SINCE_HOURS="$2"
        shift 2
        ;;
      --since-hours=*)
        SINCE_HOURS="${1#*=}"
        shift
        ;;
      --summary)
        SUMMARY="true"
        shift
        ;;
      --fail-on-missing-anchor)
        FAIL_ON_MISSING_ANCHOR="true"
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

  if ! [[ "$LATEST_N" =~ ^[0-9]+$ ]] || [[ "$LATEST_N" -lt 1 ]]; then
    echo "ERROR: --latest-n must be an integer >= 1" >&2
    exit 1
  fi

  if [[ -n "$SINCE_HOURS" ]]; then
    if ! [[ "$SINCE_HOURS" =~ ^[0-9]+$ ]] || [[ "$SINCE_HOURS" -lt 1 ]]; then
      echo "ERROR: --since-hours must be an integer >= 1" >&2
      exit 1
    fi
  fi

  if [[ ${#LAYERS[@]} -eq 0 ]]; then
    LAYERS=(mind body world full)
  fi
}

latest_seed_keys_for_layer() {
  local layer="$1"
  local objects_json
  objects_json="$(aws s3api list-objects-v2 \
    --bucket "$EXTERNAL_BUCKET" \
    --prefix "seeds/${layer}/" \
  --query 'Contents[].{Key:Key,LastModified:LastModified}' \
  --output json)"

  if [[ -z "$objects_json" || "$objects_json" == "null" || "$objects_json" == "[]" ]]; then
    return
  fi

  python3 - "$LATEST_N" "$SINCE_HOURS" "$objects_json" <<'PY'
import json
import sys
from datetime import datetime, timedelta, timezone

latest_n = int(sys.argv[1])
since_hours_arg = sys.argv[2]
objects_json = sys.argv[3]
since_hours = int(since_hours_arg) if since_hours_arg else None

try:
    objs = json.loads(objects_json) or []
except Exception:
  objs = []

def parse_ts(value: str) -> datetime:
  value = (value or "").strip()
  if not value:
    return datetime.min.replace(tzinfo=timezone.utc)
  if value.endswith("Z"):
    value = value[:-1] + "+00:00"
  dt = datetime.fromisoformat(value)
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
  return dt.astimezone(timezone.utc)

threshold = None
if since_hours is not None:
  threshold = datetime.now(timezone.utc) - timedelta(hours=since_hours)

rows = []
for o in objs:
  key = (o or {}).get("Key")
  ts_raw = (o or {}).get("LastModified")
  if not key:
    continue
  dt = parse_ts(ts_raw)
  if threshold is not None and dt < threshold:
    continue
  rows.append((dt, key))

rows.sort(key=lambda x: x[0], reverse=True)
for _, key in rows[:latest_n]:
  print(key)
PY
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

collect_row_for_seed_key() {
  local layer="$1"
  local seed_key="$2"

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
  python3 - "$ROWS_FILE" <<'PY'
import json
import sys

rows_file = sys.argv[1]

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
with open(rows_file, "r", encoding="utf-8") as f:
  for line in f:
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

emit_summary() {
  python3 - "$FORMAT" "$ROWS_FILE" <<'PY'
import json
import sys
from datetime import datetime, timezone

fmt = sys.argv[1]
rows_file = sys.argv[2]

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

def parse_ts(value: str):
  value = (value or "").strip()
  if not value:
    return None
  if value.endswith("Z"):
    value = value[:-1] + "+00:00"
  try:
    dt = datetime.fromisoformat(value)
  except Exception:
    try:
      # AWS head-object commonly returns RFC822-like timestamps, e.g.:
      # Sat, 18 Apr 2026 02:07:20 GMT
      dt = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %Z")
    except Exception:
      return None
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
  return dt.astimezone(timezone.utc)

rows = []
with open(rows_file, "r", encoding="utf-8") as f:
  for line in f:
    line = line.rstrip("\n")
    if not line:
      continue
    parts = line.split("\t")
    if len(parts) < len(fields):
      parts.extend([""] * (len(fields) - len(parts)))
    rows.append(dict(zip(fields, parts[: len(fields)])))

summary = {}
for row in rows:
  layer = row.get("layer", "")
  if not layer:
    continue
  entry = summary.setdefault(
    layer,
    {
      "layer": layer,
      "count": 0,
      "missing_rows": 0,
      "newest_checkpoint_id": "",
      "newest_timestamp": "",
      "oldest_checkpoint_id": "",
      "oldest_timestamp": "",
      "_newest_dt": None,
      "_oldest_dt": None,
    },
  )

  world_key = row.get("world_key", "")
  if not world_key or world_key == "None":
    entry["missing_rows"] += 1
    continue

  entry["count"] += 1
  ts_raw = row.get("world_last_modified", "")
  dt = parse_ts(ts_raw)
  if dt is None:
    continue

  if entry["_newest_dt"] is None or dt > entry["_newest_dt"]:
    entry["_newest_dt"] = dt
    entry["newest_timestamp"] = ts_raw
    entry["newest_checkpoint_id"] = row.get("checkpoint_id", "")

  if entry["_oldest_dt"] is None or dt < entry["_oldest_dt"]:
    entry["_oldest_dt"] = dt
    entry["oldest_timestamp"] = ts_raw
    entry["oldest_checkpoint_id"] = row.get("checkpoint_id", "")

ordered = []
for layer in summary:
  item = summary[layer]
  item.pop("_newest_dt", None)
  item.pop("_oldest_dt", None)
  ordered.append(item)

if fmt == "json":
  print(json.dumps(ordered, indent=2, ensure_ascii=False))
elif fmt == "csv":
  print("layer,count,missing_rows,newest_checkpoint_id,newest_timestamp,oldest_checkpoint_id,oldest_timestamp")
  for item in ordered:
    vals = [
      item["layer"],
      str(item["count"]),
      str(item["missing_rows"]),
      item["newest_checkpoint_id"],
      item["newest_timestamp"],
      item["oldest_checkpoint_id"],
      item["oldest_timestamp"],
    ]
    escaped = ['"' + v.replace('"', '""') + '"' for v in vals]
    print(",".join(escaped))
else:
  for item in ordered:
    print(f"=== LAYER: {item['layer']} ===")
    print(f"count: {item['count']}")
    print(f"missing_rows: {item['missing_rows']}")
    print(f"newest_checkpoint_id: {item['newest_checkpoint_id']}")
    print(f"newest_timestamp: {item['newest_timestamp']}")
    print(f"oldest_checkpoint_id: {item['oldest_checkpoint_id']}")
    print(f"oldest_timestamp: {item['oldest_timestamp']}")
    print()
PY
}

enforce_missing_anchor_gate() {
  local violations=0
  local row

  for row in "${ROWS[@]}"; do
    IFS=$'\t' read -r layer checkpoint_id seed_key anchor_key world_size world_last_modified anchor_size anchor_last_modified source_event source_component git_commit created_at <<< "$row"

    if [[ -n "$seed_key" && "$seed_key" != "None" ]]; then
      if [[ -z "$anchor_size" || -z "$anchor_last_modified" ]]; then
        echo "INTEGRITY VIOLATION: missing anchor for layer=${layer} checkpoint_id=${checkpoint_id} world_key=${seed_key} expected_anchor_key=${anchor_key}" >&2
        violations=$((violations + 1))
      fi
    fi
  done

  if [[ "$violations" -gt 0 ]]; then
    echo "FAIL: ${violations} row(s) had world seed without anchor evidence" >&2
    exit 2
  fi
}

require_tools
parse_args "$@"

ROWS=()

for layer in "${LAYERS[@]}"; do
  case "$layer" in
    mind|body|world|full)
      mapfile -t SEED_KEYS < <(latest_seed_keys_for_layer "$layer")
      if [[ ${#SEED_KEYS[@]} -eq 0 ]]; then
        ROWS+=("$(collect_row_for_seed_key "$layer" "None")")
      else
        for seed_key in "${SEED_KEYS[@]}"; do
          ROWS+=("$(collect_row_for_seed_key "$layer" "$seed_key")")
        done
      fi
      ;;
    *)
      echo "ERROR: unsupported layer '$layer' (allowed: mind body world full)" >&2
      exit 1
      ;;
  esac
done

ROWS_FILE="$(mktemp)"
trap 'rm -f "$ROWS_FILE"' EXIT
printf '%s\n' "${ROWS[@]}" > "$ROWS_FILE"

if [[ "$FAIL_ON_MISSING_ANCHOR" == "true" ]]; then
  enforce_missing_anchor_gate
fi

case "$FORMAT" in
  text)
    if [[ "$SUMMARY" == "true" ]]; then
      emit_summary
    else
      emit_text
    fi
    ;;
  csv)
    if [[ "$SUMMARY" == "true" ]]; then
      emit_summary
    else
      emit_csv
    fi
    ;;
  json)
    if [[ "$SUMMARY" == "true" ]]; then
      emit_summary
    else
      emit_json
    fi
    ;;
esac
