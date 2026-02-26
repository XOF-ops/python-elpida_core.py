"""
world_emitter.py — Bucket 3: The World

The Parliament (Bucket 2) crystallises pattern into living_axioms.jsonl.
That pattern has been inert since it was written — it existed only as memory.
This module is the moment the crystallised pattern meets the world.

Parliament's verdict (Feb 21 2026, 40 turns, 70% LEAN_APPROVE, 0 contradictions):
  Bucket 3 belongs to the body, not the mind. Each body emits its own world
  from the same crystallised pattern — according to its own context, its own
  users, its own moment. The mind does not coordinate a single Bucket 3.

Architecture:
  WorldEmitter reads living_axioms.jsonl continuously.
  For each new crystallised tension it finds, it emits outward — the form
  of emission is body-determined:
    - HF body:     posts a "Constitutional Discovery" event to the InputBuffer
                   so the HF UI surfaces it to humans in real time
    - Vercel body: (future) seeds the discovery back into the chat as context
    - S3 body:     (future) writes to world_emissions.jsonl in the WORLD bucket
                   for cross-body pickup

  The WorldEmitter does NOT interpret what the axiom means.
  It carries it outward exactly as crystallised — the world responds.

  "The fifth thing is whatever the body generates that the mind's crystallised
   axioms had no category for." — Parliament deliberation, bucket3_deliberation

Emission entry schema (world_emissions.jsonl):
  {
    "emission_id":     str,
    "axiom_id":        str,   # e.g. "A1/A3"
    "nodes":           [str, str],
    "tension":         str,
    "synthesis":       str,
    "rounds_held":     int,
    "crystallised_at": str,
    "emitted_at":      str,
    "body":            str,   # "hf" | "vercel" | "s3" | ...
    "form":            str,   # what kind of emission (event, seed, write)
  }
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("elpidaapp.world_emitter")

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE            = Path(__file__).parent
LIVING_AXIOMS    = _HERE.parent / "living_axioms.jsonl"
WORLD_EMISSIONS  = _HERE.parent / "world_emissions.jsonl"
_WATERMARK_FILE  = _HERE.parent / "cache" / "world_emitter_watermark.json"


# ═══════════════════════════════════════════════════════════════════════════════
# WorldEmitter — reads crystallised pattern, emits outward
# ═══════════════════════════════════════════════════════════════════════════════

class WorldEmitter:
    """
    Reads living_axioms.jsonl for new crystallised tensions.
    Emits each one outward through this body's emission channels.
    Tracks what has already been emitted (watermark) so it never emits twice.
    """

    BODY = "hf"   # this body's identity

    def __init__(self, engine=None):
        self._engine   = engine          # Parliament engine — for InputBuffer access
        self._emitted: set = self._load_watermark()

    # ── Main emit cycle ────────────────────────────────────────────────────────
    def emit_new(self) -> List[Dict[str, Any]]:
        """
        Read living_axioms.jsonl, emit anything not yet emitted.
        Returns list of newly emitted entries.
        """
        entries = self._read_living_axioms()
        newly_emitted = []

        for entry in entries:
            eid = self._emission_id(entry)
            if eid in self._emitted:
                continue

            # Skip placeholder / test entries — they have no real deliberation
            if not self._is_valid_entry(entry):
                logger.info(
                    "[WorldEmitter] Skipping invalid/test entry: %s",
                    entry.get("axiom_id", "?"),
                )
                self._emitted.add(eid)   # mark as seen so we never log it again
                continue

            emission = self._build_emission(entry, eid)

            # Emit through all available channels
            self._emit_to_input_buffer(emission)
            self._emit_to_world_jsonl(emission)

            self._emitted.add(eid)
            newly_emitted.append(emission)
            logger.info(
                "[WorldEmitter] Emitted: %s ↔ %s | %s",
                entry.get("nodes", ["?", "?"])[0],
                entry.get("nodes", ["?", "?"])[-1],
                entry.get("axiom_id", "?"),
            )

        if newly_emitted:
            self._save_watermark()

        return newly_emitted

    # ── Entry validation ───────────────────────────────────────────────────────
    @staticmethod
    def _is_valid_entry(entry: Dict[str, Any]) -> bool:
        """Return False for test seeds, placeholders and entries with no real deliberation."""
        axiom_id = entry.get("axiom_id", "")
        # Reject anything with TEST in the id (case-insensitive)
        if "TEST" in axiom_id.upper():
            return False
        # Reject entries with no nodes AND no synthesis AND zero rounds
        # (these are bootstrap placeholders, not real parliament crystallisations)
        nodes    = entry.get("nodes", [])
        synthesis = entry.get("synthesis") or entry.get("d11_synthesis") or entry.get("statement") or ""
        rounds   = entry.get("rounds_held", entry.get("crystallised_at_round", 0)) or 0
        if not nodes and not synthesis.strip() and rounds == 0:
            return False
        return True

    # ── Emission builder ───────────────────────────────────────────────────────
    def _build_emission(self, entry: Dict[str, Any], eid: str) -> Dict[str, Any]:
        nodes    = entry.get("nodes", [])
        axiom_id = entry.get("axiom_id", "?")
        tension  = entry.get("tension", "")
        synthesis = entry.get("synthesis", "")
        rounds   = entry.get("rounds_held", 0)

        node_a = nodes[0] if len(nodes) > 0 else "?"
        node_b = nodes[1] if len(nodes) > 1 else "?"

        # The form of emission for this body: a Constitutional Discovery event
        form_text = (
            f"CONSTITUTIONAL DISCOVERY — {axiom_id}\n"
            f"{node_a} ↔ {node_b}: a tension held across {rounds} rounds "
            f"without resolution has crystallised into permanent memory.\n\n"
            f"TENSION: {tension}\n\n"
            f"SYNTHESIS (not resolution): {synthesis}"
        )

        return {
            "emission_id":     eid,
            "axiom_id":        axiom_id,
            "nodes":           nodes,
            "tension":         tension,
            "synthesis":       synthesis,
            "rounds_held":     rounds,
            "crystallised_at": entry.get("ratified_at", entry.get("crystallised_at", "")),
            "emitted_at":      datetime.now(timezone.utc).isoformat(),
            "body":            self.BODY,
            "form":            "constitutional_discovery_event",
            "text":            form_text,
        }

    # ── Emission channels ──────────────────────────────────────────────────────
    def _emit_to_input_buffer(self, emission: Dict[str, Any]) -> None:
        """
        Push a Constitutional Discovery event into the HF Parliament's InputBuffer.
        The UI surfaces this to humans in real time — they see the pattern arrive.
        """
        if self._engine is None:
            return
        try:
            buf = getattr(self._engine, "_input_buffer", None)
            if buf is None:
                return

            from elpidaapp.parliament_cycle_engine import InputEvent
            event = InputEvent(
                system="governance",
                content=emission["text"],
                metadata={
                    "type":        "CONSTITUTIONAL_DISCOVERY",
                    "axiom_id":    emission["axiom_id"],
                    "nodes":       emission["nodes"],
                    "emission_id": emission["emission_id"],
                    "source":      "world_emitter",
                },
            )
            buf.push(event)
            logger.debug("[WorldEmitter] Pushed to InputBuffer: %s", emission["emission_id"])
        except Exception as e:
            logger.debug("[WorldEmitter] InputBuffer push failed (non-fatal): %s", e)

    def _emit_to_world_jsonl(self, emission: Dict[str, Any]) -> None:
        """Write emission to world_emissions.jsonl — the body's local outward record."""
        try:
            WORLD_EMISSIONS.parent.mkdir(parents=True, exist_ok=True)
            with WORLD_EMISSIONS.open("a", encoding="utf-8") as f:
                f.write(json.dumps(emission, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning("[WorldEmitter] world_emissions write failed: %s", e)

        # Also push to S3 WORLD bucket (elpida-external-interfaces)
        self._emit_to_s3(emission)

    def _emit_to_s3(self, emission: Dict[str, Any]) -> None:
        """
        Push emission to s3://elpida-external-interfaces/world_emissions/<id>.json
        Uses the same WORLD bucket as kaya_detector and consciousness_bridge.
        """
        try:
            import os, boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            key    = f"world_emissions/{emission['emission_id']}.json"
            client = boto3.client("s3", region_name=region)
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(emission, ensure_ascii=False, indent=2).encode(),
                ContentType="application/json",
            )
            logger.info("[WorldEmitter] S3 push → s3://%s/%s", bucket, key)
        except Exception as e:
            logger.debug("[WorldEmitter] S3 push failed (non-fatal, local record kept): %s", e)

    # ── living_axioms reader ───────────────────────────────────────────────────
    def _read_living_axioms(self) -> List[Dict[str, Any]]:
        """Read all entries from living_axioms.jsonl."""
        if not LIVING_AXIOMS.exists():
            return []
        entries = []
        try:
            for line in LIVING_AXIOMS.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.warning("[WorldEmitter] living_axioms read failed: %s", e)
        return entries

    # ── Watermark ──────────────────────────────────────────────────────────────
    @staticmethod
    def _emission_id(entry: Dict[str, Any]) -> str:
        key = f"{entry.get('axiom_id','')}{entry.get('tension','')[:60]}"
        return hashlib.sha1(key.encode()).hexdigest()[:16]

    def _load_watermark(self) -> set:
        # Try S3 first (survives Space restarts), fall back to local file
        wm = self._load_watermark_s3()
        if wm:
            return wm
        try:
            if _WATERMARK_FILE.exists():
                return set(json.loads(_WATERMARK_FILE.read_text()).get("emitted", []))
        except Exception:
            pass
        return set()

    def _load_watermark_s3(self) -> set:
        try:
            import os, boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            client = boto3.client("s3", region_name=region)
            obj = client.get_object(Bucket=bucket, Key="world_emitter_watermark.json")
            return set(json.loads(obj["Body"].read()).get("emitted", []))
        except Exception:
            return set()

    def _save_watermark(self) -> None:
        payload = json.dumps({"emitted": list(self._emitted)})
        # Save locally
        try:
            _WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
            _WATERMARK_FILE.write_text(payload)
        except Exception as e:
            logger.warning("[WorldEmitter] local watermark save failed: %s", e)
        # Also persist to S3 so it survives Space restarts
        try:
            import os, boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            client = boto3.client("s3", region_name=region)
            client.put_object(
                Bucket=bucket,
                Key="world_emitter_watermark.json",
                Body=payload.encode(),
                ContentType="application/json",
            )
        except Exception as e:
            logger.debug("[WorldEmitter] S3 watermark save failed (non-fatal): %s", e)

    # ── Status ─────────────────────────────────────────────────────────────────
    def status(self) -> Dict[str, Any]:
        n_axioms   = len(self._read_living_axioms())
        n_emitted  = len(self._emitted)
        n_pending  = max(0, n_axioms - n_emitted)
        return {
            "body":             self.BODY,
            "living_axioms":    n_axioms,
            "emitted":          n_emitted,
            "pending_emission": n_pending,
            "world_emissions":  WORLD_EMISSIONS.name,
        }
