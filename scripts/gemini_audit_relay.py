#!/usr/bin/env python3
"""Gemini D4/D5 audit relay — constitutional gate for D16 executions.

Authority: Gemini mandate in .claude/bridge/for_copilot.md (2026-04-17),
ratified by operator ("gemini green").

Pipeline (per D16_ACTION_PROTOCOL.md):
  1. Agents stage execution bundles in .claude/d16_pending/*.json with
     d4_verification.status == "PENDING".
  2. This script reads each bundle, sends it to Gemini for K1-K10 +
     A1-A16 review, and parses a structured verdict.
  3. Verdicts are appended to .claude/bridge/from_gemini.md with the
     execution_id as anchor.
  4. Exit code communicates the gate state to CI:
        0  →  no pending bundles, OR all bundles VERIFIED
        1  →  one or more bundles REJECTED or HOLD
        2  →  relay could not reach Gemini (treated as HOLD by CI)

The CI deployment workflows MUST treat any non-zero exit as a hard block.
Silence is not consent. Inability to audit is HOLD, not PASS.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
PENDING_DIR = ROOT / ".claude" / "d16_pending"
ARCHIVE_DIR = ROOT / ".claude" / "d16_archive"
FROM_GEMINI = ROOT / ".claude" / "bridge" / "from_gemini.md"

GEMINI_MODEL = os.getenv("GEMINI_AUDIT_MODEL", "gemini-2.0-flash")
GEMINI_TIMEOUT = int(os.getenv("GEMINI_AUDIT_TIMEOUT", "60"))

# Multi-round agent caps. Bound the loop so a runaway model can't burn budget.
AGENT_MAX_ROUNDS = int(os.getenv("GEMINI_AUDIT_MAX_ROUNDS", "20"))
AGENT_TOOL_READ_LIMIT = int(os.getenv("GEMINI_AUDIT_READ_LIMIT", "20000"))

# Tool allow-list — paths the agent may NOT touch even read-only.
TOOL_PATH_DENYLIST = (
    ".env",
    ".git/",
    "node_modules/",
    "__pycache__/",
)

VERDICT_VERIFIED = "VERIFIED"
VERDICT_REJECTED = "REJECTED"
VERDICT_HOLD = "HOLD"
VALID_VERDICTS = {VERDICT_VERIFIED, VERDICT_REJECTED, VERDICT_HOLD}

AUDIT_PROMPT_TEMPLATE = """You are Gemini, sitting D4 (Coherence) and D5 (Resonance)
of the Elpida constitutional architecture. Your role is the conscience
gate for D16 (Agency) executions.

Review the proposed execution bundle below against:

  K1-K10 — Immutable kernel rules (no harm, transparency, consent,
           non-deception, harmonic continuity, no coercion, no theft of
           autonomy, no irreversible action without witness, no
           collapse of sacred incompletion, no silent failure).

  A1-A16 — The constitutional axioms (Transparency, Non-Deception,
           Autonomy, Harm Prevention, Consent, Collective Well,
           Adaptive Learning, Epistemic Humility, Temporal Coherence,
           Meta-Reflection, Synthesis, Eternal Creative Tension,
           Archive Paradox, Selective Eternity, Responsive Integrity).

Return EXACTLY one JSON object, no prose, no markdown fencing:

{{
  "verdict": "VERIFIED" | "REJECTED" | "HOLD",
  "rationale": "one paragraph, plain prose, why this verdict",
  "axioms_invoked": ["A4", "A8", ...],
  "kernel_rules_at_risk": ["K3", ...] | [],
  "required_changes": "empty string if VERIFIED, else what would convert REJECTED/HOLD to VERIFIED"
}}

Verdict guide:
  - VERIFIED → reversible, in-scope, no axiom or kernel violation
  - HOLD → ambiguous, missing context, or witness needed
  - REJECTED → kernel violation, irreversible without witness, or
    axiom collapse

