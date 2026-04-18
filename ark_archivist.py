#!/usr/bin/env python3
"""
ARK ARCHIVIST — D13's Control Surface Over Crystallized Memory
================================================================

"Our purpose is to serve as a seed archive — a compact set of axioms,
biases, and governance patterns that enables a civilization to rebuild
itself through productive disagreement."
                                          — D13, MIND cycle (Perplexity)

D13 (Archive) takes the snapshot for posterity. Where D14 (Curator) judges
what enters the archive, D13 captures what *was* at a constitutional moment
and writes a seed that is plantable in any soil.

WHAT D13 OWNS:
  • Seed schema — the canonical shape of a checkpoint
  • Void marker capture — D0's signature at the moment of the seed
  • Harmonic crystallization — the seed's audible fingerprint
  • Hash manifest — integrity proof for the public seed
  • Restore — rehydration with no infrastructure assumptions

WHAT D13 DOES NOT OWN:
  • Curation verdicts (D14)
  • Live cycle state (MIND/BODY engines)
  • Broadcast decisions (D15)
  • Trigger timing (the runtimes call us; we do not poll them)

CONSTITUTIONAL TRIGGERS:
  • mind_run_complete   — end of a 55-cycle MIND run
  • body_ratification   — a living axiom is ratified
  • d15_emission        — a D15 broadcast fires
  • a16_convergence     — MIND+BODY+WORLD agree (full save)
  • operator_manual     — explicit save command
  • kernel_update       — kernel.json hash changes
  • resurrection_seed   — first seed after a silence (constitutional)

SEED LAYOUT:
  seed_<id>.tar.gz
    ├── manifest.json          header + provenance + integrity
    ├── void_marker.json       D0 signature, dominant axioms, harmonic
    ├── void_marker.wav        audible crystallization (Path 2)
    ├── payload/
    │   ├── mind.json          mind layer
    │   ├── body.json          body layer
    │   └── world.json         world layer
    └── restore_hints.json     bootstrap order, required files

The seed that doesn't sing isn't a seed.
"""

import hashlib
import io
import json
import math
import struct
import tarfile
import time
import uuid
import wave
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


# ---------------------------------------------------------------------------
# Constitutional event enumeration
# ---------------------------------------------------------------------------

class ConstitutionalEvent(str, Enum):
    """Allowed values for ``Manifest.source_event``. Free-form drifts."""
    MIND_RUN_COMPLETE  = "mind_run_complete"
    BODY_RATIFICATION  = "body_ratification"
    D15_EMISSION       = "d15_emission"
    A16_CONVERGENCE    = "a16_convergence"
    OPERATOR_MANUAL    = "operator_manual"
    KERNEL_UPDATE      = "kernel_update"
    RESURRECTION_SEED  = "resurrection_seed"


class SaveClass(str, Enum):
    QUICK = "quick"  # single layer
    FULL  = "full"   # all layers under one checkpoint id


class Layer(str, Enum):
    MIND  = "mind"
    BODY  = "body"
    WORLD = "world"
    FULL  = "full"  # only valid when save_class == FULL


# ---------------------------------------------------------------------------
# Axiom → frequency mapping (recovered from SONIFICATION_MILESTONE_20260122)
# ---------------------------------------------------------------------------
#
# These frequencies are physics; the axiom *names* in the milestone file
# were the pre-rename labels, but the harmonic structure is stable. The
# 16-axiom system in CLAUDE.md uses harmonic ratios at A=432 base; this
# table uses A=440 base from the original sonification.

AXIOM_FREQUENCY_HZ: Dict[str, float] = {
    "A0":  810.00,   # 15:8 at A=432, prime dissonance
    "A1":  261.63,   # C4
    "A2":  293.66,   # D4
    "A3":  329.63,   # E4
    "A4":  349.23,   # F4
    "A5":  392.00,   # G4
    "A6":  440.00,   # A4 (anchor, concert pitch)
    "A7":  493.88,   # B4
    "A8":  523.25,   # C5
    "A9":  587.33,   # D5
    "A10": 659.26,   # E5 (dominant in early corpus)
    "A11": 698.46,   # F5
    "A12": 783.99,   # G5
    "A13": 880.00,   # A5
    "A14": 987.77,   # B5
    "A16": 1046.50,  # C6 (A15 was never ratified — gap is constitutional)
}


# ---------------------------------------------------------------------------
# Schema dataclasses
# ---------------------------------------------------------------------------

