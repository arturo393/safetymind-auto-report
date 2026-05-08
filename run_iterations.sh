#!/bin/bash
# SafetyMind PDF Report Iteration Runner
# Runs tests and tracks improvements over time

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_ITERATIONS=${1:-5}
TARGET_SCORE=${2:-1.0}

echo "=============================================="
echo "  SAFETYMIND ITERATION RUNNER"
echo "  Max iterations: $MAX_ITERATIONS"
echo "  Target score: $TARGET_SCORE"
echo "=============================================="
echo ""

for i in $(seq 1 $MAX_ITERATIONS); do
    echo ""
    echo "📄 ITERATION $i/$MAX_ITERATIONS"
    echo "----------------------------------------------"
    
    python3 test_report.py
    
    # Check results
    RESULTS_FILE="test_reports/test_results.json"
    if [ -f "$RESULTS_FILE" ]; then
        PASSED=$(python3 -c "import json; data=json.load(open('$RESULTS_FILE')); print(data['passed'])")
        FAILED=$(python3 -c "import json; data=json.load(open('$RESULTS_FILE')); print(data['failed'])")
        TOTAL=$((PASSED + FAILED))
        SCORE=$(python3 -c "print(f'{$PASSED/$TOTAL:.2f}')")
        
        echo ""
        echo "📊 Score: $PASSED/$TOTAL ($SCORE)"
        
        if [ "$FAILED" -eq 0 ]; then
            echo ""
            echo "✅ ALL TESTS PASSED! Format is professional."
            echo "📄 Report: test_reports/SafetyMind_GSA_*.pdf"
            exit 0
        fi
        
        # Check if we hit target
        HIT_TARGET=$(python3 -c "print('yes' if $SCORE >= $TARGET_SCORE else 'no')")
        if [ "$HIT_TARGET" = "yes" ]; then
            echo ""
            echo "✅ TARGET SCORE REACHED!"
            exit 0
        fi
        
        echo "⏭ Continuing to next iteration..."
    fi
    
    echo ""
done

echo ""
echo "❌ Max iterations reached without achieving target score"
exit 1
