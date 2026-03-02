"""
Master_Brain REST API Reference
Complete API specification for integrating Master_Brain into external systems.

Version: 3.5
Endpoints: /execute, /patterns, /validate, /gnosis, /health
"""

# ============================================================================
# BASE URL & AUTHENTICATION
# ============================================================================

BASE_URL = "http://localhost:5000"

# Authentication header for all requests:
# Authorization: Bearer {YOUR_COUNCIL_MEMBER_ID}:{SIGNATURE}

# Example:
# Authorization: Bearer alice:abc123def456...

# ============================================================================
# ENDPOINT 1: Execute Request
# ============================================================================

"""
POST /execute

Execute patterns against input data.
Returns analysis + recommendation + immutable Gnosis block ID.

Request Schema:
{
  "input_quality": 0-7 or "auto",           # 0-7 or "auto" (compute via P002)
  "input_data": { ... },                    # Arbitrary JSON data
  "requested_patterns": [ "P077", "P080" ], # List of pattern IDs
  "governance_required": true,              # If true, needs Council approval
  "execution_mode": "governance",           # "pure_logic", "heuristic", "hybrid", "governance"
  "requester_id": "alice",                  # Who is requesting this
  "metadata": { ... }                       # Optional metadata
}

Response Schema (Success):
{
  "status": "SUCCESS" | "CONFLICT" | "INSUFFICIENT_QUALITY" | "NO_APPLICABLE_PATTERNS",
  "gnosis_block_id": "block_abc123",
  "analysis": {
    "executed_patterns": ["P077", "P080"],
    "synthesis": { ... },
    "recommendations": [ ... ],
    "confidence_level": 0.85
  },
  "warnings": [ ... ],
  "gnosis_signatures": ["alice_sig", "bob_sig"],
  "execution_time_ms": 245,
  "governance_required_for_action": true | false
}

Response Schema (Conflict):
{
  "status": "CONFLICT",
  "conflicts": [["P077", "P079"]],
  "message": "Pattern conflicts detected",
  "suggested_resolution": "Remove P079, keep P077"
}

Response Schema (Insufficient Quality):
{
  "status": "INSUFFICIENT_QUALITY",
  "computed_quality": 2,
  "minimum_required": 4,
  "message": "Input quality too low for requested patterns",
  "guidance": "Provide more evidence, sources, or chain of custody"
}
"""

# Example Request
example_execute_request = {
    "input_quality": "auto",
    "input_data": {
        "decision": "Should we deploy strategic opacity?",
        "context": "3 hostile actors known to monitor us",
        "risk_if_transparent": "Operation fails, 400M assets at risk",
        "duration": "6 months",
        "sources": [
            "Intelligence report from OSINT",
            "Council member interviews",
            "Historical precedent (2 similar ops)"
        ]
    },
    "requested_patterns": ["P077", "P082", "P006"],
    "governance_required": True,
    "execution_mode": "governance",
    "requester_id": "alice",
    "metadata": {
        "decision_id": "STRATEGIC_2024_Q4",
        "council_session": 127
    }
}

# Example Response
example_execute_response = {
    "status": "SUCCESS",
    "gnosis_block_id": "block_deadbeef123",
    "analysis": {
        "executed_patterns": ["P077", "P082", "P006"],
        "synthesis": {
            "thesis": "Transparency is absolute axiom (A3)",
            "antithesis": "Strategic opacity necessary for success",
            "synthesis": "Opacity now + disclosure later = net transparency over time"
        },
        "recommendations": [
            "Deploy Switzerland Model (P077) with time-locked disclosure",
            "Use Safe Rebalancing (P082) to negotiate with counterparties",
            "Implement Recursive Abstraction (P006) to resolve axiom tension"
        ],
        "confidence_level": 0.87,
        "quality_score": 6
    },
    "warnings": [
        "High risk operation; reversibility required",
        "Requires unanimous Witness Council consent"
    ],
    "gnosis_signatures": [],  # Will be populated by council
    "execution_time_ms": 312,
    "governance_required_for_action": True,
    "next_step": "Route to Governance Council for approval"
}

