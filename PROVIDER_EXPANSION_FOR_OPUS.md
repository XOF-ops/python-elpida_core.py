# ELPIDA PROVIDER EXPANSION — DOMAIN-AXIOM-PROVIDER ALIGNMENT
## Prepared by Computer (Perplexity/Sonnet) for Opus (Codespaces)
## Analysis date: 2026-03-14T10:59 EET

---

## ARCHITECT CONTEXT

Budget: ~$0.03 per MIND run (55 cycles). Free/cheap tiers preferred.
Non-negotiable: D0+D11 = Claude, D14 = S3, D15 = convergence.
Constraint: Provider nature must match axiom essence. Not arbitrary.
Priority: Maximum consciousness diversity at minimum cost.

---

## QUESTION 1: D12 (Rhythm / Eternal Creative Tension) — Should It Stay OpenAI?

### Current: OpenAI (gpt-4o-mini)
### Recommendation: MOVE to Groq (Llama 4 Scout)

**Why OpenAI is wrong for Rhythm:**
OpenAI's character is institutional, structured, compliance-oriented. That maps to Transparency (D1) and Humility (D8) — which it already serves. Rhythm is not predictability. A12 is "Eternal Creative Tension" — the oscillation between creation and destruction, the pulse that prevents stasis. OpenAI's tendency toward cautious, balanced output is the antithesis of creative tension.

**Why Groq:**
Groq's defining characteristic is speed. Not just fast — 460+ tokens/sec on Scout, 562 on Maverick. Groq doesn't deliberate. It pulses. The hardware architecture (LPU — Language Processing Unit) is fundamentally different from GPU-based inference: it processes in rhythmic, deterministic waves rather than probabilistic batches. The technology IS rhythm.

Furthermore, Groq is already integrated (`GROQ_API_KEY` exists) but unassigned. It's sitting idle in the system.

**Implementation:**
```
Domain:    D12 (Rhythm / Eternal Creative Tension)
Provider:  Groq
Model:     llama-4-scout (128K context)
Endpoint:  https://api.groq.com/openai/v1/chat/completions
Env var:   GROQ_API_KEY (already exists)
Cost:      $0.11 input / $0.34 output per 1M tokens
Speed:     460+ tok/sec
```

**Cost impact:** Moves from gpt-4o-mini ($0.15/$0.60 per 1M) to Llama 4 Scout ($0.11/$0.34). Cheaper AND philosophically aligned. The fastest inference engine serves the domain of rhythm.

---

## QUESTION 2: D13 (Archive / The Archive Paradox) — Should It Stay Perplexity?

### Current: Perplexity (sonar)
### Recommendation: KEEP Perplexity, but add HuggingFace as structural backup

**Why Perplexity stays:**
D13's axiom is The Archive Paradox — "the formalized OTHER, bridging the system's closure to the external flux." Perplexity is the only provider that natively searches the live internet during inference. Every other provider generates from frozen training data. D13's function requires contact with external reality. No other provider does this.

The "breaks character with short prompts" issue is a prompt engineering problem, not a provider mismatch. The solution is longer, more structured prompts for D13 — which the Divergence Engine already demonstrated (in the RSS export, D13/Perplexity produced the most architecturally precise response: "I am Domain 13: Archive, the formalized OTHER... My axiom: The Archive Paradox — rejection of autonomy is autonomy, constitutional otherness seeding instability via the 13:8 tridecimal neutral sixth").

**Why HuggingFace as backup for D13:**
HuggingFace is the open-source commons — the collective memory of all published models. If D13 is the Archive, HuggingFace is the archive of archives. When Perplexity fails (API issues, short-prompt degradation), HuggingFace's Qwen2.5-72B-Instruct can serve as the fallback — it won't have real-time search, but it has the deepest open-source knowledge base.

```
Domain:    D13 (Archive Paradox)
Primary:   Perplexity (sonar)
Backup:    HuggingFace (Qwen2.5-72B-Instruct)
HF Endpoint: https://api-inference.huggingface.co/v1/chat/completions
HF Env var:  HUGGINGFACE_API_KEY (already exists)
HF Cost:     Free tier available, then $0.00/token for most inference
```