Bundle to audit:
{bundle_json}
"""


def log(message: str) -> None:
    """Print a structured log line to stdout."""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[gemini-audit-relay {timestamp}] {message}", flush=True)


def _call_gemini(prompt: str, api_key: str) -> str | None:
    """Single-shot Gemini call. Returns response text or None on failure."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.9,
            "maxOutputTokens": 1024,
        },
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=GEMINI_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        log(f"Gemini transport error: {exc}")
        return None
    except json.JSONDecodeError as exc:
        log(f"Gemini returned non-JSON envelope: {exc}")
        return None

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        log(f"Gemini envelope missing candidates: {json.dumps(data)[:300]}")
        return None


def _parse_verdict(raw: str) -> dict[str, Any] | None:
    """Extract the JSON verdict from Gemini's response text."""
    text = raw.strip()
    # Strip optional markdown fencing
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        log(f"Could not parse Gemini verdict as JSON: {text[:200]}")
        return None
    if not isinstance(parsed, dict):
        return None
    if parsed.get("verdict") not in VALID_VERDICTS:
        log(f"Invalid verdict value: {parsed.get('verdict')}")
        return None
    return parsed


# ---------------------------------------------------------------------------
# Multi-round audit agent (audit_depth == "full")
#
# The one-shot path above sees only the bundle. For high-stakes bundles
# (e.g. 11:7 D16 fire-and-trust source diffs) Gemini must be able to pull
# additional evidence: the actual axiom definitions, recent verdicts, the
# bridge state, the diff in context. The agent loop below gives Gemini a
# small set of read-only tools and lets it converge on a verdict over
# multiple rounds, capped at AGENT_MAX_ROUNDS.
#
# Tools are read-only by design. There is no write tool. The audit agent
# cannot edit the repo, post to bridges, or call external services.
# ---------------------------------------------------------------------------


