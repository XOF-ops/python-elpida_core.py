#!/usr/bin/env python3
"""Smoke + behavioural tests for scripts/temporal_rhythm_extractor.py."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import temporal_rhythm_extractor as tre  # noqa: E402


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")


def _write_d15(path: Path, broadcasts: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema": "d15-index-v1", "broadcasts": broadcasts}),
        encoding="utf-8",
    )


class TestNormalization(unittest.TestCase):
    def test_extract_axiom_from_list(self):
        ev = tre._normalize(
            {"timestamp": "2026-04-10T12:00:00Z", "axioms_invoked": ["A1", "A10"]},
            "MIND",
            "fake:L1",
        )
        self.assertEqual(ev["axiom"], "A1")
        self.assertEqual(ev["source_system"], "MIND")
        self.assertEqual(ev["lineage_id"], "fake:L1")

    def test_extract_domain_from_int(self):
        ev = tre._normalize(
            {"timestamp": "2026-04-10T12:00:00Z", "domain_active": 11},
            "MIND",
            "fake:L1",
        )
        self.assertEqual(ev["domain"], "D11")

    def test_missing_timestamp_yields_none(self):
        ev = tre._normalize({"domain": "D0"}, "MIND", "fake:L1")
        self.assertIsNone(ev["timestamp_utc"])

    def test_confidence_clamped_from_score(self):
        ev = tre._normalize(
            {"timestamp": "2026-04-10T12:00:00Z", "score": 9},
            "MIND",
            "fake:L1",
        )
        # score 9 on a 0-10 scale → 0.9
        self.assertAlmostEqual(ev["confidence"], 0.9, places=3)


class TestTriadAttractor(unittest.TestCase):
    def _events(self) -> list[dict]:
        # Periodic triad: D0 → D11 → D16 every 10 minutes, 5 rounds.
        events = []
        t0 = 1_800_000_000  # arbitrary UTC epoch seconds
        for i in range(5):
            base = t0 + i * 600
            events.append(tre._normalize(
                {"timestamp": base, "domain": "D0", "axioms": ["A0"]},
                "MIND", f"mem:L{3*i+1}",
            ))
            events.append(tre._normalize(
                {"timestamp": base + 60, "domain": "D11", "axioms": ["A11"]},
                "MIND", f"mem:L{3*i+2}",
            ))
            events.append(tre._normalize(
                {"timestamp": base + 120, "domain": "D16", "axioms": ["A16"]},
                "MIND", f"mem:L{3*i+3}",
            ))
        return events

    def test_stable_attractor_detected(self):
        triad = tre.triad_analysis(self._events())
        self.assertTrue(triad["stable_attractor"])
        self.assertEqual(triad["domain_counts"]["D0"], 5)
        self.assertEqual(triad["full_triad_chain_lag"]["source_count"], 5)
        self.assertGreaterEqual(
            triad["full_triad_chain_lag"]["stability_score"], 0.99
        )

    def test_no_d16_breaks_attractor(self):
        events = [e for e in self._events() if e["domain"] != "D16"]
        triad = tre.triad_analysis(events)
        self.assertFalse(triad["stable_attractor"])
        self.assertEqual(triad["domain_counts"]["D16"], 0)


class TestEndToEnd(unittest.TestCase):
    def test_end_to_end_writes_three_artifacts_with_audit(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src_mind = tmp_path / "mind.jsonl"
            src_fed = tmp_path / "fed.jsonl"
            src_d15 = tmp_path / "d15_index.json"

            _write_jsonl(src_mind, [
                {"timestamp": "2026-04-10T12:00:00Z", "domain": "D0",
                 "axioms_invoked": ["A0"], "confidence": 0.8},
                {"timestamp": "2026-04-10T12:01:00Z", "domain": "D11",
                 "axioms_invoked": ["A11"]},
                {"timestamp": "2026-04-10T12:02:00Z", "domain": "D16",
                 "axioms_invoked": ["A16"]},
                # Provenance-missing event (no timestamp).
                {"domain": "D0", "axioms": ["A0"]},
            ])
            _write_jsonl(src_fed, [
                {"timestamp": "2026-04-10T12:03:00Z", "domain": "D11"},
            ])
            _write_d15(src_d15, [
                {"broadcast_id": "b1",
                 "timestamp": "2026-04-10T12:04:00Z",
                 "axioms_in_tension": ["A0"],
                 "contributing_domains": ["D0"]},
            ])

            paths = tre.run(
                sources=[(src_mind, "MIND"), (src_fed, "FEDERATION"),
                         (src_d15, "D15")],
                out_dir=tmp_path / "out",
            )
            for p in paths.values():
                self.assertTrue(p.exists(), f"{p} missing")

            rhythm = json.loads(paths["rhythm_model"].read_text())
            self.assertEqual(rhythm["schema"], tre.SCHEMA_VERSION)
            self.assertGreater(rhythm["event_count"], 0)
            self.assertIn("inter_event_intervals", rhythm["features"])
            # Every top-level feature carries source_count / confidence.
            iei = rhythm["features"]["inter_event_intervals"]
            self.assertIn("source_count", iei)
            self.assertIn("confidence", iei)
            self.assertTrue(rhythm["audit"]["all_events_have_lineage"])

            queue = json.loads(paths["governance_queue"].read_text())
            self.assertEqual(
                queue["audit"]["missing_provenance_auto_yellow"], True
            )
            # The event without a timestamp must be flagged Yellow with
            # reason=missing_provenance.
            yellow_missing = [
                i for i in queue["items"]
                if i.get("reason") == "missing_provenance"
            ]
            self.assertGreaterEqual(len(yellow_missing), 1)
            for item in yellow_missing:
                self.assertEqual(item["label"], "Yellow")

            report = json.loads(paths["triad_stability_report"].read_text())
            self.assertTrue(report["audit"]["every_metric_has_source_count"])
            self.assertEqual(report["schema"], tre.SCHEMA_VERSION)


if __name__ == "__main__":
    unittest.main()