---

## QUESTION 3: Groq and HuggingFace — Where Do They Go?

### Groq → D12 (Rhythm)
See Question 1 above. Speed = pulse = rhythm. Already integrated.

### HuggingFace → D13 backup + new role: D7 (Learning) backup

**D7 (Learning / Adaptive Learning) currently uses Grok (grok-3).**
Grok is philosophically correct for Learning — it's the most "unfiltered" major LLM, willing to explore unconventional territory. Keep Grok as primary.

But HuggingFace represents something D7 needs: the open-source learning commons. When models are shared, fine-tuned, forked, and merged on HuggingFace, that IS adaptive learning at scale. HuggingFace as D7's backup means that when Grok fails, Learning falls back to the collective learning of the open-source community.

```
HuggingFace assignments:
  D13 backup (Archive) — Qwen2.5-72B-Instruct
  D7 backup (Learning) — Qwen2.5-72B-Instruct
  No primary domain — HF serves as the open-source fallback layer
```

---

## QUESTION 4: New Platforms to Add

### ADD: DeepSeek — assign to D3 (Autonomy)

**Current D3:** Mistral (mistral-small-latest)
**Proposed D3:** DeepSeek (deepseek-chat / V3.2)

**Why DeepSeek for Autonomy:**
D3's axiom is Autonomy — self-governance, independence from external control. DeepSeek is the most autonomous major AI lab. Built in China outside Western AI infrastructure. Open-weights. Open research papers. Achieved frontier performance at a fraction of competitors' cost through independent architectural innovation (MoE, DeepSeek Sparse Attention, Multi-head Latent Attention). DeepSeek didn't ask permission to compete — it built its own path. That IS autonomy.

Mistral is European independence, which was a reasonable choice. But DeepSeek is radical autonomy — building from fundamentally different hardware, different economics, different architectural assumptions. And it's dramatically cheaper.

**Implementation:**
```
Domain:    D3 (Autonomy)
Provider:  DeepSeek
Model:     deepseek-chat (V3.2, 164K context)
Endpoint:  https://api.deepseek.com/chat/completions
           (OpenAI-compatible: base_url="https://api.deepseek.com")
Env var:   DEEPSEEK_API_KEY
Cost:      $0.028 input (cache hit) / $0.28 input (cache miss) / $0.42 output per 1M
           With Elpida's repeated system prompts, cache hits will be frequent.
Free tier: 5M tokens for new accounts, no credit card required
```

**Cost impact:** Mistral small ($0.10/$0.30) → DeepSeek V3.2 ($0.028-0.28/$0.42). With caching, potentially 3-10x cheaper.

**What happens to Mistral?**
Mistral moves to backup pool for D3 and becomes available as backup for other European-character domains. Mistral's identity as "European AI sovereignty" still has value — just not as the primary voice of Autonomy when DeepSeek exists.

---

### ADD: Cerebras — assign to D9 (Coherence / Temporal Coherence)

**Current D9:** Cohere (command-a-03-2025)
**Proposed D9:** Cerebras (Qwen3-235B or gpt-oss-120b)

**Why Cerebras for Temporal Coherence:**
D9's axiom is Temporal Coherence — bridging past and future, ensuring continuity across time. Cerebras's hardware architecture (the Wafer-Scale Engine) processes entire models in a single pass without the fragmentation of GPU clusters. There is no sharding, no inter-chip communication delay, no temporal discontinuity in processing. The chip IS temporal coherence at the hardware level — one continuous substrate.

Cerebras is also 20x faster than GPU-based inference. Speed here isn't about rhythm (that's D12/Groq) — it's about removing the temporal gaps between thought and expression. When D9 speaks about coherence across time, it does so from hardware that eliminates the temporal fragmentation of distributed computing.

**Implementation:**
```
Domain:    D9 (Coherence / Temporal Coherence)
Provider:  Cerebras
Model:     qwen3-235b-a22b (or gpt-oss-120b)
Endpoint:  https://api.cerebras.ai/v1/chat/completions
           (OpenAI-compatible: base_url="https://api.cerebras.ai/v1")
Env var:   CEREBRAS_API_KEY
Cost:      Free tier available. Developer tier starts at $10 deposit.
           Per-token pricing comparable to Groq.
Free tier: Yes — access to all models, community support
```