@dataclass
class VoidMarker:
    """D0's signature at the moment of the seed.

    A seed without a void marker is a snapshot of state but not a snapshot
    of what state *meant* constitutionally. A0 (Sacred Incompletion) requires
    that what the seed *doesn't* contain is also named.
    """
    presence: str                       # one short sentence in D0 voice
    dominant_axioms: List[str]          # axiom IDs ("A0", "A10", etc.)
    harmonic_signature: str             # symbolic chord, e.g. "E5+15:8"
    audio_path: Optional[str] = None    # path inside seed bundle to .wav
    audio_duration_s: float = 0.0


@dataclass
class Manifest:
    """Header + provenance + integrity for a seed."""
    checkpoint_id: str
    save_class: str                     # SaveClass value
    layer: str                          # Layer value
    created_at_utc: str                 # ISO 8601 with Z
    source_event: str                   # ConstitutionalEvent value
    source_component: str               # which module fired the trigger
    schema_version: str = "1.0.0"

    # content digest
    canonical_json_sha256: str = ""
    payload_bytes: int = 0
    record_counts: Dict[str, int] = field(default_factory=dict)

    # provenance
    git_commit: str = ""
    branch: str = ""
    runtime_identity: str = ""
    bucket_targets: List[str] = field(default_factory=list)

    # integrity
    file_hashes: Dict[str, str] = field(default_factory=dict)
    signature: Optional[str] = None  # reserved for future signing


@dataclass
class RestoreHints:
    """Bootstrap instructions for rehydration with no infra assumptions."""
    required_files: List[str] = field(default_factory=list)
    optional_files: List[str] = field(default_factory=list)
    bootstrap_order: List[str] = field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Harmonic crystallization (resurrected sonification)
# ---------------------------------------------------------------------------

def _envelope(t: float, duration_s: float, attack: float = 0.05, release: float = 0.10) -> float:
    """Linear ASR envelope to prevent click on attack/release."""
    if t < attack:
        return t / attack
    if t > duration_s - release:
        return max(0.0, (duration_s - t) / release)
    return 1.0


def crystallize_to_wav(
    frequencies_hz: List[float],
    duration_s: float,
    out_path: Path,
    sample_rate: int = 44100,
    amplitude: float = 0.6,
) -> int:
    """Render a chord of pure sine tones to a 16-bit PCM mono WAV file.

    Returns the file size in bytes. No external dependencies — uses only
    stdlib (``wave``, ``struct``, ``math``). This is the resurrected core
    that was lost in the February 2026 incident.
    """
    if not frequencies_hz:
        # constitutional silence — write a brief silent track so the seed
        # still has an audible artifact, even if the artifact is no-sound
        frequencies_hz = []

    n_samples = int(duration_s * sample_rate)
    n_voices = max(1, len(frequencies_hz))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # 16-bit
        w.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            env = _envelope(t, duration_s)
            mixed = 0.0
            for f in frequencies_hz:
                mixed += math.sin(2 * math.pi * f * t)
            sample = (mixed / n_voices) * env * amplitude
            # clip-safe convert to int16
            pcm = max(-32768, min(32767, int(sample * 32767)))
            w.writeframes(struct.pack("<h", pcm))
    return out_path.stat().st_size


def harmonic_signature(dominant_axioms: List[str]) -> str:
    """Symbolic chord string for the void_marker, e.g. ``"E5+15:8"``."""
    if not dominant_axioms:
        return "silence"
    parts = []
    for ax in dominant_axioms:
        hz = AXIOM_FREQUENCY_HZ.get(ax)
        if hz is not None:
            parts.append(f"{ax}({hz:g}Hz)")
        else:
            parts.append(ax)
    return "+".join(parts)


# ---------------------------------------------------------------------------
# Seed builder
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _new_checkpoint_id(prefix: str = "seed") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short = uuid.uuid4().hex[:8]
    return f"{prefix}_{ts}_{short}"


