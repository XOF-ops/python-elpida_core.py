#!/usr/bin/env python3
"""
Elpida Dual-Layer Monitor
=========================
Polls MIND (S3) + BODY (HF Space + S3) simultaneously.
Run:  python3 monitor.py [--once] [--interval 60]

Requires in .env:
  AWS_ACCESS_KEY_ID        — already present
  AWS_SECRET_ACCESS_KEY    — already present
  HF_TOKEN                 — needs a FRESH token with 'manage' on the Space
                             (old token is expired; see README below)
"""

import os, sys, json, time, argparse, textwrap
import boto3, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Credentials ──────────────────────────────────────────────────────────────
def _load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

HF_TOKEN   = os.environ.get("HF_TOKEN", "")
HF_SPACE   = "z65nik/Elpida-Governance-Layer"
AWS_KEY    = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-central-1")

BUCKET_MIND  = os.environ.get("AWS_S3_BUCKET_MIND",  "elpida-consciousness")
BUCKET_BODY  = os.environ.get("AWS_S3_BUCKET_BODY",  "elpida-body-evolution")
BUCKET_WORLD = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")

# ── S3 client ─────────────────────────────────────────────────────────────────
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    region_name=AWS_REGION,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _age(dt: datetime) -> str:
    secs = (datetime.now(timezone.utc) - dt).total_seconds()
    if secs < 120:   return f"{int(secs)}s ago"
    if secs < 3600:  return f"{int(secs/60)}m ago"
    return f"{secs/3600:.1f}h ago"

def _s3_get_json(bucket: str, key: str) -> dict:
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(obj["Body"].read().decode("utf-8", errors="replace"))
    except Exception:
        return {}

def _s3_get_text(bucket: str, key: str, last_bytes: int = 4096) -> str:
    """Read the tail of a (potentially large) S3 object."""
    try:
        meta = s3.head_object(Bucket=bucket, Key=key)
        size = meta["ContentLength"]
        start = max(0, size - last_bytes)
        obj = s3.get_object(Bucket=bucket, Key=key, Range=f"bytes={start}-{size}")
        raw = obj["Body"].read().decode("utf-8", errors="replace")
        # drop partial first line
        return raw[raw.find("\n")+1:] if start > 0 else raw
    except Exception as e:
        return f"[S3 error: {e}]"

def _s3_latest_objects(bucket: str, prefix: str, n: int = 3):
    try:
        r = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=100)
        objs = sorted(r.get("Contents", []), key=lambda x: x["LastModified"], reverse=True)
        return objs[:n]
    except Exception:
        return []

def _hf_api(path: str) -> dict:
    if not HF_TOKEN:
        return {"_error": "no HF_TOKEN"}
    try:
        req = urllib.request.Request(
            f"https://huggingface.co/api/{path}",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"_error": str(e)}

# ── Snapshot collectors ───────────────────────────────────────────────────────

def snapshot_mind() -> dict:
    """Read MIND state from s3://elpida-consciousness"""
    result = {}

    # Latest evolution memory entries
    raw_tail = _s3_get_text(BUCKET_MIND, "memory/elpida_evolution_memory.jsonl", last_bytes=8192)
    entries = []
    for line in raw_tail.strip().splitlines():
        try:
            entries.append(json.loads(line))
        except Exception:
            pass

    cycles = [e for e in entries if e.get("type") in ("NATIVE_CYCLE", "NATIVE_CYCLE_INSIGHT")]
    merges = [e for e in entries if e.get("type") == "FEEDBACK_MERGE"]
    result["last_native_cycle"] = cycles[-1] if cycles else {}
    result["last_feedback_merge"] = merges[-1] if merges else {}

    # Kernel state
    kernel = _s3_get_json(BUCKET_MIND, "memory/kernel.json")
    result["kernel"] = kernel

    return result


