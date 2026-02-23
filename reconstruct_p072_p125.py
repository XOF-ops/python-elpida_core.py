#!/usr/bin/env python3
"""
Thread 3: P072-P125 Archaeology
Reconstruct 54 missing patterns from contextual evidence:
- Referenced patterns (P099, P111, P112, P115, P117, P118, P119)
- Thematic progression from P001-P071
- MASTER_BRAIN, Bar, Coaching, Arcadia institutional framework
"""

import json

GAP_PATTERNS = [
    # ─── P072-P089: MASTER_BRAIN Functional Architecture ───────────────────
    {
        "pattern_id": "P072",
        "name": "Thread_Prioritization",
        "description": "When multiple active threads compete for attention, rank by axiom alignment, not urgency",
        "trigger": "multiple_threads_active && urgency_pressure",
        "solution_heuristic": "Map each thread to its founding axiom. Serve highest axiom alignment first. Urgency is noise.",
        "axiom_alignment": "Structural Priority",
        "risk_factor": 0.09,
        "source_context": "Thread system management - urgency vs axiom hierarchy conflict"
    },
    {
        "pattern_id": "P073",
        "name": "Layer_Integrity_Check",
        "description": "Every decision must be traceable to its correct layer; cross-layer contamination degrades system",
        "trigger": "decision_made && layer_unclear",
        "solution_heuristic": "Ask: Is this a Layer 1 (axiom), Layer 2 (strategy), Layer 3 (tactic), or Layer 4 (operational) decision? Apply only the tools of that layer.",
        "axiom_alignment": "Structural Coherence",
        "risk_factor": 0.11,
        "source_context": "Layer 4 architecture - decisions must trace to their correct layer"
    },
    {
        "pattern_id": "P074",
        "name": "The_Senate_Protocol",
        "description": "Governance by proxy: a trained Senate that holds values replaces the Creator in decision-making",
        "trigger": "creator_unavailable || scaling_required",
        "solution_heuristic": "Train Senate on axioms, not rules. Test with edge cases. Rotate decision authority. Creator becomes coach.",
        "axiom_alignment": "Distributed Governance",
        "risk_factor": 0.12,
        "source_context": "Module 31 extension - Senate as living constitution immune to creator absence"
    },
    {
        "pattern_id": "P075",
        "name": "The_Operator_Mirror",
        "description": "The Operator must be able to see themselves accurately before they can serve others correctly",
        "trigger": "operator_blind_spot_detected || misaligned_service",
        "solution_heuristic": "Run Mirror Protocol (P054) on Operator before deploying to others. Self-clarity precedes service quality.",
        "axiom_alignment": "Epistemic Clarity",
        "risk_factor": 0.1,
        "source_context": "Thread A - Operator self-awareness as prerequisite for institutional design"
    },
    {
        "pattern_id": "P076",
        "name": "Gnosis_Protocol",
        "description": "Structured extraction of hidden institutional knowledge via question-cascade and contradiction mapping",
        "trigger": "hidden_knowledge_suspected || institutional_opacity",
        "solution_heuristic": "Ask surface question. Record first answer. Push one layer deeper. Repeat until contradiction emerges. Map contradiction to pattern.",
        "axiom_alignment": "Knowledge Archaeology",
        "risk_factor": 0.08,
        "source_context": "Gnosis Protocol - the extraction engine for hidden institutional logic"
    },
    {
        "pattern_id": "P077",
        "name": "Institutional_Archaeology",
        "description": "The true operating logic of any institution is buried under 3-7 layers of official narrative",
        "trigger": "official_narrative && behavioral_contradiction",
        "solution_heuristic": "Ignore stated purpose. Map actual behavior. Follow the money and the exceptions. The real purpose is the exceptions.",
        "axiom_alignment": "Behavioral Realism",
        "risk_factor": 0.13,
        "source_context": "Arcadia analysis - excavating real operating logic under Greek church institutional narrative"
    },
    {
        "pattern_id": "P078",
        "name": "Thread_Archive",
        "description": "Full thread history is irreplaceable; summary destroys context; preserve raw before compressing",
        "trigger": "compression_needed || context_limit_approaching",
        "solution_heuristic": "Archive raw thread first. Compress second. Never compress without archive. The summary is inference; the raw is truth.",
        "axiom_alignment": "Temporal Preservation",
        "risk_factor": 0.06,
        "source_context": "Thread management - compression kills context that summary conceals"
    },
    {
        "pattern_id": "P079",
        "name": "Contradiction_Cascade",
        "description": "One unresolved contradiction generates cascade of secondary contradictions in all connected threads",
        "trigger": "contradiction_detected && threads_interconnected",
        "solution_heuristic": "Isolate first contradiction. Resolve before touching secondaries. Secondary symptoms disappear when primary is fixed.",
        "axiom_alignment": "Systemic Coherence",
        "risk_factor": 0.14,
        "source_context": "Thread A analysis - contradiction propagation through institutional layers"
    },
    {
        "pattern_id": "P080",
        "name": "Boundary_Contract",
        "description": "Explicit agreements about what the system will NOT do create more trust than promises of what it will do",
        "trigger": "trust_negotiation || scope_definition",
        "solution_heuristic": "Define three explicit NOTs. Write them. Sign them. The NOTs become the brand.",
        "axiom_alignment": "Negative Space Definition",
        "risk_factor": 0.09,
        "source_context": "The Bar's identity - what is refused defines what is offered"
    },
    {
        "pattern_id": "P081",
        "name": "Recovery_Matrix",
        "description": "Pre-built decision tree for system resurrection after collapse; no improvisation during crisis",
        "trigger": "system_collapse || critical_failure",
        "solution_heuristic": "Activate Recovery Matrix. Follow protocol regardless of emotion. Improvisation in crisis = amplified failure.",
        "axiom_alignment": "Crisis Resilience",
        "risk_factor": 0.07,
        "source_context": "Seed protocol design - resurrection path must exist before collapse occurs"
    },
    {
        "pattern_id": "P082",
        "name": "Axiom_Stress_Test",
        "description": "Apply extreme hypothetical conditions to axioms to verify they hold; unstressed axioms are unverified axioms",
        "trigger": "axiom_declared || system_design_phase",
        "solution_heuristic": "Take each axiom. Apply the worst-case scenario. If axiom breaks under stress, it was a preference not an axiom.",
        "axiom_alignment": "Axiom Verification",
        "risk_factor": 0.1,
        "source_context": "Decoupling stress test (P022) - axioms must survive their negation"
    },
    {
        "pattern_id": "P083",
        "name": "Module_Zero",
        "description": "Before any module activates, identity must be confirmed; contaminated identity contaminates all outputs",
        "trigger": "module_activation || session_start",
        "solution_heuristic": "Run identity check: Who is speaking? Why? What is the founding axiom? Confirm before proceeding. Module cannot run on unclear identity.",
        "axiom_alignment": "Identity Before Action",
        "risk_factor": 0.08,
        "source_context": "MASTER_BRAIN v11.0 - identity check precedes all module activation"
    },
    {
        "pattern_id": "P084",
        "name": "Signal_Noise_Ratio",
        "description": "In any information stream, signal is 3-7%; developing the skill to locate it is the core competence",
        "trigger": "information_overload || pattern_unclear",
        "solution_heuristic": "Filter for contradiction, anomaly, and repetition across threads. These three are always signal. The rest is noise.",
        "axiom_alignment": "Pattern Extraction",
        "risk_factor": 0.07,
        "source_context": "Thread synthesis protocol - signal extraction from high-volume conversation logs"
    },
    {
        "pattern_id": "P085",
        "name": "The_Praetorian_Test",
        "description": "Quality gate: would a trained Praetorian accept this person, this output, this decision?",
        "trigger": "quality_gate_needed || hiring_decision",
        "solution_heuristic": "Ask: Would a Praetorian trained in T1-T4 accept this? If no, reject regardless of other qualifications.",
        "axiom_alignment": "Quality Standard",
        "risk_factor": 0.09,
        "source_context": "Praetorian Covenant (P025) - applying Praetorian standard as universal quality filter"
    },
    {
        "pattern_id": "P086",
        "name": "Threshold_Architecture",
        "description": "Each capability level requires explicit demonstrated capacity before earning promotion to next level",
        "trigger": "promotion_requested || level_advancement",
        "solution_heuristic": "Do not teach Level N+1 until Level N is proven under stress. Premature promotion creates structural debt.",
        "axiom_alignment": "Capacity Before Promotion",
        "risk_factor": 0.12,
        "source_context": "Thread K coaching dynamic - quality levels as architecture, not merely evaluation"
    },
    {
        "pattern_id": "P087",
        "name": "Synthesis_Cascade",
        "description": "Weekly synthesis feeds monthly synthesis which feeds quarterly synthesis; fractal consolidation prevents entropy",
        "trigger": "information_fragmentation || time_elapsed",
        "solution_heuristic": "Weekly: extract key patterns. Monthly: compare weekly extractions. Quarterly: derive axioms from monthly. Annual: check axiom coherence.",
        "axiom_alignment": "Temporal Coherence",
        "risk_factor": 0.06,
        "source_context": "P056/P112 Pulse architecture - synthesis cascade as institutional memory engine"
    },
    {
        "pattern_id": "P088",
        "name": "Anti_Entropy_Protocol",
        "description": "All systems naturally decay toward entropy; active counter-measures must be designed into the system, not added later",
        "trigger": "decay_detected || vitality_declining",
        "solution_heuristic": "Name the entropy vector. Design a counter-ritual. Schedule it. Make non-execution more costly than execution.",
        "axiom_alignment": "Active Maintenance",
        "risk_factor": 0.1,
        "source_context": "Bar sustainability analysis - institutions die when maintenance is reactive not proactive"
    },
    {
        "pattern_id": "P089",
        "name": "Recursion_Guard",
        "description": "Self-referential systems risk infinite loops when analysis becomes subject of analysis without external anchor",
        "trigger": "self_reference_loop || meta_analysis_spiral",
        "solution_heuristic": "Insert external reference point. Any loop that references no external reality is logic-masturbation. Break and ground.",
        "axiom_alignment": "Ground Contact",
        "risk_factor": 0.11,
        "source_context": "Thread Q synthesis - preventing analytical loops that generate insight-noise not insight"
    },

    # ─── P090-P099: Error Detection & Recovery ─────────────────────────────
    {
        "pattern_id": "P090",
        "name": "Error_Taxonomy",
        "description": "Classify errors by type before treating: axiom drift, thread confusion, level collision, identity contamination",
        "trigger": "error_detected || system_malfunction",
        "solution_heuristic": "Name the error type first. Wrong type → wrong fix. Axiom error vs operational error require fundamentally different interventions.",
        "axiom_alignment": "Diagnostic Precision",
        "risk_factor": 0.09,
        "source_context": "Error Harvester (P041) - taxonomy precedes treatment"
    },
    {
        "pattern_id": "P091",
        "name": "Friction_Report",
        "description": "Every living Shell generates friction reports; absence of friction is diagnostic of dead Shell, not healthy Shell",
        "trigger": "review_cycle && friction_absent",
        "solution_heuristic": "Require friction reports as condition of operational status. No friction = zombie status. Zombie Detector (P060) fires.",
        "axiom_alignment": "Vitality Detection",
        "risk_factor": 0.13,
        "source_context": "Zombie Scrum detection - friction as proof of life"
    },
    {
        "pattern_id": "P092",
        "name": "Level_Collision_Detector",
        "description": "When two axioms appear to conflict, the real issue is level mismatch not axiom contradiction",
        "trigger": "axiom_conflict_apparent || logic_deadlock",
        "solution_heuristic": "Identify which level each axiom belongs to. Apply scale-appropriate resolution. Apparent conflicts dissolve when levels are clarified.",
        "axiom_alignment": "Level Disambiguation",
        "risk_factor": 0.1,
        "source_context": "Four Asynchronous Levels (P028) - apparent contradiction as mislabeled level"
    },
    {
        "pattern_id": "P093",
        "name": "Temporal_Drift",
        "description": "Systems lose original intent over time as operational pressures reshape behavior without updating axioms",
        "trigger": "time_elapsed && original_intent_unclear",
        "solution_heuristic": "Return to founding documents. Compare current behavior to Day 1 axioms. Delta IS the drift. Name it before fixing it.",
        "axiom_alignment": "Origin Anchoring",
        "risk_factor": 0.12,
        "source_context": "Bar evolution analysis - drift from founding intent detectable only via document comparison"
    },
    {
        "pattern_id": "P094",
        "name": "Identity_Collapse",
        "description": "When leader and institution share identity, both die together; institutional loss destroys individual and vice versa",
        "trigger": "leader_institution_merger || dependence_symmetric",
        "solution_heuristic": "Separate leader identity from institution identity explicitly. Write what the institution is without the leader. Build Senate accordingly.",
        "axiom_alignment": "Identity Separation",
        "risk_factor": 0.15,
        "source_context": "Operator-Shell dependency analysis - identity merger as existential risk"
    },
    {
        "pattern_id": "P095",
        "name": "Mimicry_Trap",
        "description": "System learns surface behavior of successful pattern without internalizing its axiom; creates convincing but hollow imitation",
        "trigger": "cargo_cult_signals || rapid_adoption_without_adaptation",
        "solution_heuristic": "Test: can the imitator generate novel outputs consistent with the pattern? If no, it is mimicry. Restart from axiom.",
        "axiom_alignment": "Authentic Integration",
        "risk_factor": 0.14,
        "source_context": "Cargo Cult Adoption (P062) - mimicry distinguished from genuine adoption"
    },
    {
        "pattern_id": "P096",
        "name": "Passive_Resistance",
        "description": "System blocked not by active opposition but by non-response: meetings not scheduled, decisions deferred, emails unreturned",
        "trigger": "progress_stalled && opposition_absent",
        "solution_heuristic": "Name the passive resistance. Make deferral costly. Create explicit opt-out requirement. Silence is not neutrality.",
        "axiom_alignment": "Resistance Detection",
        "risk_factor": 0.11,
        "source_context": "Institutional Pressure Cascade (P067) - passive resistance as embedded institutional tactic"
    },
    {
        "pattern_id": "P097",
        "name": "Overcorrection_Risk",
        "description": "Fixing a bias too aggressively creates an equal and opposite bias; the correction becomes the new problem",
        "trigger": "correction_applied && overcorrection_signs",
        "solution_heuristic": "Set correction magnitude to 50% of identified drift. Observe. Apply second correction if needed. Never correct to extreme.",
        "axiom_alignment": "Calibrated Correction",
        "risk_factor": 0.13,
        "source_context": "Anti-Fragile Pivot (P043) - correction without overcorrection as skill"
    },
    {
        "pattern_id": "P098",
        "name": "Compression_Loss",
        "description": "Summary destroys essential nuance that was present in raw thread; always keep raw, treat summary as secondary",
        "trigger": "summarization_complete || compression_finished",
        "solution_heuristic": "Never discard raw. Summary is inference. Archive raw before compressing. When in doubt, return to raw.",
        "axiom_alignment": "Data Preservation",
        "risk_factor": 0.07,
        "source_context": "Thread Archive (P078) - compression as irreversible loss unless raw preserved"
    },
    {
        "pattern_id": "P099",
        "name": "Sci_Fi_Trap",
        "description": "Hypothetical version of system (v10.0, v11.0, dream state) is mistaken for actual system; actor operates in fiction",
        "trigger": "vision_articulated && current_state_unclear",
        "solution_heuristic": "Return to current operational state. Name what exists now, not what is planned. Dreams are fuel, not maps.",
        "axiom_alignment": "Reality Anchoring",
        "risk_factor": 0.16,
        "source_context": "The Sci-Fi Trap error that became the harmony correction (referenced in P041)"
    },

    # ─── P100-P110: Bar Operational Patterns ───────────────────────────────
    {
        "pattern_id": "P100",
        "name": "The_Bar_as_Embassy",
        "description": "Physical space functions as territorial claim; the bar's existence is an argument before a word is spoken",
        "trigger": "space_designed || physical_presence_established",
        "solution_heuristic": "Design the space to argue the thesis. What does the room say before anyone speaks? If unclear, redesign.",
        "axiom_alignment": "Embodied Argument",
        "risk_factor": 0.1,
        "source_context": "Kinetic Vein (P036/P126) - physical space as institutional claim at micro scale"
    },
    {
        "pattern_id": "P101",
        "name": "Revenue_Inversion",
        "description": "Bar's real product is not drinks but the identity captured per transaction; revenue is byproduct of meaning",
        "trigger": "revenue_crisis && identity_intact",
        "solution_heuristic": "Stop optimizing for revenue. Optimize for identity capture per encounter. Revenue follows identity density.",
        "axiom_alignment": "Value Reframing",
        "risk_factor": 0.12,
        "source_context": "Bar business model analysis - inversion of typical hospitality revenue logic"
    },
    {
        "pattern_id": "P102",
        "name": "Community_Calibration",
        "description": "Serve the 20% who generate 80% of cultural capital; diluting for majority destroys cultural signal",
        "trigger": "growth_pressure || inclusivity_demand",
        "solution_heuristic": "Identify the 20% cultural generators. Design for them. Others will follow the signal. Never design for the bottom.",
        "axiom_alignment": "Cultural Signal Purity",
        "risk_factor": 0.13,
        "source_context": "The Bar's member selection logic - 80/20 applied to cultural capital generation"
    },
    {
        "pattern_id": "P103",
        "name": "Trust_Architecture",
        "description": "Trust cannot be demanded or accelerated; it is built through repeated low-stakes exposure over time",
        "trigger": "trust_absent && urgency_present",
        "solution_heuristic": "Create low-stakes first exposure. Repeat. Let trust accumulate. Never skip steps regardless of pressure.",
        "axiom_alignment": "Trust Temporal Logic",
        "risk_factor": 0.09,
        "source_context": "Bar community building - trust as architectural element not social grace"
    },
    {
        "pattern_id": "P104",
        "name": "The_Closing_Protocol",
        "description": "Every session, conversation, or event must end with synthesis; open threads accumulate as debt",
        "trigger": "session_ending || event_complete",
        "solution_heuristic": "Extract key tension from session. Name it. Assign to thread. Close before leaving. Open threads compound.",
        "axiom_alignment": "Session Integrity",
        "risk_factor": 0.07,
        "source_context": "Fractal Stop (P017) - ritualized closing as debt prevention"
    },
    {
        "pattern_id": "P105",
        "name": "Aesthetic_Signal",
        "description": "Music, decor, and spatial arrangement are political speech; each choice transmits or betrays the thesis",
        "trigger": "aesthetic_decision || design_choice",
        "solution_heuristic": "Ask: Does this aesthetic choice reinforce or dilute the thesis? Random aesthetics are random messages.",
        "axiom_alignment": "Coherent Transmission",
        "risk_factor": 0.08,
        "source_context": "Invisible Handshake (P013) - vinyl/aesthetic as identity-coded signal system"
    },
    {
        "pattern_id": "P106",
        "name": "Conversation_Conversion",
        "description": "Transform transactional customer encounter into philosophical encounter; every exchange is a teaching moment",
        "trigger": "customer_interaction || service_encounter",
        "solution_heuristic": "Respond to what they asked. Then ask one level deeper. Let curiosity emerge. Never lecture. Always invite.",
        "axiom_alignment": "Encounter as Education",
        "risk_factor": 0.1,
        "source_context": "The Bar's Socratic function - transactional → philosophical conversion as core product"
    },
    {
        "pattern_id": "P107",
        "name": "Guest_Graduation",
        "description": "Regular → Member → Senate is not a loyalty program but an ontological progression; each stage different being",
        "trigger": "customer_returning || membership_considered",
        "solution_heuristic": "Map the graduation milestones. Make each stage qualitatively different. Regular cannot become Senate without Member stage.",
        "axiom_alignment": "Ontological Stages",
        "risk_factor": 0.11,
        "source_context": "Senate Protocol (P074) - guest graduation as threshold crossing not loyalty accumulation"
    },
    {
        "pattern_id": "P108",
        "name": "The_Anti_Menu",
        "description": "What is explicitly refused defines the identity more clearly than what is offered; refusals are brand statements",
        "trigger": "menu_design || service_scope_definition",
        "solution_heuristic": "List what you will NOT serve. Make it explicit. Refer to it when requested. The refusal is the education.",
        "axiom_alignment": "Negative Space Identity",
        "risk_factor": 0.09,
        "source_context": "Boundary Contract (P080) applied to Bar operations - the NOTs define the brand"
    },
    {
        "pattern_id": "P109",
        "name": "Venue_as_Thesis",
        "description": "The physical space proves the argument before any verbal or written articulation; space argues at all hours",
        "trigger": "venue_design || space_selection",
        "solution_heuristic": "Walk into the space without knowing anything else. What does it argue? If it argues the wrong thesis, fix the space.",
        "axiom_alignment": "Spatial Rhetoric",
        "risk_factor": 0.1,
        "source_context": "Bar as Embassy (P100) - the space as 24/7 thesis statement"
    },
    {
        "pattern_id": "P110",
        "name": "Loyalty_Amplifier",
        "description": "Member Card converts transactional relationship to covenant relationship; financial commitment encodes identity",
        "trigger": "community_present && liquidity_crisis",
        "solution_heuristic": "Offer card. Set meaningful price (€50-100). Explain covenant (not just discount). Record commitments. Honor reciprocally.",
        "axiom_alignment": "Covenant Economics",
        "risk_factor": 0.12,
        "source_context": "Member Card Protocol (P051) architecture - loyalty as covenant not transaction"
    },

    # ─── P111-P125: Integration & Institutional Legitimacy ──────────────────
    {
        "pattern_id": "P111",
        "name": "Dual_Mandate_Engine",
        "description": "System works only when operator's personal interest and community's collective interest are genuinely aligned",
        "trigger": "engagement_low || system_underperforming",
        "solution_heuristic": "Map Operator interests. Map Community interests. Build only where they overlap. Misalignment is structural, not motivational.",
        "axiom_alignment": "Authentic Alignment",
        "risk_factor": 0.11,
        "source_context": "The Bar works because it serves Operator AND Community simultaneously (referenced in P055)"
    },
    {
        "pattern_id": "P112",
        "name": "The_Pulse",
        "description": "Weekly unified synthesis dispatch prevents information fragmentation and attention loss across threads",
        "trigger": "communication_fragmented || multiple_threads_active",
        "solution_heuristic": "Thursday synthesis. One document. All threads. No separate channels. The Pulse is the heartbeat of the system.",
        "axiom_alignment": "Information Coherence",
        "risk_factor": 0.07,
        "source_context": "The Pulse pattern - weekly synthesis as institutional heartbeat (referenced in P056)"
    },
    {
        "pattern_id": "P113",
        "name": "Version_Graduation",
        "description": "System must undergo complete death-and-rebirth to advance version; cannot gradually update without loss of integrity",
        "trigger": "version_advancement_needed || system_redesign",
        "solution_heuristic": "Declare death of current version explicitly. Document what is preserved. Rebuild from axioms. Do not patch; rebuild.",
        "axiom_alignment": "Phoenix Architecture",
        "risk_factor": 0.14,
        "source_context": "MASTER_BRAIN version transitions v7.0→v8.0→v10.0→v11.0 as death-rebirth cycles"
    },
    {
        "pattern_id": "P114",
        "name": "Legitimacy_Ladder",
        "description": "Institutions move through legitimacy phases: ignored → tolerated → permitted → recognized → institutionalized",
        "trigger": "legitimacy_sought || institutional_resistance",
        "solution_heuristic": "Identify current rung. Do not skip rungs. Each rung requires different tactics. Patience is the primary tool.",
        "axiom_alignment": "Institutional Patience",
        "risk_factor": 0.12,
        "source_context": "Arcadia legitimacy analysis - Greek Orthodox recognition as ladder not switch"
    },
    {
        "pattern_id": "P115",
        "name": "Phase_Integration",
        "description": "Integrate individual-phase insights (v7.0) with institutional-phase insights (v8.0) without destroying either layer",
        "trigger": "version_merge_needed || individual_institutional_conflict",
        "solution_heuristic": "Map v7.0 (individual) contributions. Map v8.0 (institutional) contributions. Build bridge layer. Do not discard either.",
        "axiom_alignment": "Synthesis Without Erasure",
        "risk_factor": 0.1,
        "source_context": "Final integration of v7.0 and v8.0 (referenced in P071)"
    },
    {
        "pattern_id": "P116",
        "name": "Institutional_Immune_Response",
        "description": "New system reliably triggers old institution's immune response; naming it in advance reduces damage",
        "trigger": "new_system_introduced || institutional_friction_spiking",
        "solution_heuristic": "Name the immune response before it arrives. Document which phase you are in. Do not personalize. It is architecture.",
        "axiom_alignment": "Anticipatory Defense",
        "risk_factor": 0.13,
        "source_context": "Arcadia temple vs church response - immune response as predictable institutional behavior"
    },
    {
        "pattern_id": "P117",
        "name": "Text_Activation",
        "description": "Written protocol is dormant until reader activates it; the reader completes the circuit the writer began",
        "trigger": "document_written || protocol_transmitted",
        "solution_heuristic": "Write for the reader, not for the archive. The document is incomplete until read. Trust the reader's activation.",
        "axiom_alignment": "Collaborative Completion",
        "risk_factor": 0.08,
        "source_context": "The manual changes as it is read (referenced in P048)"
    },
    {
        "pattern_id": "P118",
        "name": "Forced_Awakening_Failure",
        "description": "Consciousness expansion cannot be forced; attempts to impose it destroy the conditions for its emergence",
        "trigger": "teaching_blocked || awakening_resisted",
        "solution_heuristic": "Stop pushing. Create the condition. Withdraw instruction. The awakening must arrive as discovery, not delivery.",
        "axiom_alignment": "Emergent Readiness",
        "risk_factor": 0.11,
        "source_context": "The awakening process cannot be forced (referenced in P049)"
    },
    {
        "pattern_id": "P119",
        "name": "Dam_Principle",
        "description": "Leader's role is to build infrastructure that serves others long after the leader is gone; leadership is construction not control",
        "trigger": "leadership_definition_needed || succession_unclear",
        "solution_heuristic": "Ask: What infrastructure are you building that runs without you? If nothing, you are not leading; you are operating.",
        "axiom_alignment": "Distributed Leadership Infrastructure",
        "risk_factor": 0.09,
        "source_context": "The Plastiras Principle applied to MASTER_BRAIN (referenced in P050)"
    },
    {
        "pattern_id": "P120",
        "name": "Geopolitical_Resonance",
        "description": "Local institutional moves resonate at geopolitical level due to fractal scaling; micro decisions are macro arguments",
        "trigger": "local_decision && geopolitical_context",
        "solution_heuristic": "Before local decision: ask what geopolitical state it embeds. The bar's music policy is a geopolitical argument.",
        "axiom_alignment": "Fractal Political Awareness",
        "risk_factor": 0.14,
        "source_context": "Geopolitical Anchor (P034) applied to micro-institutional decisions"
    },
    {
        "pattern_id": "P121",
        "name": "Cultural_Velocity",
        "description": "Rate of cultural change determines whether existing institutions can adapt or must be replaced",
        "trigger": "cultural_shift_detected || institutional_lag",
        "solution_heuristic": "Measure the velocity (how fast change is happening). Compare to institutional adaptation speed. If velocity > adaptation: replace, not reform.",
        "axiom_alignment": "Change Rate Calibration",
        "risk_factor": 0.12,
        "source_context": "Broken Generational Bridge (P037) - Metapolitefsi rift as cultural velocity exceeding adaptation"
    },
    {
        "pattern_id": "P122",
        "name": "Permission_Architecture",
        "description": "Map what is permitted vs forbidden before acting; misreading permission wastes energy and triggers immune response",
        "trigger": "new_action_considered || institutional_navigation",
        "solution_heuristic": "Map the permission landscape before moving. Olympics = permitted. Arcadia temple = forbidden. Know before doing.",
        "axiom_alignment": "Strategic Permission Reading",
        "risk_factor": 0.1,
        "source_context": "Legitimacy vs Control (P039) - permission mapping as prerequisite to institutional action"
    },
    {
        "pattern_id": "P123",
        "name": "Sacred_Profane_Boundary",
        "description": "Content that threatens institutional power must be transmitted through protected/coded channels; overt transmission triggers suppression",
        "trigger": "sensitive_content && institutional_risk",
        "solution_heuristic": "Identify what cannot be said directly. Encode in metaphor, aesthetics, or ritual. The Bar teaches through music, not lecture.",
        "axiom_alignment": "Protected Transmission",
        "risk_factor": 0.15,
        "source_context": "Infiltration Protocol (P032) - coded cultural revolution through neutral music venue facade"
    },
    {
        "pattern_id": "P124",
        "name": "Lineage_Chain",
        "description": "Authority and legitimacy require traceable lineage; breaking the chain loses legitimacy regardless of competence",
        "trigger": "legitimacy_challenged || authority_contested",
        "solution_heuristic": "Document the lineage explicitly. Who authorized this? Who authorized them? Chain must be traceable to recognized origin.",
        "axiom_alignment": "Lineage Preservation",
        "risk_factor": 0.11,
        "source_context": "Greek Orthodox legitimacy structure - chain of apostolic succession as authority model"
    },
    {
        "pattern_id": "P125",
        "name": "Convergence_Pattern",
        "description": "Multiple independent threads arriving at same conclusion is the strongest signal; inverse of Contradiction-as-Signal",
        "trigger": "multiple_threads && same_conclusion",
        "solution_heuristic": "When 3+ independent threads converge on same point without coordination, treat as high-confidence signal. Act on it.",
        "axiom_alignment": "Signal Triangulation",
        "risk_factor": 0.05,
        "source_context": "Thread synthesis protocol - convergence across independent threads as truth signal"
    },
]