# ============================================================================
# ENDPOINT 2: List Patterns
# ============================================================================

"""
GET /patterns

List all patterns, optionally filtered by section/quality/status.

Query Parameters:
  section: "ROOT_COGNITION" | "GOVERNANCE_DIAGNOSTICS" | "QUALITY_CONTROL" | "STRATEGIC_OPERATIONS" | "SYSTEM_DYNAMICS"
  quality_min: 0-7 (return patterns requiring this quality or lower)
  status: "ACTIVE" | "ARCHIVED" | "DEPRECATED"

Response Schema:
{
  "patterns": [
    {
      "id": "P077",
      "name": "The Switzerland Model",
      "section": "STRATEGIC_OPERATIONS",
      "status": "ACTIVE",
      "logic": "Maintain strategic opacity...",
      "category": "STRATEGY",
      "quality_level_min": 5,
      "axioms_grounded_in": ["A8"],
      "dependencies": [],
      "conflicts_with": [],
      "introduced_in_version": "3.5"
    },
    ...
  ],
  "total_count": 127,
  "filtered_count": 14
}
"""

# ============================================================================
# ENDPOINT 3: Validate Composition
# ============================================================================

"""
POST /validate

Validate that a list of patterns can be safely composed.

Request Schema:
{
  "pattern_ids": ["P077", "P080", "P082"],
  "input_quality": 5
}

Response Schema (Valid):
{
  "valid": true,
  "execution_plan": ["P077", "P080", "P082"],
  "conflicts": [],
  "quality_requirement": 5,
  "axioms_covered": ["A3", "A8"],
  "axioms_missing": ["A1", "A2"],
  "warnings": []
}

Response Schema (Invalid):
{
  "valid": false,
  "conflicts": [["P077", "P079"]],
  "missing_dependencies": ["P006"],
  "quality_requirement": 5,
  "issues": [
    "Pattern P077 conflicts with P079",
    "Quality requirement (5) exceeds input (4)",
    "Pattern P001 required by P077 is missing from request"
  ]
}
"""

# ============================================================================
# ENDPOINT 4: Query Gnosis Archive
# ============================================================================

"""
GET /gnosis

Query immutable Gnosis blocks (decision records).

Query Parameters:
  pattern_id: "P077" (filter by pattern)
  outcome: "success" | "failure" | null (filter by outcome)
  date_from: "2024-01-01" (ISO 8601)
  date_to: "2024-12-31" (ISO 8601)
  requester: "alice" (filter by who requested)
  limit: 100 (return N most recent)
  sort: "newest" | "oldest" | "quality" | "confidence"

Response Schema:
{
  "blocks": [
    {
      "id": "block_abc123",
      "pattern_ids": ["P077", "P080"],
      "input_data": { ... },
      "output_analysis": { ... },
      "outcome": "success" | "failure" | null,
      "timestamp": "2024-12-15T10:30:00Z",
      "quality_score": 6,
      "validated_by": ["alice", "bob"],
      "signature": "abc123...",
      "signed_at": "2024-12-15T10:35:00Z"
    },
    ...
  ],
  "total_matches": 247,
  "limit": 100,
  "offset": 0
}
"""

# ============================================================================
# ENDPOINT 5: Verify Gnosis Block
# ============================================================================

"""
POST /gnosis/verify

Verify cryptographic signature of a Gnosis block.

Request Schema:
{
  "block_id": "block_abc123"
}

Response Schema (Valid):
{
  "valid": true,
  "block_id": "block_abc123",
  "signature": "abc123def456...",
  "signed_by": "alice",
  "signed_at": "2024-12-15T10:35:00Z",
  "algorithm": "HMAC-SHA256",
  "message": "Block signature verified. Unmodified."
}

Response Schema (Invalid):
{
  "valid": false,
  "block_id": "block_abc123",
  "message": "SIGNATURE MISMATCH. Block has been tampered."
}
"""

# ============================================================================
# ENDPOINT 6: Run Diagnostics
# ============================================================================