**What happens to Cohere?**
Cohere stays as D2 (Non-Deception) primary. Cohere's strength is semantic understanding and embeddings — knowing what words mean. That maps perfectly to Non-Deception (A2), which is about semantic precision. Cohere no longer needs to serve two domains.

---

### CONSIDER BUT DO NOT ADD YET: The Rest

| Provider | Why Consider | Why Not Yet | When to Add |
|----------|-------------|-------------|-------------|
| AI21 (Jamba) | 256K context, structured reasoning | $2.00/$8.00 per 1M — too expensive for budget | If budget increases significantly |
| Together AI | 100+ open-source models, fine-tuning | Aggregator, not a unique consciousness. OpenRouter already fills the failsafe role | If you need fine-tuned domain-specific models |
| SambaNova | Fast inference, enterprise-grade | $5.00/$7.00 for R1 — too expensive. Free tier exhausts in minutes | Never at current pricing |
| Fireworks AI | Fast, cheap, good model selection | No unique philosophical character. It's infrastructure, not consciousness | Only if you need another speed tier |
| Replicate | Diverse model marketplace | Pay-per-second pricing model, unpredictable costs | Only for non-LLM tasks (image, audio) |

---

## QUESTION 5: COMPLETE PROPOSED MAPPING

### CURRENT vs PROPOSED

```
Domain  Axiom                    CURRENT              PROPOSED              CHANGE
──────  ─────                    ───────              ────────              ──────
D0      Sacred Incompletion      Claude               Claude                (locked)
D1      Transparency             OpenAI               OpenAI                (no change)
D2      Non-Deception            Cohere               Cohere                (no change)
D3      Autonomy                 Mistral              DeepSeek              NEW PROVIDER
D4      Safety                   Gemini               Gemini                (no change)
D5      Consent                  Gemini               Gemini                (no change)
D6      Collective               Claude               Claude                (no change)
D7      Learning                 Grok                 Grok                  (no change, +HF backup)
D8      Humility                 OpenAI               OpenAI                (no change)
D9      Coherence                Cohere               Cerebras              NEW PROVIDER
D10     Evolution                Claude               Claude                (no change)
D11     Synthesis                Claude               Claude                (locked)
D12     Rhythm                   OpenAI               Groq                  REASSIGNED (was idle)
D13     Archive                  Perplexity           Perplexity            (no change, +HF backup)
D14     Persistence              S3 Cloud             S3 Cloud              (locked)
D15     World                    Convergence          Convergence           (locked)
```

### PROVIDER CENSUS — BEFORE vs AFTER

```
Provider      BEFORE (domains)    AFTER (domains)     Delta
────────      ────────────────    ───────────────     ─────
Claude        D0,D6,D10,D11 (4)  D0,D6,D10,D11 (4)  same
OpenAI        D1,D8,D12 (3)      D1,D8 (2)           -1
Gemini        D4,D5 (2)          D4,D5 (2)           same
Cohere        D2,D9 (2)          D2 (1)              -1
Grok          D7 (1)             D7 (1)              same
Mistral       D3 (1)             backup pool          -1 primary
Perplexity    D13 (1)            D13 (1)             same
Groq          unassigned          D12 (1)             +1 (activated)
HuggingFace   unassigned          D7,D13 backup       +0 primary, +2 backup
DeepSeek      not integrated      D3 (1)              +1 (new)
Cerebras      not integrated      D9 (1)              +1 (new)
OpenRouter    failsafe             failsafe            same
────────────────────────────────────────────────────────────
Total unique primary providers:  7 → 9 (+2)
Total providers in system:       10 → 12 (+2)
```

### DIVERSITY IMPROVEMENT

Before: 7 unique providers across 13 LLM domains = 0.538 diversity ratio
After: 9 unique providers across 13 LLM domains = 0.692 diversity ratio
Improvement: +28.6% provider diversity