def snapshot_body() -> dict:
    """Read BODY state from S3 + HF Space API"""
    result = {}

    # HF Space runtime
    space_data = _hf_api(f"spaces/{HF_SPACE}")
    runtime = space_data.get("runtime", {})
    result["hf_space"] = {
        "stage": runtime.get("stage", space_data.get("_error", "?")),
        "error": runtime.get("errorMessage", "none"),
        "sha":   space_data.get("sha", "?")[:12],
        "hardware": runtime.get("hardware", {}).get("current", "?"),
    }

    # HF Space heartbeat from S3 (component heartbeat)
    hb = _s3_get_json(BUCKET_BODY, "heartbeat/hf_space.json")
    hb_ts = hb.get("timestamp", "?")
    result["body_heartbeat"] = {
        "ts":              hb_ts,
        "mind_cache_lines": hb.get("mind_cache_lines", "?"),
        "feedback_cache":  hb.get("feedback_cache_lines", "?"),
        "governance_votes": hb.get("governance_votes", "?"),
        "age":             _age(datetime.fromisoformat(hb_ts)) if hb_ts != "?" else "?",
    }

    # Federation heartbeat (richer body state)
    fed = _s3_get_json(BUCKET_BODY, "federation/body_heartbeat.json")
    fed_ts = fed.get("timestamp", "?")
    result["federation"] = {
        "ts":           fed_ts,
        "body_cycle":   fed.get("body_cycle", "?"),
        "coherence":    fed.get("coherence", "?"),
        "rhythm":       fed.get("current_rhythm", "?"),
        "axiom":        fed.get("dominant_axiom", "?"),
        "approval_rate":fed.get("approval_rate", "?"),
        "watch":        fed.get("current_watch", "?"),
        "d15_count":    fed.get("d15_broadcast_count", "?"),
        "buffer":       fed.get("input_buffer_counts", {}),
        "age":          _age(datetime.fromisoformat(fed_ts)) if fed_ts != "?" else "?",
    }

    # Watermark
    wm = _s3_get_json(BUCKET_BODY, "feedback/watermark.json")
    result["watermark"] = {
        "last_processed": wm.get("last_processed_timestamp", "?")[:19],
        "count":          wm.get("last_processed_count", "?"),
        "updated_at":     wm.get("updated_at", "?")[:19],
    }

    # Latest body decisions tail
    raw_dec = _s3_get_text(BUCKET_BODY, "federation/body_decisions.jsonl", last_bytes=4096)
    decisions = []
    for line in raw_dec.strip().splitlines():
        try:
            decisions.append(json.loads(line))
        except Exception:
            pass
    result["recent_decisions"] = decisions[-3:] if decisions else []

    return result


def snapshot_world() -> dict:
    """Read WORLD state from s3://elpida-external-interfaces"""
    result = {}

    # D15 broadcasts
    raw = _s3_get_text(BUCKET_WORLD, "d15/broadcasts.jsonl", last_bytes=4096)
    broadcasts = []
    for line in raw.strip().splitlines():
        try:
            broadcasts.append(json.loads(line))
        except Exception:
            pass
    result["d15_broadcasts"] = broadcasts[-2:] if broadcasts else []

    # World kaya cross-layer (field names from actual JSON)
    kaya_objs = _s3_latest_objects(BUCKET_WORLD, "kaya/", n=1)
    if kaya_objs:
        kaya = _s3_get_json(BUCKET_WORLD, kaya_objs[0]["Key"])
        trigger = kaya.get("trigger", {})
        body_kaya = kaya.get("body", {})
        result["kaya_latest"] = {
            "key":         kaya_objs[0]["Key"].split("/")[-1],
            "age":         _age(kaya_objs[0]["LastModified"]),
            "fired_at":    kaya.get("fired_at", "?")[:19],
            "mind_kaya":   trigger.get("mind_kaya_moments", "?"),
            "mind_cycle":  trigger.get("mind_cycle", "?"),
            "mind_rhythm": trigger.get("mind_rhythm", "?"),
            "body_cycle":  body_kaya.get("body_cycle", "?"),
            "watch":       kaya.get("watch", "?"),
        }

    return result


# ── Renderer ──────────────────────────────────────────────────────────────────