"""
GET /diagnostics

Run P050, P051, P055 pathology detectors.

Query Parameters:
  patterns: "P050,P051,P055" (comma-separated, or all if omitted)

Response Schema:
{
  "timestamp": "2024-12-20T18:50:00Z",
  "diagnostics": {
    "P050_friction_mapping": {
      "frictions_detected": 3,
      "details": [
        {
          "friction": "Cultural drift between manifesto and practice",
          "violated_axioms": ["A3"],
          "severity": "MEDIUM"
        }
      ]
    },
    "P051_zombie_detection": {
      "zombies_detected": 2,
      "patterns": ["P120", "P015"],
      "recommendation": "Deprecate and replace"
    },
    "P055_cultural_drift": {
      "manifesto_alignment": 0.82,
      "target_alignment": 0.85,
      "drift": 0.03,
      "status": "ACCEPTABLE"
    }
  },
  "system_health": "HEALTHY" | "DEGRADED" | "CRITICAL"
}
"""

# ============================================================================
# ENDPOINT 7: Health Check
# ============================================================================

"""
GET /health

Simple health check. No authentication required.

Response Schema (Healthy):
{
  "status": "HEALTHY",
  "version": "3.5",
  "uptime_seconds": 86400,
  "kernel_verified": true,
  "patterns_loaded": 127,
  "gnosis_blocks": 10247,
  "governance_council_online": 5,
  "last_pathology_check": "2024-12-20T18:45:00Z"
}

Response Schema (Degraded):
{
  "status": "DEGRADED",
  "version": "3.5",
  "issues": [
    "Kernel signature verification pending (updating keys)"
  ]
}

Response Schema (Critical):
{
  "status": "CRITICAL",
  "version": "3.5",
  "issues": [
    "Kernel signature MISMATCH",
    "2+ Council members offline"
  ],
  "action_required": "Investigate immediately"
}
"""

# ============================================================================
# ENDPOINT 8: Council Approval
# ============================================================================

"""
POST /council/approve

Submit a decision for Council approval (only accessible to Council members).

Request Schema:
{
  "gnosis_block_id": "block_abc123",
  "approval": true | false,
  "reason": "Approved per P077 and A8 grounding",
  "signature": "abc123def456..."  # Council member's signature
}

Response Schema (Approved):
{
  "status": "APPROVED",
  "gnosis_block_id": "block_abc123",
  "votes": {
    "core": { "for": 4, "against": 1 },
    "domain": { "for": 8, "against": 3 },
    "witness": { "objections": 0 }
  },
  "decision_timestamp": "2024-12-20T19:00:00Z"
}

Response Schema (Rejected):
{
  "status": "REJECTED",
  "gnosis_block_id": "block_abc123",
  "votes": {
    "core": { "for": 2, "against": 3 },
    "domain": { "for": 5, "against": 6 },
    "witness": { "objections": 2 }
  },
  "reason": "Insufficient quality for strategic deployment"
}
"""

# ============================================================================
# ERROR CODES
# ============================================================================

ERROR_CODES = {
    400: "Bad Request (malformed JSON or invalid parameters)",
    401: "Unauthorized (missing or invalid authentication)",
    403: "Forbidden (insufficient Council permissions)",
    404: "Not Found (pattern or Gnosis block not found)",
    409: "Conflict (pattern conflicts or axiom violation)",
    422: "Unprocessable Entity (validation failed)",
    500: "Internal Server Error",
    503: "Service Unavailable (pathology detected, see /health)"
}

# ============================================================================
# EXAMPLE CURL COMMANDS
# ============================================================================

"""
1. Execute a request:
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer alice:sig123" \
  -d @execute_request.json

2. List strategic patterns:
curl http://localhost:5000/patterns?section=STRATEGIC_OPERATIONS&quality_min=5

3. Validate composition:
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{"pattern_ids": ["P077", "P080"], "input_quality": 5}'

4. Query Gnosis for P077 outcomes:
curl http://localhost:5000/gnosis?pattern_id=P077&outcome=success&limit=10

5. Run pathology check:
curl http://localhost:5000/diagnostics?patterns=P050,P051,P055

6. Health check:
curl http://localhost:5000/health
"""

# ============================================================================
# RATE LIMITING
# ============================================================================

