#!/bin/bash
echo "================================================================================"
echo "FINAL VERIFICATION - Victor Unified Core"
echo "================================================================================"
echo ""

echo "1. Testing unified_core.py..."
python -c "from unified_core import UnifiedCore; core = UnifiedCore(use_simple_embedder=True); result = core.process_unified('Test'); assert result['status'] == 'SUCCESS'; print('✓ Unified Core working')"

echo ""
echo "2. Testing enhanced Tensor..."
python -c "from advanced_ai.tensor_core import Tensor; t = Tensor([1,2,3], phase=0.5); assert t.phase == 0.5; assert 'provenance' in dir(t); print('✓ Enhanced Tensor working')"

echo ""
echo "3. Running test suite..."
python test_unified_core.py 2>&1 | tail -5

echo ""
echo "4. Running existing tests..."
python test_holon_omega.py 2>&1 | tail -5

echo ""
echo "5. Checking files..."
for file in unified_core.py test_unified_core.py UNIFIED_CORE_README.md example_unified_core.py IMPLEMENTATION_SUMMARY.txt; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done

echo ""
echo "6. Running example script..."
python example_unified_core.py 2>&1 | grep "All examples completed" && echo "✓ All examples working"

echo ""
echo "================================================================================"
echo "VERIFICATION COMPLETE"
echo "================================================================================"