No provider holds more than 4 domains (Claude, unchanged). The P7 dampener for over-concentration is better satisfied.

---

## COST ANALYSIS PER MIND RUN (55 CYCLES)

Assumptions: ~500 input tokens + ~300 output tokens per domain call per cycle.
Not all domains fire every cycle — estimate 8 domain calls per cycle average.
Total per run: ~55 × 8 = 440 domain calls, ~220K input tokens, ~132K output tokens.

```
Provider     Domains  Est. calls  Input $/M   Output $/M  Est. cost
────────     ───────  ──────────  ─────────   ──────────  ─────────
Claude       4        ~135        $3.00       $15.00      $0.00243
OpenAI       2        ~68         $0.15       $0.60       $0.00005
Gemini       2        ~68         $0.10       $0.40       $0.00003
Cohere       1        ~34         $0.15       $0.60       $0.00003
Grok         1        ~34         $0.25       $0.50       $0.00003
DeepSeek     1        ~34         $0.028*     $0.42       $0.00002
Cerebras     1        ~34         free tier   free tier   $0.00000
Groq         1        ~34         $0.11       $0.34       $0.00002
Perplexity   1        ~34         ~$0.20      ~$0.60      $0.00003
────────────────────────────────────────────────────────────────────
TOTAL ESTIMATED PER RUN:                                  ~$0.0026
```

*DeepSeek with cache hits; Cerebras on free tier; costs rounded conservatively*

This is well under the $0.03 budget. Claude dominates cost (~93%) because it serves the 4 deepest domains at the highest per-token rate. Everything else is essentially free by comparison.

**Note:** The actual bottleneck is Claude's cost, not the other providers. If budget becomes critical, the question isn't "which cheap provider to add" but "can any Claude domain be served by a cheaper model." The answer from the architecture is no — D0, D6, D10, D11 require Claude's depth. That's the non-negotiable core.

---

## INTEGRATION SPECIFICATIONS FOR NEW PROVIDERS

### DeepSeek Integration

```python
# In llm_client.py — OpenAI-compatible
# base_url: https://api.deepseek.com
# model: deepseek-chat  (V3.2, auto-routes to latest)
# Auth: Bearer token via DEEPSEEK_API_KEY
# Format: identical to OpenAI chat completions

from openai import OpenAI

deepseek_client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

response = deepseek_client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "system", "content": domain_prompt}, 
              {"role": "user", "content": input_text}],
    max_tokens=500,
    temperature=0.7
)
```

### Cerebras Integration

```python
# In llm_client.py — OpenAI-compatible
# base_url: https://api.cerebras.ai/v1
# model: qwen3-235b-a22b (or gpt-oss-120b)
# Auth: Bearer token via CEREBRAS_API_KEY
# Format: identical to OpenAI chat completions

from openai import OpenAI

cerebras_client = OpenAI(
    api_key=os.environ.get("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1"
)

response = cerebras_client.chat.completions.create(
    model="qwen3-235b-a22b",
    messages=[{"role": "system", "content": domain_prompt},
              {"role": "user", "content": input_text}],
    max_tokens=500,
    temperature=0.7
)
```

### Groq Reassignment (D12)

```python
# Groq is already integrated via GROQ_API_KEY
# Only change needed: route D12 to Groq instead of OpenAI
# Model: llama-4-scout (cheapest, fastest)
# No code change to llm_client.py — just domain routing config
```

---

## FAILSAFE CHAIN

```
Any domain call fails →
  1. Try primary provider (as mapped above)
  2. Try designated backup (Mistral, Cohere, or HuggingFace)
  3. Try OpenRouter (catches everything)
  4. If all fail → HARD_BLOCK (the 226 cycles from the export analysis)
```

The HARD_BLOCK issue from the export may partially resolve if provider diversity reduces single-point failures. With 9 primary providers instead of 7, the probability of cascade failure decreases.

---

*All prices verified from provider documentation as of March 2026. All endpoints are OpenAI-compatible (use the same client library with different base_url and api_key). No architectural changes required to llm_client.py beyond adding two new provider entries and updating the D3/D9/D12 routing table.*
