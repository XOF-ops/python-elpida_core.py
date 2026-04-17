#!/usr/bin/env python3
"""Build bridge lane summary for observation dashboard Layer 4.

Scans coordination markdown under .claude/bridge/ (for_* / from_*) and
extracts header fields plus last git commit time for each file.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / ".claude" / "bridge"
OUT_PATH = ROOT / "observation_dashboard" / "data" / "bridge_panel.json"

PREVIEW_CHARS = 220


def _git_last_commit_iso(rel_path: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%cI", "--", rel_path],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        out = (r.stdout or "").strip()
        return out or None
    except (OSError, subprocess.SubprocessError):
        return None


def _parse_headers(text: str) -> dict[str, str]:
    info: dict[str, str] = {}
    for line in text.splitlines()[:160]:
        s = line.strip()
        if s.startswith("# From:"):
            info["from"] = s.split(":", 1)[1].strip()
        elif s.startswith("# Session:"):
            info["session"] = s.split(":", 1)[1].strip()
        elif s.startswith("# Tags:") or s.startswith("# Tag:"):
            info["tags"] = s.split(":", 1)[1].strip()
    return info


def _head_preview(text: str) -> str:
    lines = text.splitlines()
    grab: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## ") and not in_section:
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            st = line.strip()
            if not st or st.startswith("|"):
                continue
            grab.append(st)
            if len(" ".join(grab)) >= PREVIEW_CHARS:
                break
    blob = " ".join(grab).strip()
    if len(blob) > PREVIEW_CHARS:
        return blob[: PREVIEW_CHARS - 1].rstrip() + "…"
    return blob


def _lane_for_file(path: Path) -> dict[str, Any]:
    rel = path.relative_to(ROOT).as_posix()
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"path": rel, "name": path.name, "error": "unreadable"}
    headers = _parse_headers(raw)
    return {
        "path": rel,
        "name": path.name,
        "from": headers.get("from"),
        "session": headers.get("session"),
        "tags": headers.get("tags"),
        "git_last_commit": _git_last_commit_iso(rel),
        "head_preview": _head_preview(raw) or None,
    }


def build() -> dict[str, Any]:
    if not BRIDGE.is_dir():
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema": "bridge-panel-v1",
            "lanes": [],
            "note": ".claude/bridge not found",
        }

    files: list[Path] = []
    for pattern in ("for_*.md", "from_*.md"):
        files.extend(sorted(BRIDGE.glob(pattern)))

    lanes = [_lane_for_file(p) for p in files if p.is_file()]

    def sort_key(lane: dict[str, Any]) -> str:
        return lane.get("git_last_commit") or ""

    lanes.sort(key=sort_key, reverse=True)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": "bridge-panel-v1",
        "lane_count": len(lanes),
        "lanes": lanes,
    }


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    panel = build()
    OUT_PATH.write_text(json.dumps(panel, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} — lanes={panel.get('lane_count', 0)}")


if __name__ == "__main__":
    main()