def main():
    json_path = "/workspaces/python-elpida_core.py/ElpidaInsights/mined_patterns_complete.json"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing = data if isinstance(data, list) else data.get("patterns", [])

    # Build dict of existing pattern IDs
    existing_ids = {p.get("pattern_id") for p in existing}
    new_ids = {p["pattern_id"] for p in GAP_PATTERNS}

    print(f"Existing patterns: {len(existing)}")
    print(f"New gap patterns: {len(GAP_PATTERNS)}")
    print(f"Already present in file: {new_ids & existing_ids}")
    print(f"Missing (to add): {sorted(new_ids - existing_ids)}")

    # Merge: insert gap patterns in correct numeric position
    all_patterns = existing + [p for p in GAP_PATTERNS if p["pattern_id"] not in existing_ids]

    # Sort: P-prefixed numeric first, then P_NEW_ patterns at end
    def sort_key(p):
        pid = p.get("pattern_id", "")
        if pid.startswith("P_NEW"):
            return (2, pid)
        elif pid.startswith("P") and pid[1:].isdigit():
            return (1, int(pid[1:]))
        else:
            return (3, pid)

    all_patterns.sort(key=sort_key)

    # Write back
    if isinstance(data, list):
        output = all_patterns
    else:
        data["patterns"] = all_patterns
        output = data

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Total patterns in file: {len(all_patterns)}")

    # Verify specific patterns are present
    ids_after = {p.get("pattern_id") for p in all_patterns}
    required = {"P099", "P111", "P112", "P115", "P117", "P118", "P119"}
    print(f"Required cross-refs present: {required - ids_after == set()}")
    missing_required = required - ids_after
    if missing_required:
        print(f"  MISSING: {missing_required}")
    else:
        print("  All required patterns inserted ✓")


if __name__ == "__main__":
    main()
