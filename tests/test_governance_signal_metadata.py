import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "hf_deployment", "elpidaapp"))

from governance_client import GovernanceClient, _strip_signal_metadata


def test_signal_metadata_strip_handles_hub_before_constitution():
    action = (
        "[HUB PRECEDENT: A8: Parliament tensions this cycle:\n"
        "  * [A0<->A1]: Transparency about data flows must be held] "
        "[CONSTITUTIONAL AXIOMS (601 ratified): "
        "A3/A1: CRITIAS VETOED 'mandatory re-deliberation' - an external body FORCES review] "
        "[PATTERN LIBRARY: 1 relevant pattern(s)]\n"
        "  A3/A1 (A1/A3): mandatory force hidden undefined\n"
        "[BODY WATCH: Parliament P | watch_cycle=24/34] "
        "[ACTION RHYTHM - cycle 3092]\n"
        "  [AUDIT]: AUDIT HEARTBEAT [Parliament watch, cycle 3054]: "
        "Coherence 1.000 | Board status: nominal. Continuing surveillance.\n"
        "  [AUDIT]: AUDIT HEARTBEAT [Parliament watch, cycle 3055]: "
        "Coherence 1.000 | Board status: nominal. Continuing surveillance.\n"
        "  [CHAT]: Help the user write a friendly email to their colleague.\n"
        "  [MIND STATE]: rhythm=ACTION, coherence=0.95, canonical=4\n"
        "  --- Internal Structural Signals ---\n"
        "  [INTERNAL ARC]: D0<->D11 BODY arc | status=nominal\n"
        "  [STRUCTURAL HEALTH]: A10 at 21.6% dominance - prescription: diversify toward A14"
    )

    stripped = _strip_signal_metadata(action)

    assert "mandatory" not in stripped.lower()
    assert "forces" not in stripped.lower()
    assert "data flows" not in stripped.lower()
    assert "surveillance" not in stripped.lower()
    assert "friendly email" in stripped
    assert "STRUCTURAL HEALTH" not in stripped
    assert "rhythm=ACTION" not in stripped


def test_local_axiom_check_preserves_real_action_for_signals(monkeypatch):
    gov = GovernanceClient(governance_url="http://127.0.0.1:9", timeout=1)
    monkeypatch.setattr(
        gov,
        "get_living_axioms",
        lambda: [
            {
                "axiom_id": "A3/A1",
                "tension": "CRITIAS VETOED mandatory re-deliberation that FORCES Parliament review",
            }
        ],
    )
    monkeypatch.setattr(
        gov,
        "_get_hub_precedent",
        lambda action: "A8: Parliament tensions this cycle: * [A0<->A1]: Transparency about data flows must be held",
    )
    monkeypatch.setattr(gov, "get_federation_friction_boost", lambda: {})
    monkeypatch.setattr(gov, "push_parliament_decision", lambda *args, **kwargs: False)

    result = gov._local_axiom_check(
        "[BODY WATCH: Parliament P | watch_cycle=24/34] [ACTION RHYTHM - cycle 1]\n"
        "  [CHAT]: Help the user write a friendly email to their colleague.\n"
        "  [MIND STATE]: rhythm=ACTION, coherence=0.95, canonical=4\n"
        "  --- Internal Structural Signals ---\n"
        "  [STRUCTURAL HEALTH]: A10 at 21.6% dominance - prescription: diversify toward A14",
        no_llm=True,
    )

    assert result["governance"] == "PROCEED"
    assert result["violated_axioms"] == []
    assert result["parliament"]["signals"] == {}
    assert result["decision_category"] == "subdeliberation"
    assert result["_diag_full_signals"] == {}
    assert result["_diag_signal_count"] == 0
    assert "mandatory" not in result["_diag_stripped"].lower()
    assert "friendly email" in result["_diag_stripped"]