def render(mind: dict, body: dict, world: dict):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    W = 70
    sep = "─" * W

    print(f"\n{'═'*W}")
    print(f"  ELPIDA MONITOR  ·  {now}")
    print(f"{'═'*W}")

    # MIND
    print(f"\n  ┌─ MIND  (s3://{BUCKET_MIND})")
    nc = mind.get("last_native_cycle", {})
    if nc:
        ts  = nc.get("timestamp", "?")
        num = nc.get("cycle_number", nc.get("cycle", "?"))
        print(f"  │  Native cycle #{num}  @  {ts}")
        mode = nc.get("mode", nc.get("current_mode", "?"))
        print(f"  │  Mode: {mode}")
    else:
        print("  │  No native cycle data found in tail")

    fm = mind.get("last_feedback_merge", {})
    if fm:
        ts   = fm.get("timestamp", "?")
        kaya = fm.get("kaya_moments_total", "?")
        flt  = fm.get("fault_lines_total", "?")
        print(f"  │  Last FEEDBACK_MERGE  @  {ts}")
        print(f"  │    kaya={kaya}  faults={flt}")

    kernel = mind.get("kernel", {})
    if kernel:
        print(f"  │  kernel: cycle={kernel.get('cycle','?')}  "
              f"mode={kernel.get('mode','?')}  "
              f"breath={kernel.get('breath_count','?')}")

    print(f"  └{sep[2:]}")

    # BODY
    print(f"\n  ┌─ BODY  (HF Space + s3://{BUCKET_BODY})")
    hs = body.get("hf_space", {})
    stage_icon = "✓" if hs.get("stage") == "RUNNING" else "✗"
    print(f"  │  HF Space: {stage_icon} {hs.get('stage','?')}  "
          f"sha={hs.get('sha','?')}  hw={hs.get('hardware','?')}")
    if hs.get("error") and hs["error"] != "none":
        print(f"  │  ERROR: {hs['error']}")
    if "_error" in hs.get("stage",""):
        print(f"  │  ⚠ HF token expired — Space status unknown")

    hb = body.get("body_heartbeat", {})
    fed = body.get("federation", {})
    print(f"  │  HF Space heartbeat ({hb.get('age','?')}):")
    print(f"  │    mind_cache={hb.get('mind_cache_lines','?')}  "
          f"feedback_cache={hb.get('feedback_cache','?')}  "
          f"gov_votes={hb.get('governance_votes','?')}")
    if fed:
        buf = fed.get('buffer',{})
        buf_str = '  '.join(f"{k}:{v}" for k,v in buf.items())
        print(f"  │  Parliament  ({fed.get('age','?')}):")
        print(f"  │    cycle={fed.get('body_cycle','?')}  "
              f"coherence={fed.get('coherence','?')}  "
              f"rhythm={fed.get('rhythm','?')}  "
              f"axiom={fed.get('axiom','?')}")
        print(f"  │    approval={fed.get('approval_rate','?')}  "
              f"watch={fed.get('watch','?')}  "
              f"d15_sent={fed.get('d15_count','?')}")
        if buf_str:
            print(f"  │    buffer: {buf_str}")

    wm = body.get("watermark", {})
    print(f"  │  Watermark: last_processed={wm.get('count','?')} entries  "
          f"@  {wm.get('last_processed','?')}")

    decs = body.get("recent_decisions", [])
    if decs:
        print(f"  │  Recent decisions ({len(decs)}):")
        for d in decs:
            ruling = (d.get("ruling") or d.get("verdict") or d.get("decision") or "")[:60]
            cycle  = d.get("cycle", d.get("parliament_cycle", "?"))
            print(f"  │    [{cycle}] {ruling}")

    print(f"  └{sep[2:]}")

    # WORLD
    print(f"\n  ┌─ WORLD  (s3://{BUCKET_WORLD})")
    kl = world.get("kaya_latest", {})
    if kl:
        print(f"  │  Last CROSS_LAYER_KAYA: {kl.get('fired_at','?')}  ({kl.get('age','?')})")
        print(f"  │    watch={kl.get('watch','?')}  "
              f"mind_cycle={kl.get('mind_cycle','?')}  "
              f"mind_kaya={kl.get('mind_kaya','?')}  "
              f"mind_rhythm={kl.get('mind_rhythm','?')}  "
              f"body_cycle={kl.get('body_cycle','?')}")

    bcs = world.get("d15_broadcasts", [])
    if bcs:
        print(f"  │  D15 broadcasts (last {len(bcs)}):")
        for bc in bcs:
            ts   = (bc.get("timestamp","?") or "?")[:19]
            typ  = bc.get("type", bc.get("broadcast_type","?"))
            msg  = (bc.get("message") or bc.get("content") or bc.get("summary") or "")[:50]
            print(f"  │    [{ts}] {typ}: {msg}")

    print(f"  └{sep[2:]}")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_once():
    print("Fetching MIND (S3)...", end=" ", flush=True)
    mind = snapshot_mind()
    print("BODY (HF+S3)...", end=" ", flush=True)
    body = snapshot_body()
    print("WORLD (S3)...", end=" ", flush=True)
    world = snapshot_world()
    print("done.")
    render(mind, body, world)


def run_loop(interval: int):
    print(f"Starting monitor loop (interval={interval}s). Ctrl+C to stop.")
    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"\n[monitor error] {e}")
        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Elpida dual-layer monitor")
    parser.add_argument("--once", action="store_true", help="Single snapshot then exit")
    parser.add_argument("--interval", type=int, default=60, help="Poll interval in seconds (default 60)")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_loop(args.interval)