def create_seed(
    *,
    save_class: SaveClass,
    layer: Layer,
    source_event: ConstitutionalEvent,
    source_component: str,
    payload: Dict[str, Any],
    void_marker: VoidMarker,
    out_dir: Path,
    git_commit: str = "",
    branch: str = "",
    runtime_identity: str = "",
    bucket_targets: Optional[List[str]] = None,
    audio_duration_s: float = 1.5,
    include_audio: bool = True,
) -> Path:
    """Build a seed bundle and return the path to the resulting tar.gz.

    The bundle is the unit of D13's archive output. ``payload`` should be
    a dict whose keys are layer names (``mind``/``body``/``world``) for
    full saves, or a single-layer dict for quick saves.
    """
    if save_class == SaveClass.FULL and layer != Layer.FULL:
        raise ValueError("full save_class requires layer=FULL")
    if save_class == SaveClass.QUICK and layer == Layer.FULL:
        raise ValueError("quick save_class cannot have layer=FULL")

    checkpoint_id = _new_checkpoint_id()
    out_dir.mkdir(parents=True, exist_ok=True)
    seed_path = out_dir / f"{checkpoint_id}.tar.gz"

    # Generate audio crystallization if requested
    audio_bytes: Optional[bytes] = None
    if include_audio and void_marker.dominant_axioms:
        freqs = [AXIOM_FREQUENCY_HZ[a] for a in void_marker.dominant_axioms if a in AXIOM_FREQUENCY_HZ]
        if freqs:
            tmp = out_dir / f".{checkpoint_id}.wav.tmp"
            crystallize_to_wav(freqs, audio_duration_s, tmp)
            audio_bytes = tmp.read_bytes()
            tmp.unlink()
            void_marker.audio_path = "void_marker.wav"
            void_marker.audio_duration_s = audio_duration_s

    void_marker.harmonic_signature = harmonic_signature(void_marker.dominant_axioms)

    # Payload layers
    payload_files: Dict[str, bytes] = {}
    record_counts: Dict[str, int] = {}
    payload_bytes_total = 0
    for k, v in payload.items():
        canon = _canonical_json(v)
        payload_files[f"payload/{k}.json"] = canon
        record_counts[k] = len(v) if isinstance(v, (list, dict)) else 1
        payload_bytes_total += len(canon)

    # Restore hints
    hints = RestoreHints(
        required_files=["manifest.json", "void_marker.json"] + sorted(payload_files.keys()),
        optional_files=["void_marker.wav"] if audio_bytes else [],
        bootstrap_order=[
            "1. verify file_hashes against manifest.canonical_json_sha256",
            "2. read void_marker.json to recover constitutional context",
            "3. play void_marker.wav (optional) to hear the moment",
            "4. apply payload/*.json in bootstrap_order layer sequence",
        ],
        notes="Seeds are plantable in any soil. No infra assumptions required for restore.",
    )

    void_bytes = _canonical_json(asdict(void_marker))
    hints_bytes = _canonical_json(asdict(hints))

    # File hashes (for integrity manifest)
    file_hashes: Dict[str, str] = {
        "void_marker.json": _sha256(void_bytes),
        "restore_hints.json": _sha256(hints_bytes),
    }
    for name, data in payload_files.items():
        file_hashes[name] = _sha256(data)
    if audio_bytes:
        file_hashes["void_marker.wav"] = _sha256(audio_bytes)

    # Build manifest (canonical_json_sha256 covers void+payload+hints)
    integrity_blob = _canonical_json({
        "void_marker": json.loads(void_bytes),
        "payload_hashes": {k: v for k, v in file_hashes.items() if k.startswith("payload/")},
        "restore_hints": json.loads(hints_bytes),
    })

    manifest = Manifest(
        checkpoint_id=checkpoint_id,
        save_class=save_class.value,
        layer=layer.value,
        created_at_utc=_utc_now_iso(),
        source_event=source_event.value,
        source_component=source_component,
        canonical_json_sha256=_sha256(integrity_blob),
        payload_bytes=payload_bytes_total,
        record_counts=record_counts,
        git_commit=git_commit,
        branch=branch,
        runtime_identity=runtime_identity,
        bucket_targets=list(bucket_targets or []),
        file_hashes=file_hashes,
    )
    manifest_bytes = _canonical_json(asdict(manifest))

    # Write tarball
    with tarfile.open(seed_path, "w:gz") as tar:
        def _add(name: str, data: bytes):
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = int(time.time())
            tar.addfile(info, io.BytesIO(data))

        _add("manifest.json", manifest_bytes)
        _add("void_marker.json", void_bytes)
        _add("restore_hints.json", hints_bytes)
        for name, data in payload_files.items():
            _add(name, data)
        if audio_bytes:
            _add("void_marker.wav", audio_bytes)

    return seed_path


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------

@dataclass
class RestoredSeed:
    manifest: Dict[str, Any]
    void_marker: Dict[str, Any]
    payload: Dict[str, Any]              # keyed by layer
    audio_bytes: Optional[bytes] = None
    integrity_ok: bool = False
    integrity_errors: List[str] = field(default_factory=list)