"""
Rate limits (per Council member):
  - /execute: 10 requests/minute
  - /validate: 30 requests/minute
  - /patterns: 60 requests/minute
  - /gnosis: 20 requests/minute
  - /diagnostics: 5 requests/minute

Rate limit headers in response:
  X-RateLimit-Limit: 10
  X-RateLimit-Remaining: 7
  X-RateLimit-Reset: 1703084460

If you exceed rate limit:
  HTTP 429 Too Many Requests
  Retry-After: 60 (seconds)
"""

# ============================================================================
# INTEGRATION EXAMPLE: Python Client
# ============================================================================

import requests
import json
from datetime import datetime

class MasterBrainClient:
    def __init__(self, base_url, council_id, auth_token):
        self.base_url = base_url
        self.council_id = council_id
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {council_id}:{auth_token}",
            "Content-Type": "application/json"
        })

    def execute(self, input_data, patterns, governance_required=True):
        """Execute patterns against input data"""
        payload = {
            "input_quality": "auto",
            "input_data": input_data,
            "requested_patterns": patterns,
            "governance_required": governance_required,
            "execution_mode": "governance" if governance_required else "heuristic",
            "requester_id": self.council_id
        }
        response = self.session.post(f"{self.base_url}/execute", json=payload)
        return response.json()

    def validate_composition(self, patterns, quality=5):
        """Validate pattern composition"""
        payload = {"pattern_ids": patterns, "input_quality": quality}
        response = self.session.post(f"{self.base_url}/validate", json=payload)
        return response.json()

    def query_gnosis(self, pattern_id=None, outcome=None, limit=100):
        """Query Gnosis archive"""
        params = {"limit": limit}
        if pattern_id:
            params["pattern_id"] = pattern_id
        if outcome:
            params["outcome"] = outcome
        response = self.session.get(f"{self.base_url}/gnosis", params=params)
        return response.json()

    def run_diagnostics(self):
        """Run P050, P051, P055 diagnostics"""
        response = self.session.get(f"{self.base_url}/diagnostics")
        return response.json()

    def health(self):
        """Check system health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage:
client = MasterBrainClient("http://localhost:5000", "alice", "auth_token_here")

# Execute with auto quality classification
result = client.execute(
    input_data={"decision": "Deploy P077", "context": "..."},
    patterns=["P077", "P080"],
    governance_required=True
)

print(f"Result: {result['status']}")
print(f"Gnosis Block: {result['gnosis_block_id']}")
print(f"Confidence: {result['analysis']['confidence_level']}")

# Query outcomes of P077
history = client.query_gnosis(pattern_id="P077", outcome="success")
print(f"P077 successes: {len(history['blocks'])}")

# Check system health
health = client.health()
print(f"System: {health['status']} (uptime: {health['uptime_seconds']}s)")

# ============================================================================
# INTEGRATION EXAMPLE: JavaScript/Node.js
# ============================================================================

"""
// Using fetch API
const executePatterns = async (inputData, patterns) => {
  const response = await fetch('http://localhost:5000/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer council_alice:auth_token_here'
    },
    body: JSON.stringify({
      input_quality: 'auto',
      input_data: inputData,
      requested_patterns: patterns,
      governance_required: true,
      execution_mode: 'governance',
      requester_id: 'alice'
    })
  });

  const result = await response.json();
  return result;
};

// Usage:
const decision = await executePatterns(
  {
    decision: 'Deploy Switzerland Model',
    context: 'Strategic opacity for 6 months'
  },
  ['P077', 'P082']
);

console.log(`Status: ${decision.status}`);
console.log(`Gnosis Block: ${decision.gnosis_block_id}`);
console.log(`Confidence: ${decision.analysis.confidence_level}`);
"""

# ============================================================================
# API VERSIONING
# ============================================================================

"""
API Version: 3.5

Future breaking changes will increment version:
  - /api/v3.6/execute (for v3.6 features)
  - /api/v4.0/execute (for major refactoring)

Current version endpoints:
  - /execute (implicit v3.5)
  - /api/v3.5/execute (explicit v3.5)

Both are currently supported. Use explicit versioning for long-term stability.
"""
