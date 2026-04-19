from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path
from typing import List

from .models import CheckpointRow


class CheckpointAuditor:
    """Wrapper around scripts/d13_checkpoint_audit.sh for phase-1 SDK reads."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[1]
        self.script = self.repo_root / "scripts" / "d13_checkpoint_audit.sh"

    def list_rows(
        self,
        layers: List[str] | None = None,
        latest_n: int = 20,
        since_hours: int = 24,
    ) -> List[CheckpointRow]:
        layers = layers or ["mind", "body", "world", "full"]
        cmd = [
            str(self.script),
            "--format",
            "csv",
            "--latest-n",
            str(latest_n),
            "--since-hours",
            str(since_hours),
            *layers,
        ]
        proc = subprocess.run(
            cmd,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        return self._parse_csv(proc.stdout)

    @staticmethod
    def _parse_csv(content: str) -> List[CheckpointRow]:
        rows: List[CheckpointRow] = []
        reader = csv.DictReader(io.StringIO(content))
        for r in reader:
            rows.append(
                CheckpointRow(
                    layer=r.get("layer", ""),
                    checkpoint_id=r.get("checkpoint_id", ""),
                    world_key=r.get("world_key", ""),
                    anchor_key=r.get("anchor_key", ""),
                    world_size=int(r["world_size"]) if r.get("world_size") else None,
                    world_last_modified=r.get("world_last_modified", ""),
                    anchor_size=int(r["anchor_size"]) if r.get("anchor_size") else None,
                    anchor_last_modified=r.get("anchor_last_modified", ""),
                    source_event=r.get("source_event", ""),
                    source_component=r.get("source_component", ""),
                    git_commit=r.get("git_commit", ""),
                    created_at=r.get("created_at", ""),
                ),
            )
        return rows