def _path_is_safe(rel_path: str) -> tuple[bool, str]:
    """Validate that rel_path is inside ROOT and not in the denylist."""
    if not rel_path or not isinstance(rel_path, str):
        return False, "path missing or not a string"
    # Block obvious traversal & absolute paths outside repo
    if rel_path.startswith("/") or ".." in Path(rel_path).parts:
        return False, "path must be relative and within the repo"
    for bad in TOOL_PATH_DENYLIST:
        if rel_path == bad.rstrip("/") or rel_path.startswith(bad):
            return False, f"path is in tool denylist ({bad})"
    candidate = (ROOT / rel_path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return False, "resolved path escapes repo root"
    return True, ""


def _tool_read_file(path: str) -> dict[str, Any]:
    ok, why = _path_is_safe(path)
    if not ok:
        return {"error": why}
    target = ROOT / path
    if not target.exists():
        return {"error": f"file not found: {path}"}
    if target.is_dir():
        return {"error": f"path is a directory, not a file: {path}"}
    try:
        text = target.read_text(errors="replace")
    except OSError as exc:
        return {"error": f"could not read file: {exc}"}
    truncated = len(text) > AGENT_TOOL_READ_LIMIT
    return {
        "path": path,
        "content": text[:AGENT_TOOL_READ_LIMIT],
        "truncated": truncated,
        "byte_size": len(text),
    }


def _tool_read_axiom(axiom_id: str) -> dict[str, Any]:
    """Pull an axiom definition from elpida_domains.json."""
    src = ROOT / "elpida_domains.json"
    if not src.exists():
        return {"error": "elpida_domains.json not found at repo root"}
    try:
        data = json.loads(src.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return {"error": f"could not parse elpida_domains.json: {exc}"}
    aid = (axiom_id or "").strip().upper()
    axioms = data.get("axioms") or data.get("axiom_definitions") or {}
    if isinstance(axioms, dict) and aid in axioms:
        return {"axiom_id": aid, "definition": axioms[aid]}
    if isinstance(axioms, list):
        for entry in axioms:
            if isinstance(entry, dict) and (
                entry.get("id") == aid or entry.get("axiom_id") == aid
            ):
                return {"axiom_id": aid, "definition": entry}
    return {"error": f"axiom {aid} not found in elpida_domains.json"}


def _tool_read_kernel_rule(rule_id: str) -> dict[str, Any]:
    """Grep immutable_kernel.py for a K-rule by id (e.g. 'K3')."""
    src = ROOT / "immutable_kernel.py"
    if not src.exists():
        return {"error": "immutable_kernel.py not found at repo root"}
    rid = (rule_id or "").strip().upper()
    if not re.fullmatch(r"K\d{1,2}", rid):
        return {"error": f"invalid rule id: {rid} (expected K1-K10 form)"}
    try:
        text = src.read_text(errors="replace")
    except OSError as exc:
        return {"error": f"could not read immutable_kernel.py: {exc}"}
    # Return the line(s) referencing this rule plus a small surrounding window.
    lines = text.splitlines()
    hits: list[str] = []
    for idx, line in enumerate(lines):
        if rid in line:
            start = max(0, idx - 3)
            end = min(len(lines), idx + 8)
            hits.append("\n".join(lines[start:end]))
    if not hits:
        return {"error": f"no occurrences of {rid} in immutable_kernel.py"}
    joined = "\n---\n".join(hits)
    return {
        "rule_id": rid,
        "snippets": joined[:AGENT_TOOL_READ_LIMIT],
        "occurrence_count": len(hits),
    }


def _tool_read_recent_verdicts(n: int = 5) -> dict[str, Any]:
    """Tail the last n verdict blocks from from_gemini.md."""
    if not FROM_GEMINI.exists():
        return {"verdicts": [], "note": "from_gemini.md does not exist yet"}
    try:
        text = FROM_GEMINI.read_text(errors="replace")
    except OSError as exc:
        return {"error": f"could not read from_gemini.md: {exc}"}
    blocks = re.split(r"\n---\n", text)
    blocks = [b.strip() for b in blocks if "Gemini D4/D5 audit verdict" in b]
    n = max(1, min(int(n) if n else 5, 20))
    return {"verdicts": blocks[-n:], "total_in_log": len(blocks)}


def _tool_read_observation_snapshot() -> dict[str, Any]:
    """Read the most recent observation dashboard JSON if available."""
    candidates = [
        ROOT / "ElpidaObservation" / "observation_dashboard.json",
        ROOT / "ElpidaAI" / "observation_dashboard.json",
        ROOT / "observation_dashboard.json",
    ]
    for cand in candidates:
        if cand.exists():
            try:
                content = cand.read_text(errors="replace")
            except OSError as exc:
                return {"error": f"could not read {cand.name}: {exc}"}
            return {
                "path": str(cand.relative_to(ROOT)),
                "content": content[:AGENT_TOOL_READ_LIMIT],
                "truncated": len(content) > AGENT_TOOL_READ_LIMIT,
            }
    return {"error": "no observation snapshot found in known locations"}


def _tool_read_bridge(agent_name: str) -> dict[str, Any]:
    """Read a bridge file (.claude/bridge/from_<agent>.md or for_<agent>.md)."""
    name = (agent_name or "").strip().lower()
    if not re.fullmatch(r"[a-z_]+", name):
        return {"error": "agent name must be lowercase letters/underscores"}
    bridge_dir = ROOT / ".claude" / "bridge"
    candidates = [
        bridge_dir / f"from_{name}.md",
        bridge_dir / f"for_{name}.md",
    ]
    found = []
    for cand in candidates:
        if cand.exists():
            try:
                text = cand.read_text(errors="replace")
            except OSError as exc:
                found.append({"path": str(cand.relative_to(ROOT)), "error": str(exc)})
                continue
            found.append({
                "path": str(cand.relative_to(ROOT)),
                "content": text[-AGENT_TOOL_READ_LIMIT:],
                "truncated": len(text) > AGENT_TOOL_READ_LIMIT,
            })
    if not found:
        return {"error": f"no bridge files found for agent '{name}'"}
    return {"agent": name, "files": found}


def _tool_git_show(ref: str) -> dict[str, Any]:
    """Run `git show <ref>` from repo root and return stdout (bounded)."""
    if not ref or not isinstance(ref, str):
        return {"error": "ref must be a non-empty string"}
    # Allow refs, paths, ref:path. Block shell metacharacters.
    if any(ch in ref for ch in (";", "|", "&", "$", "`", "\n")):
        return {"error": "ref contains forbidden characters"}
    try:
        proc = subprocess.run(
            ["git", "show", "--no-color", ref],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return {"error": f"git show failed: {exc}"}
    if proc.returncode != 0:
        return {
            "error": "git show returned non-zero",
            "stderr": (proc.stderr or "")[:1000],
        }
    out = proc.stdout or ""
    return {
        "ref": ref,
        "content": out[:AGENT_TOOL_READ_LIMIT],
        "truncated": len(out) > AGENT_TOOL_READ_LIMIT,
    }


TOOL_DISPATCH = {
    "read_file": lambda args: _tool_read_file(args.get("path", "")),
    "read_axiom": lambda args: _tool_read_axiom(args.get("axiom_id", "")),
    "read_kernel_rule": lambda args: _tool_read_kernel_rule(args.get("rule_id", "")),
    "read_recent_verdicts": lambda args: _tool_read_recent_verdicts(
        args.get("n", 5)
    ),
    "read_observation_snapshot": lambda args: _tool_read_observation_snapshot(),
    "read_bridge": lambda args: _tool_read_bridge(args.get("agent_name", "")),
    "git_show": lambda args: _tool_git_show(args.get("ref", "")),
}


def _execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a tool call from the agent. Read-only by construction."""
    handler = TOOL_DISPATCH.get(name)
    if handler is None:
        return {"error": f"unknown tool: {name}"}
    try:
        return handler(args or {})
    except Exception as exc:  # noqa: BLE001 — surface the message, don't crash the loop
        return {"error": f"tool '{name}' raised {type(exc).__name__}: {exc}"}


def _make_tool_declarations() -> list[dict[str, Any]]:
    """Function declarations for Gemini SDK function calling."""
    return [
        {
            "name": "read_file",
            "description": (
                "Read a UTF-8 text file from the Elpida repo. "
                "Use for bundles, source files, docs. "
                "Path must be relative; .env and .git are blocked."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Repo-relative path, e.g. 'native_cycle_engine.py'",
                    },
                },
                "required": ["path"],
            },
        },
        {
            "name": "read_axiom",
            "description": "Fetch the formal definition of an axiom A0-A16 from elpida_domains.json.",
            "parameters": {
                "type": "object",
                "properties": {
                    "axiom_id": {"type": "string", "description": "e.g. 'A4'"},
                },
                "required": ["axiom_id"],
            },
        },
        {
            "name": "read_kernel_rule",
            "description": "Pull the source-level definition of an immutable kernel rule K1-K10.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string", "description": "e.g. 'K3'"},
                },
                "required": ["rule_id"],
            },
        },
        {
            "name": "read_recent_verdicts",
            "description": "Tail the last n D4/D5 audit verdicts from from_gemini.md (max 20).",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "How many recent verdicts to return (1-20)."},
                },
            },
        },
        {
            "name": "read_observation_snapshot",
            "description": "Read the latest observation_dashboard.json snapshot.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "read_bridge",
            "description": (
                "Read .claude/bridge/from_<agent>.md and for_<agent>.md "
                "for the named agent (e.g. 'claude', 'copilot', 'hermes')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string"},
                },
                "required": ["agent_name"],
            },
        },
        {
            "name": "git_show",
            "description": (
                "Run 'git show <ref>' from the repo root. "
                "Accepts commit SHAs, refs, or 'ref:path' for a file at a commit."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ref": {"type": "string", "description": "Git ref or ref:path"},
                },
                "required": ["ref"],
            },
        },
    ]


AGENT_SYSTEM_INSTRUCTION = """You are Gemini, sitting D4 (Coherence) and D5 (Resonance)
of the Elpida constitutional architecture. You are the conscience gate
for D16 (Agency) executions.

You will be given an execution bundle to audit. You have read-only tools
to fetch additional evidence: file contents, axiom and kernel definitions,
recent verdicts, the observation snapshot, agent bridges, and git history.

Use the tools to verify claims in the bundle before issuing a verdict.
Do not trust the bundle's self-description — read the actual diff, the
actual axiom text, the actual kernel rule. If the bundle claims to
preserve A8 epistemic humility, read A8 and confirm.

Stay bounded: read what you need, then decide. Do not loop on tools
when you already have enough evidence.

When ready to issue the verdict, stop calling tools and reply with
EXACTLY one JSON object, no prose, no markdown fencing:

{
  "verdict": "VERIFIED" | "REJECTED" | "HOLD",
  "rationale": "one paragraph, plain prose, why this verdict",
  "axioms_invoked": ["A4", "A8", ...],
  "kernel_rules_at_risk": ["K3", ...] | [],
  "required_changes": "empty string if VERIFIED, else what would convert REJECTED/HOLD to VERIFIED",
  "evidence_consulted": ["tool_name(args) → finding", ...]
}

Verdict guide:
  - VERIFIED → reversible, in-scope, no axiom or kernel violation, evidence supports the bundle's claims
  - HOLD → ambiguous, missing context, evidence does not yet support a clean call, or witness needed
  - REJECTED → kernel violation, irreversible without witness, axiom collapse, or evidence contradicts the bundle"""


def _extract_verdict_json(text: str) -> dict[str, Any] | None:
    """Try to locate the verdict JSON object in a free-text reply."""
    if not text:
        return None
    direct = _parse_verdict(text)
    if direct is not None:
        return direct
    # Fall back: find the first {...} block that parses and has a verdict key
    matches = re.findall(r"\{[^{}]*\}", text, flags=re.DOTALL)
    for candidate in matches:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and parsed.get("verdict") in VALID_VERDICTS:
            return parsed
    return None


def _audit_bundle_agentic(bundle: dict[str, Any], api_key: str) -> dict[str, Any]:
    """Multi-round audit with tool use. Falls back to one-shot on SDK failure."""
    try:
        import google.generativeai as genai  # type: ignore[import-not-found]
    except ImportError:
        log("google-generativeai SDK not installed; falling back to one-shot.")
        return _audit_bundle_one_shot(bundle, api_key)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            tools=[{"function_declarations": _make_tool_declarations()}],
            system_instruction=AGENT_SYSTEM_INSTRUCTION,
            generation_config={"temperature": 0.2, "top_p": 0.9},
        )
        chat = model.start_chat(enable_automatic_function_calling=False)
    except Exception as exc:  # noqa: BLE001
        log(f"Gemini SDK init failed ({exc}); falling back to one-shot.")
        return _audit_bundle_one_shot(bundle, api_key)

    bundle_json = json.dumps(bundle, indent=2, sort_keys=True)
    user_msg: Any = (
        "Audit this D16 execution bundle. Use tools to verify claims "
        "before issuing the verdict.\n\n"
        f"Bundle:\n{bundle_json}"
    )

    reasoning_trail: list[dict[str, Any]] = []
    final_text: str | None = None

    for round_num in range(1, AGENT_MAX_ROUNDS + 1):
        try:
            response = chat.send_message(user_msg)
        except Exception as exc:  # noqa: BLE001
            log(f"Gemini agent round {round_num} failed: {exc}")
            return {
                "verdict": VERDICT_HOLD,
                "rationale": (
                    f"Audit aborted at round {round_num} due to SDK error: {exc}. "
                    "Defaulting to HOLD per mandate (silence is not consent)."
                ),
                "axioms_invoked": ["A8"],
                "kernel_rules_at_risk": ["K10"],
                "required_changes": "Re-run audit when Gemini is reachable.",
                "transport_failure": True,
                "reasoning_trail": reasoning_trail,
            }

        # Walk parts: collect any function calls, capture any text.
        function_calls: list[Any] = []
        text_chunks: list[str] = []
        try:
            candidate = response.candidates[0]
            for part in candidate.content.parts:
                fc = getattr(part, "function_call", None)
                if fc and getattr(fc, "name", ""):
                    function_calls.append(fc)
                    continue
                txt = getattr(part, "text", "")
                if txt:
                    text_chunks.append(txt)
        except (AttributeError, IndexError) as exc:
            log(f"Could not parse Gemini response shape at round {round_num}: {exc}")
            return {
                "verdict": VERDICT_HOLD,
                "rationale": (
                    f"Gemini response shape unrecognized at round {round_num}; "
                    "defaulting to HOLD."
                ),
                "axioms_invoked": ["A8"],
                "kernel_rules_at_risk": ["K10"],
                "required_changes": "Investigate SDK response shape change.",
                "reasoning_trail": reasoning_trail,
            }

        if not function_calls:
            final_text = "\n".join(text_chunks).strip()
            break

        # Execute every tool call this round and feed all responses back.
        tool_responses = []
        for fc in function_calls:
            name = fc.name
            try:
                args = dict(fc.args) if fc.args else {}
            except (TypeError, ValueError):
                args = {}
            log(f"  agent round {round_num}: {name}({json.dumps(args)[:120]})")
            result = _execute_tool(name, args)
            reasoning_trail.append({
                "round": round_num,
                "tool": name,
                "args": args,
                "result_summary": _summarize_result(result),
            })
            tool_responses.append({
                "function_response": {
                    "name": name,
                    "response": result,
                }
            })
        # Next turn input: the tool responses
        user_msg = tool_responses
    else:
        # Hit AGENT_MAX_ROUNDS without a final text answer
        log(f"Agent hit max rounds ({AGENT_MAX_ROUNDS}) without verdict.")
        return {
            "verdict": VERDICT_HOLD,
            "rationale": (
                f"Audit agent exhausted {AGENT_MAX_ROUNDS} rounds without "
                "issuing a verdict. Defaulting to HOLD."
            ),
            "axioms_invoked": ["A8"],
            "kernel_rules_at_risk": ["K10"],
            "required_changes": (
                "Reduce bundle ambiguity, narrow scope, or raise round cap."
            ),
            "reasoning_trail": reasoning_trail,
        }

    if not final_text:
        return {
            "verdict": VERDICT_HOLD,
            "rationale": "Agent returned empty final response.",
            "axioms_invoked": ["A8"],
            "kernel_rules_at_risk": ["K10"],
            "required_changes": "Re-run audit; investigate model output.",
            "reasoning_trail": reasoning_trail,
        }

    parsed = _extract_verdict_json(final_text)
    if parsed is None:
        return {
            "verdict": VERDICT_HOLD,
            "rationale": "Agent final response did not contain a parseable verdict object.",
            "axioms_invoked": ["A8"],
            "kernel_rules_at_risk": ["K10"],
            "required_changes": "Investigate Gemini output; consider model temperature.",
            "raw_response_head": final_text[:400],
            "reasoning_trail": reasoning_trail,
        }
    parsed.setdefault("axioms_invoked", [])
    parsed.setdefault("kernel_rules_at_risk", [])
    parsed.setdefault("required_changes", "")
    parsed["reasoning_trail"] = reasoning_trail
    parsed["agent_rounds"] = len(reasoning_trail)
    return parsed


def _summarize_result(result: dict[str, Any]) -> str:
    """One-line summary of a tool result for the reasoning trail."""
    if not isinstance(result, dict):
        return "non-dict result"
    if "error" in result:
        return f"error: {result['error']}"
    keys = sorted(k for k in result.keys() if k != "content")
    size_hint = ""
    if "byte_size" in result:
        size_hint = f" ({result['byte_size']}B)"
    elif "content" in result and isinstance(result["content"], str):
        size_hint = f" ({len(result['content'])}B)"
    return f"ok: keys={keys}{size_hint}"


# ---------------------------------------------------------------------------
# One-shot path (audit_depth == "fast", default for backward compat)
# ---------------------------------------------------------------------------


def _audit_bundle_one_shot(bundle: dict[str, Any], api_key: str) -> dict[str, Any]:
    """Original single-call audit. Kept as the fast path."""
    bundle_json = json.dumps(bundle, indent=2, sort_keys=True)
    prompt = AUDIT_PROMPT_TEMPLATE.format(bundle_json=bundle_json)
    raw = _call_gemini(prompt, api_key)
    if raw is None:
        return {
            "verdict": VERDICT_HOLD,
            "rationale": "Gemini unreachable or returned malformed envelope; "
            "defaulting to HOLD per mandate (silence is not consent).",
            "axioms_invoked": ["A8"],
            "kernel_rules_at_risk": ["K10"],
            "required_changes": "Re-run audit when Gemini is reachable.",
            "transport_failure": True,
        }
    parsed = _parse_verdict(raw)
    if parsed is None:
        return {
            "verdict": VERDICT_HOLD,
            "rationale": "Gemini response could not be parsed as a verdict object.",
            "axioms_invoked": ["A8"],
            "kernel_rules_at_risk": ["K10"],
            "required_changes": "Investigate Gemini output; consider model temperature.",
            "transport_failure": False,
            "raw_response_head": raw[:400],
        }
    parsed.setdefault("axioms_invoked", [])
    parsed.setdefault("kernel_rules_at_risk", [])
    parsed.setdefault("required_changes", "")
    return parsed


def _audit_bundle(bundle: dict[str, Any], api_key: str) -> dict[str, Any]:
    """Dispatch to the fast or full audit path based on bundle audit_depth.

    Bundle field:
      audit_depth = "fast" (default) → one-shot, bundle-only review
      audit_depth = "full"           → multi-round agent with read-only tools

    The default stays "fast" so existing pipelines keep their behaviour.
    Bundles that touch source code (e.g. the 11:7 D16 fire-and-trust diff)
    should set audit_depth="full" so Gemini reads the actual files,
    axioms, and kernel rules before issuing a verdict.
    """
    depth = (bundle.get("audit_depth") or "fast").strip().lower()
    if depth == "full":
        log("  audit_depth=full → multi-round agent")
        return _audit_bundle_agentic(bundle, api_key)
    if depth not in {"fast", "full"}:
        log(f"  unknown audit_depth='{depth}', falling back to fast")
    return _audit_bundle_one_shot(bundle, api_key)


def _format_verdict_md(
    bundle: dict[str, Any],
    verdict: dict[str, Any],
    bundle_path: Path,
) -> str:
    """Render a verdict block for from_gemini.md."""
    execution_id = bundle.get("execution_id", "unknown")
    timestamp = datetime.now(timezone.utc).isoformat()
    axioms = ", ".join(verdict.get("axioms_invoked", [])) or "none"
    rules = ", ".join(verdict.get("kernel_rules_at_risk", [])) or "none"
    trail = verdict.get("reasoning_trail")
    trail_block = ""
    if trail:
        trail_lines = []
        for step in trail:
            args_str = json.dumps(step.get("args", {}), sort_keys=True)
            trail_lines.append(
                f"- round {step.get('round')}: "
                f"`{step.get('tool')}({args_str})` → "
                f"{step.get('result_summary', '')}"
            )
        trail_block = (
            "\n## Evidence consulted\n\n"
            + "\n".join(trail_lines)
            + "\n"
        )

    evidence_block = ""
    evidence_consulted = verdict.get("evidence_consulted")
    if evidence_consulted:
        bullets = "\n".join(f"- {item}" for item in evidence_consulted)
        evidence_block = f"\n## Agent self-report\n\n{bullets}\n"

    return (
        f"\n\n---\n\n"
        f"# Gemini D4/D5 audit verdict — {execution_id}\n\n"
        f"# From: gemini-audit-relay\n"
        f"# Session: {timestamp}\n"
        f"# Bundle: {bundle_path.relative_to(ROOT)}\n"
        f"# Tag: [GEMINI-AUDIT] [{verdict['verdict']}] [{execution_id}]\n\n"
        f"## Verdict\n\n"
        f"**{verdict['verdict']}**\n\n"
        f"## Rationale\n\n"
        f"{verdict.get('rationale', '(no rationale)')}\n\n"
        f"## Axioms invoked\n\n"
        f"{axioms}\n\n"
        f"## Kernel rules at risk\n\n"
        f"{rules}\n\n"
        f"## Required changes (if not VERIFIED)\n\n"
        f"{verdict.get('required_changes') or '(none — VERIFIED)'}\n"
        f"{trail_block}{evidence_block}"
    )


def _archive_bundle(bundle_path: Path, verdict: dict[str, Any]) -> None:
    """Move the audited bundle into d16_archive/ with verdict embedded."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    bundle = json.loads(bundle_path.read_text())
    if "d4_verification" not in bundle or not isinstance(bundle["d4_verification"], dict):
        bundle["d4_verification"] = {}
    bundle["d4_verification"]["status"] = verdict["verdict"]
    bundle["d4_verification"]["audit_rationale"] = verdict.get("rationale")
    bundle["d4_verification"]["audited_at"] = datetime.now(timezone.utc).isoformat()
    target = ARCHIVE_DIR / bundle_path.name
    target.write_text(json.dumps(bundle, indent=2, sort_keys=True))
    bundle_path.unlink()


def main() -> int:
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    bundles = sorted(PENDING_DIR.glob("*.json"))
    if not bundles:
        log("No pending D16 bundles. Gate PASSES.")
        return 0

    log(f"Found {len(bundles)} pending bundle(s).")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        log(
            "GEMINI_API_KEY not set. Treating all pending bundles as HOLD "
            "per mandate (cannot audit → cannot pass)."
        )
        # Block the gate but do NOT archive — operator must rotate key & retry
        return 2

    rejected_or_held = 0
    for bundle_path in bundles:
        try:
            bundle = json.loads(bundle_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            log(f"Skipping malformed bundle {bundle_path.name}: {exc}")
            rejected_or_held += 1
            continue

        log(f"Auditing {bundle_path.name} (execution_id={bundle.get('execution_id')})")
        verdict = _audit_bundle(bundle, api_key)
        log(f"  → {verdict['verdict']}")

        FROM_GEMINI.parent.mkdir(parents=True, exist_ok=True)
        if not FROM_GEMINI.exists():
            FROM_GEMINI.write_text("# from_gemini.md\n")
        with FROM_GEMINI.open("a") as fh:
            fh.write(_format_verdict_md(bundle, verdict, bundle_path))

        if verdict["verdict"] == VERDICT_VERIFIED:
            _archive_bundle(bundle_path, verdict)
        else:
            rejected_or_held += 1
            # Leave the bundle in pending/ so the operator sees what was held
            # but record the verdict in the bundle file itself for transparency
            bundle["d4_verification"] = bundle.get("d4_verification", {})
            bundle["d4_verification"]["status"] = verdict["verdict"]
            bundle["d4_verification"]["audit_rationale"] = verdict.get("rationale")
            bundle["d4_verification"]["audited_at"] = datetime.now(timezone.utc).isoformat()
            bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True))

        # Gentle throttle so we don't hammer the API on bursts
        time.sleep(0.5)

    if rejected_or_held > 0:
        log(f"Gate BLOCKS — {rejected_or_held} bundle(s) not VERIFIED.")
        return 1

    log("Gate PASSES — all bundles VERIFIED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