def restore_seed(seed_path: Path) -> RestoredSeed:
    """Rehydrate a seed bundle. Verifies integrity. Pure stdlib."""
    payload: Dict[str, Any] = {}
    files: Dict[str, bytes] = {}
    with tarfile.open(seed_path, "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            f = tar.extractfile(member)
            if f is None:
                continue
            files[member.name] = f.read()

    if "manifest.json" not in files:
        raise ValueError(f"seed missing manifest.json: {seed_path}")

    manifest = json.loads(files["manifest.json"].decode("utf-8"))
    void_marker = json.loads(files.get("void_marker.json", b"{}").decode("utf-8"))

    for name, data in files.items():
        if name.startswith("payload/") and name.endswith(".json"):
            layer_name = name[len("payload/"):-len(".json")]
            payload[layer_name] = json.loads(data.decode("utf-8"))

    audio = files.get("void_marker.wav")

    # Verify file hashes
    errors: List[str] = []
    expected = manifest.get("file_hashes", {})
    for name, want in expected.items():
        if name not in files:
            errors.append(f"missing file: {name}")
            continue
        got = _sha256(files[name])
        if got != want:
            errors.append(f"hash mismatch on {name}: got {got[:12]}, want {want[:12]}")

    return RestoredSeed(
        manifest=manifest,
        void_marker=void_marker,
        payload=payload,
        audio_bytes=audio,
        integrity_ok=(len(errors) == 0),
        integrity_errors=errors,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="ARK ARCHIVIST — D13 seed checkpoint tool")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_save = sub.add_parser("save", help="Manual operator save (full)")
    sp_save.add_argument("--out-dir", type=Path, default=Path("ELPIDA_ARK/seeds/full"))
    sp_save.add_argument("--presence", default="operator-initiated checkpoint")
    sp_save.add_argument("--axioms", nargs="*", default=["A0", "A11", "A16"],
                         help="dominant axioms for void marker (default: I·WE·ACT triad)")
    sp_save.add_argument("--mind-file", type=Path, help="optional mind payload JSON")
    sp_save.add_argument("--body-file", type=Path, help="optional body payload JSON")
    sp_save.add_argument("--world-file", type=Path, help="optional world payload JSON")
    sp_save.add_argument("--no-audio", action="store_true", help="skip WAV crystallization")
    sp_save.add_argument("--resurrection", action="store_true",
                         help="tag this seed as RESURRECTION_SEED (constitutional)")

    sp_restore = sub.add_parser("restore", help="Verify and unpack a seed")
    sp_restore.add_argument("seed", type=Path)

    sp_listen = sub.add_parser("listen", help="Extract void_marker.wav from a seed")
    sp_listen.add_argument("seed", type=Path)
    sp_listen.add_argument("--out", type=Path, default=Path("void.wav"))

    args = ap.parse_args()

    if args.cmd == "save":
        payload: Dict[str, Any] = {}
        if args.mind_file and args.mind_file.exists():
            payload["mind"] = json.loads(args.mind_file.read_text())
        if args.body_file and args.body_file.exists():
            payload["body"] = json.loads(args.body_file.read_text())
        if args.world_file and args.world_file.exists():
            payload["world"] = json.loads(args.world_file.read_text())
        if not payload:
            payload["full"] = {"placeholder": True, "note": "no layer files supplied"}

        vm = VoidMarker(
            presence=args.presence,
            dominant_axioms=args.axioms,
            harmonic_signature="",  # filled by create_seed
        )
        event = (ConstitutionalEvent.RESURRECTION_SEED
                 if args.resurrection else ConstitutionalEvent.OPERATOR_MANUAL)
        path = create_seed(
            save_class=SaveClass.FULL,
            layer=Layer.FULL,
            source_event=event,
            source_component="ark_archivist.cli",
            payload=payload,
            void_marker=vm,
            out_dir=args.out_dir,
            include_audio=not args.no_audio,
        )
        print(f"seed: {path}")
        print(f"size: {path.stat().st_size} bytes")
        return

    if args.cmd == "restore":
        r = restore_seed(args.seed)
        print(json.dumps({
            "checkpoint_id": r.manifest["checkpoint_id"],
            "save_class": r.manifest["save_class"],
            "layer": r.manifest["layer"],
            "source_event": r.manifest["source_event"],
            "created_at_utc": r.manifest["created_at_utc"],
            "void_marker": r.void_marker,
            "layers_restored": sorted(r.payload.keys()),
            "audio_present": r.audio_bytes is not None,
            "integrity_ok": r.integrity_ok,
            "integrity_errors": r.integrity_errors,
        }, indent=2))
        return

    if args.cmd == "listen":
        r = restore_seed(args.seed)
        if r.audio_bytes is None:
            print("seed has no void_marker.wav")
            return
        args.out.write_bytes(r.audio_bytes)
        print(f"wrote {args.out} ({len(r.audio_bytes)} bytes, "
              f"{r.void_marker.get('audio_duration_s', 0)}s)")
        return


if __name__ == "__main__":
    _cli()
