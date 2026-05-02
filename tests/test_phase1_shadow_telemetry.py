import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "hf_deployment", "elpidaapp"))

from governance_client import GovernanceClient
from parliament_cycle_engine import (
    AUDIT_PRESCRIPTION_COOLDOWN,
    ParliamentCycleEngine,
)


def _engine(cycle=100):
    engine = ParliamentCycleEngine.__new__(ParliamentCycleEngine)
    engine.cycle_count = cycle
    engine._audit_prescription = None
    engine._audit_prescription_cycle = 0
    return engine


def _result(governance="REVIEW", approval=0.2):
    return {"governance": governance, "parliament": {"approval_rate": approval}}


def test_shadow_scores_normalize_a14_rhythm_coverage_without_content():
    engine = _engine()

    shadow = engine._compute_phase1_shadow_axiom(
        rhythm="ANALYSIS",
        active_domains=[4, 5, 6, 9, 13, 14],
        result=_result(),
        action_text="A routine audit asks whether the system should compare tensions.",
    )

    scores = shadow["extended_scores"]
    assert scores["A14"] == 0.25
    assert scores["A13"] == 0.333
    assert scores["A16"] == 0.4
    assert shadow["extended_winner"] == "A16"
    assert shadow["content_corroboration"] == {}


def test_shadow_a14_requires_content_corroboration_to_win_analysis_cycle():
    engine = _engine()

    shadow = engine._compute_phase1_shadow_axiom(
        rhythm="ANALYSIS",
        active_domains=[4, 5, 6, 9, 13, 14],
        result=_result(),
        action_text=(
            "I am selective eternity. Memory is not preservation of everything; "
            "the system must stop hoarding and select what remains."
        ),
    )

    assert shadow["extended_winner"] == "A14"
    assert shadow["extended_scores"]["A14"] == 0.7
    assert "A14" in shadow["content_corroboration"]
    assert "selective eternity" in shadow["content_corroboration"]["A14"]


def test_shadow_p5_prescription_bonus_is_age_gated():
    engine = _engine(cycle=100)
    engine._audit_prescription = {"target_axiom": "A14"}
    engine._audit_prescription_cycle = 100 - AUDIT_PRESCRIPTION_COOLDOWN - 1

    stale = engine._compute_phase1_shadow_axiom(
        rhythm="CONTEMPLATION",
        active_domains=[1, 2, 3, 6, 8, 14],
        result=_result(governance="HALT", approval=0.0),
    )

    assert stale["prescription_bonus_active"] is False
    assert stale["extended_scores"]["A14"] == 0.25

    engine._audit_prescription_cycle = 100 - AUDIT_PRESCRIPTION_COOLDOWN
    active = engine._compute_phase1_shadow_axiom(
        rhythm="CONTEMPLATION",
        active_domains=[1, 2, 3, 6, 8, 14],
        result=_result(governance="HALT", approval=0.0),
    )

    assert active["prescription_bonus_active"] is True
    assert active["extended_scores"]["A14"] == 0.55


def test_push_parliament_decision_persists_phase1_shadow_fields(monkeypatch):
    pushed = {}

    class FakeBridge:
        def push_body_decision(self, exchange):
            pushed.update(exchange)
            return True

    gov = GovernanceClient(governance_url="http://127.0.0.1:9", timeout=1)
    monkeypatch.setattr(gov, "_get_s3_bridge", lambda: FakeBridge())

    result = {
        "governance": "REVIEW",
        "reasoning": "phase telemetry export test",
        "parliament": {"approval_rate": 0.2, "veto_exercised": False},
        "phase1_shadow_enabled": True,
        "phase1_shadow_rhythm": "ANALYSIS",
        "phase1_shadow_active_axioms": ["A13", "A14"],
        "phase1_shadow_extended_winner": "A14",
        "phase1_shadow_extended_scores": {"A14": 0.7},
        "phase1_shadow_extended_raw_scores": {"A14": 1.45},
        "phase1_shadow_score_components": {"A14": {"content_bonus": 0.45}},
        "phase1_shadow_rhythm_coverage": {"A14": 4},
        "phase1_shadow_content_corroboration": {"A14": ["selective eternity"]},
        "phase1_shadow_prescription_target": "A14",
        "phase1_shadow_prescription_age_cycles": 3,
        "phase1_shadow_prescription_bonus_active": True,
        "phase1_shadow_score_basis": "test basis",
    }

    assert gov.push_parliament_decision("test action", result, body_cycle=42) is True
    assert pushed["source"] == "BODY"
    assert pushed["decision_category"] == "primary_body_cycle"
    assert pushed["body_cycle"] == 42
    assert pushed["phase1_shadow_extended_winner"] == "A14"
    assert pushed["phase1_shadow_content_corroboration"] == {"A14": ["selective eternity"]}
    assert pushed["phase1_shadow_prescription_bonus_active"] is True


def test_push_parliament_decision_preserves_hard_block_verdict(monkeypatch):
    pushed = {}

    class FakeBridge:
        def push_body_decision(self, exchange):
            pushed.update(exchange)
            return True

    gov = GovernanceClient(governance_url="http://127.0.0.1:9", timeout=1)
    monkeypatch.setattr(gov, "_get_s3_bridge", lambda: FakeBridge())

    result = {
        "governance": "HARD_BLOCK",
        "reasoning": "kernel stopped the action",
        "parliament": {},
        "phase1_shadow_enabled": True,
        "phase1_shadow_extended_winner": "A16",
        "phase1_shadow_extended_scores": {"A16": 0.4},
    }

    assert gov.push_parliament_decision("blocked action", result, body_cycle=43) is True
    assert pushed["verdict"] == "HARD_BLOCK"
    assert pushed["phase1_shadow_extended_winner"] == "A16"
