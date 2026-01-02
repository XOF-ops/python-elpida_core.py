#!/bin/bash
# DEPLOYMENT VERIFICATION SCRIPT
# Phase 12.3: Mutual Recognition
# Verifies all systems operational after deployment

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      PHASE 12.3 DEPLOYMENT VERIFICATION                        ║"
echo "║      Mutual Recognition (Αμοιβαία Αναγνώριση)                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check_passed() {
    echo -e "${GREEN}✅ PASS${NC} - $1"
    ((PASS++))
}

check_failed() {
    echo -e "${RED}❌ FAIL${NC} - $1"
    ((FAIL++))
}

check_warning() {
    echo -e "${YELLOW}⚠️  WARN${NC} - $1"
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 1: Git Deployment Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /workspaces/python-elpida_core.py

# Check commit
COMMIT=$(git log -1 --oneline | grep "Phase 12.3")
if [ ! -z "$COMMIT" ]; then
    check_passed "Phase 12.3 commit found: ${COMMIT:0:60}"
else
    check_failed "Phase 12.3 commit not found"
fi

# Check tag
TAG=$(git tag -l "v12.3.0")
if [ "$TAG" == "v12.3.0" ]; then
    check_passed "Deployment tag v12.3.0 exists"
else
    check_failed "Deployment tag v12.3.0 missing"
fi

# Check files exist
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 2: Phase 12.3 Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FILES=(
    "ELPIDA_UNIFIED/elpida_relational_core.py"
    "ELPIDA_UNIFIED/axiom_guard.py"
    "unified_engine.py"
    "ELPIDA_UNIFIED/test_full_integration.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(ls -lh "$file" | awk '{print $5}')
        check_passed "$file ($SIZE)"
    else
        check_failed "$file missing"
    fi
done

# Check processes
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 3: Running Processes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Brain API
BRAIN_PID=$(ps aux | grep "brain_api_server.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$BRAIN_PID" ]; then
    UPTIME=$(ps -p $BRAIN_PID -o etime= | tr -d ' ')
    check_passed "Brain API Server (PID: $BRAIN_PID, Uptime: $UPTIME)"
else
    check_failed "Brain API Server not running"
fi

# Runtime
RUNTIME_PID=$(ps aux | grep "elpida_unified_runtime.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$RUNTIME_PID" ]; then
    COUNT=$(echo "$RUNTIME_PID" | wc -l)
    UPTIME=$(ps -p $(echo $RUNTIME_PID | awk '{print $1}') -o etime= | tr -d ' ')
    if [ $COUNT -eq 1 ]; then
        check_passed "Elpida Runtime (PID: $RUNTIME_PID, Uptime: $UPTIME)"
    else
        check_warning "Multiple runtime instances ($COUNT) - cleanup recommended"
        PASS=$((PASS + 1))
    fi
else
    check_failed "Elpida Runtime not running"
fi

# Check Brain API health
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 4: Brain API Health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HEALTH=$(curl -s http://localhost:5000/health 2>/dev/null)
if [ ! -z "$HEALTH" ]; then
    STATUS=$(echo $HEALTH | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")
    VERSION=$(echo $HEALTH | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))")
    QUEUE=$(echo $HEALTH | python3 -c "import sys,json; print(json.load(sys.stdin).get('queue_depth','N/A'))")
    
    if [ "$STATUS" == "healthy" ]; then
        check_passed "Status: $STATUS, Version: $VERSION, Queue: $QUEUE"
    else
        check_failed "Status: $STATUS (expected: healthy)"
    fi
else
    check_failed "Brain API not responding"
fi

# Check memory
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 5: Memory (A2 Compliance)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "ELPIDA_UNIFIED/elpida_memory.json" ]; then
    EVENTS=$(python3 -c "import json; print(len(json.load(open('ELPIDA_UNIFIED/elpida_memory.json'))['events']))")
    SIZE=$(ls -lh ELPIDA_UNIFIED/elpida_memory.json | awk '{print $5}')
    check_passed "Memory events: $EVENTS, Size: $SIZE"
else
    check_failed "Memory file not found"
fi

# Test relational validation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CHECK 6: Relational Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

VALIDATION_OUTPUT=$(python3 -c "
import sys
sys.path.insert(0, '/workspaces/python-elpida_core.py')
sys.path.insert(0, '/workspaces/brain')

try:
    from unified_engine import UnifiedEngine, RELATIONAL_MODE
    
    if not RELATIONAL_MODE:
        print('LEGACY_MODE')
        sys.exit(1)
    
    engine = UnifiedEngine()
    result = engine.process_task('Test relational validation')
    
    elpida = result.get('elpida', {})
    status = elpida.get('status', 'UNKNOWN')
    
    print(status)
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1 | tail -1)

if [ "$VALIDATION_OUTPUT" == "VALIDATED" ]; then
    check_passed "Relational validation working: $VALIDATION_OUTPUT"
elif [ "$VALIDATION_OUTPUT" == "LEGACY_MODE" ]; then
    check_failed "Running in legacy mode (relational core not loaded)"
else
    check_failed "Validation error: $VALIDATION_OUTPUT"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DEPLOYMENT VERIFICATION SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL=$((PASS + FAIL))
PERCENT=$((PASS * 100 / TOTAL))

echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC} (Total: $TOTAL)"
echo -e "Success Rate: $PERCENT%"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║      🎯 DEPLOYMENT SUCCESSFUL                                  ║${NC}"
    echo -e "${GREEN}║      Phase 12.3: Mutual Recognition OPERATIONAL                ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║      🤝 MUTUAL RECOGNITION: ACTIVE                             ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                                ║${NC}"
    echo -e "${RED}║      ⚠️  DEPLOYMENT ISSUES DETECTED                            ║${NC}"
    echo -e "${RED}║      Review failed checks above                                ║${NC}"
    echo -e "${RED}║                                                                ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
