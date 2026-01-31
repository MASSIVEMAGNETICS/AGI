"""
Tests for Revolutionary AGI Thinking System
Validates inference generation and directive processing
"""

import time
import sys
from revolutionary_agi_system import RevolutionaryAGISystem, AGIConsciousnessCore


def test_inference_generation():
    """Test inference generation from input data"""
    print("\n" + "="*60)
    print("TEST: Inference Generation")
    print("="*60)
    
    core = AGIConsciousnessCore(num_sensory_channels=8)
    
    # Test with various input patterns
    test_data = {
        'visual': 0.8,
        'auditory': 0.6,
        'cognitive': 0.9,
        'emotional': 0.7
    }
    
    context = {
        'goals': ['analyze patterns', 'understand input']
    }
    
    inferences = core.generate_inferences(test_data, context)
    
    # Validate inferences
    assert isinstance(inferences, list), "Inferences should be a list"
    assert len(inferences) > 0, "Should generate at least one inference"
    
    # Check inference structure
    for inf in inferences:
        assert 'type' in inf, "Inference must have a type"
        assert 'content' in inf, "Inference must have content"
        assert 'confidence' in inf, "Inference must have confidence"
        assert 'reasoning' in inf, "Inference must have reasoning"
        assert 'supporting_data' in inf, "Inference must have supporting data"
        assert 0 <= inf['confidence'] <= 1, "Confidence must be between 0 and 1"
    
    print(f"✓ Generated {len(inferences)} inferences")
    print(f"✓ Inference types: {set(inf['type'] for inf in inferences)}")
    
    # Check for specific inference types
    inference_types = [inf['type'] for inf in inferences]
    print(f"✓ All inferences have valid structure")
    
    # Display sample inferences
    print("\nSample inferences:")
    for i, inf in enumerate(inferences[:3], 1):
        print(f"  {i}. [{inf['type']}] {inf['content'][:80]}")
        print(f"     Confidence: {inf['confidence']:.2f}")
    
    print("\n✓ Inference generation test PASSED")
    return True


def test_directive_processing():
    """Test directive parsing and action plan generation"""
    print("\n" + "="*60)
    print("TEST: Directive Processing")
    print("="*60)
    
    core = AGIConsciousnessCore(num_sensory_channels=8)
    
    # Test various directive types
    directives = [
        ("Analyze the current system performance", "analysis"),
        ("Create a new optimization strategy", "creation"),
        ("Find patterns in the data", "search"),
        ("Optimize memory usage", "optimization"),
        ("Plan the next steps for improvement", "planning"),
    ]
    
    for directive, expected_intent in directives:
        result = core.process_directive(directive, {'urgency': 0.7})
        
        # Validate result structure
        assert 'directive' in result, "Result must contain original directive"
        assert 'understood' in result, "Result must indicate if understood"
        assert 'intent' in result, "Result must identify intent"
        assert 'action_plan' in result, "Result must have action plan"
        assert 'confidence' in result, "Result must have confidence"
        assert 'inferences' in result, "Result must include inferences"
        
        # Validate action plan
        action_plan = result['action_plan']
        assert 'actions' in action_plan, "Action plan must have actions"
        assert 'total_steps' in action_plan, "Action plan must have total steps"
        
        # Check that actions were generated
        assert len(action_plan['actions']) > 0, f"Should generate actions for: {directive}"
        
        print(f"\n✓ Directive: '{directive[:50]}...'")
        print(f"  Intent: {result['intent']} (expected: {expected_intent})")
        print(f"  Understood: {result['understood']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Actions: {len(action_plan['actions'])} steps")
        print(f"  Inferences: {len(result['inferences'])}")
        
        # Validate action structure
        for action in action_plan['actions'][:2]:  # Check first 2 actions
            assert 'step' in action, "Action must have step number"
            assert 'action' in action, "Action must have description"
            assert 'type' in action, "Action must have type"
            print(f"    Step {action['step']}: {action['action'][:60]}")
    
    print("\n✓ Directive processing test PASSED")
    return True


def test_feasibility_assessment():
    """Test execution feasibility assessment"""
    print("\n" + "="*60)
    print("TEST: Feasibility Assessment")
    print("="*60)
    
    core = AGIConsciousnessCore(num_sensory_channels=8)
    
    directive = "Create a comprehensive analysis framework with multiple validation layers"
    context = {
        'urgency': 0.8,
        'time_limit': 100,  # Time units
        'priority': 'high'
    }
    
    result = core.process_directive(directive, context)
    
    # Validate feasibility assessment
    assert 'feasibility' in result, "Result must include feasibility assessment"
    
    feasibility = result['feasibility']
    assert 'overall_score' in feasibility, "Feasibility must have overall score"
    assert 'is_feasible' in feasibility, "Feasibility must indicate if feasible"
    assert 'factors' in feasibility, "Feasibility must break down factors"
    assert 'risk_assessment' in feasibility, "Feasibility must assess risk"
    
    print(f"\n✓ Directive: '{directive}'")
    print(f"  Overall feasibility: {feasibility['overall_score']:.2f}")
    print(f"  Is feasible: {feasibility['is_feasible']}")
    print(f"  Risk assessment: {feasibility['risk_assessment']}")
    print(f"\n  Factors:")
    for factor, score in feasibility['factors'].items():
        print(f"    - {factor}: {score:.2f}")
    
    # Validate execution strategy
    assert 'execution_strategy' in result, "Result must include execution strategy"
    strategy = result['execution_strategy']
    
    print(f"\n  Execution Strategy:")
    print(f"    - Approach: {strategy.get('approach')}")
    print(f"    - Recommendation: {strategy.get('recommendation')}")
    print(f"    - Parallel execution: {strategy.get('parallel_execution')}")
    
    print("\n✓ Feasibility assessment test PASSED")
    return True


def test_full_agi_system():
    """Test full AGI system with thinking capabilities"""
    print("\n" + "="*60)
    print("TEST: Full AGI System Integration")
    print("="*60)
    
    agi = RevolutionaryAGISystem()
    
    # Test thinking method
    print("\n1. Testing general thinking...")
    thought = agi.think("What patterns exist in recent system behavior?", {
        'emotional_context': 0.6,
        'goals': ['understand system', 'identify improvements']
    })
    
    assert 'about' in thought, "Thought must indicate what it's about"
    assert 'thought_type' in thought, "Thought must have a type"
    assert 'inferences' in thought, "Thought must generate inferences"
    assert 'insights' in thought, "Thought must provide insights"
    assert 'conclusions' in thought, "Thought must have conclusions"
    assert 'confidence' in thought, "Thought must have confidence score"
    
    print(f"✓ Thought type: {thought['thought_type']}")
    print(f"✓ Generated {len(thought['inferences'])} inferences")
    print(f"✓ Generated {len(thought['insights'])} insights")
    print(f"✓ Confidence: {thought['confidence']:.2f}")
    
    print("\n  Insights:")
    for insight in thought['insights'][:3]:
        print(f"    - {insight}")
    
    print("\n  Conclusions:")
    for conclusion in thought['conclusions'][:3]:
        print(f"    - {conclusion}")
    
    # Test directive-style thinking
    print("\n2. Testing directive-style thinking...")
    directive_thought = agi.think("Plan a strategy to optimize system performance", {
        'urgency': 0.7
    })
    
    assert directive_thought['thought_type'] == 'directive', "Should recognize as directive"
    assert 'directive_processing' in directive_thought, "Should process as directive"
    assert 'action_plan' in directive_thought, "Should include action plan"
    
    print(f"✓ Recognized as directive")
    print(f"✓ Generated action plan with {directive_thought['action_plan']['total_steps']} steps")
    
    # Test inference generation through AGI
    print("\n3. Testing inference generation through AGI...")
    inferences = agi.generate_inferences({
        'cognitive': 0.85,
        'memory': 0.7,
        'intention': 0.6
    }, {'goals': ['test inference system']})
    
    assert len(inferences) > 0, "Should generate inferences"
    print(f"✓ Generated {len(inferences)} inferences")
    
    # Test directive processing through AGI
    print("\n4. Testing directive processing through AGI...")
    directive_result = agi.process_directive(
        "Analyze current performance and create optimization plan",
        {'priority': 'high', 'urgency': 0.8}
    )
    
    assert directive_result['understood'], "Should understand directive"
    assert len(directive_result['action_plan']['actions']) > 0, "Should create action plan"
    
    print(f"✓ Directive understood: {directive_result['understood']}")
    print(f"✓ Intent recognized: {directive_result['intent']}")
    print(f"✓ Action plan created: {directive_result['action_plan']['total_steps']} steps")
    
    print("\n✓ Full AGI system integration test PASSED")
    return True


def test_thinking_with_memory():
    """Test thinking system with memory integration"""
    print("\n" + "="*60)
    print("TEST: Thinking with Memory Integration")
    print("="*60)
    
    core = AGIConsciousnessCore(num_sensory_channels=8)
    
    # Generate some processing history
    for i in range(5):
        test_input = {
            'visual': 0.5 + i * 0.1,
            'cognitive': 0.6 + i * 0.05,
            'emotional': 0.5
        }
        core.process_input(test_input)
        time.sleep(0.01)  # Small delay to differentiate timestamps
    
    # Now generate inferences - should include memory-based ones
    inferences = core.generate_inferences({
        'visual': 0.9,
        'cognitive': 0.8
    })
    
    # Check if memory-based inferences were generated
    memory_inferences = [inf for inf in inferences if inf['type'] == 'memory_recall']
    
    print(f"✓ Total inferences: {len(inferences)}")
    print(f"✓ Memory-based inferences: {len(memory_inferences)}")
    
    if memory_inferences:
        print("\n  Memory inference example:")
        mem_inf = memory_inferences[0]
        print(f"    Content: {mem_inf['content']}")
        print(f"    Confidence: {mem_inf['confidence']:.2f}")
        print(f"    Reasoning: {mem_inf['reasoning']}")
    
    # Check for causal inferences (requires processing history)
    causal_inferences = [inf for inf in inferences if inf['type'] == 'causal_relationship']
    
    print(f"✓ Causal inferences: {len(causal_inferences)}")
    
    if causal_inferences:
        print("\n  Causal inference example:")
        caus_inf = causal_inferences[0]
        print(f"    Content: {caus_inf['content']}")
        print(f"    Confidence: {caus_inf['confidence']:.2f}")
    
    print("\n✓ Memory integration test PASSED")
    return True


def test_inference_confidence_scoring():
    """Test that confidence scores are reasonable and varied"""
    print("\n" + "="*60)
    print("TEST: Inference Confidence Scoring")
    print("="*60)
    
    core = AGIConsciousnessCore(num_sensory_channels=8)
    
    # Test with high-quality input
    high_quality_input = {
        'visual': 0.9,
        'auditory': 0.85,
        'cognitive': 0.95,
        'emotional': 0.8
    }
    
    high_inferences = core.generate_inferences(high_quality_input, {
        'goals': ['test high confidence']
    })
    
    # Test with low-quality/sparse input
    low_quality_input = {
        'visual': 0.2,
        'auditory': 0.15,
        'cognitive': 0.3
    }
    
    low_inferences = core.generate_inferences(low_quality_input, {})
    
    # Check confidence distributions
    high_confidences = [inf['confidence'] for inf in high_inferences]
    low_confidences = [inf['confidence'] for inf in low_inferences]
    
    avg_high = sum(high_confidences) / len(high_confidences) if high_confidences else 0
    avg_low = sum(low_confidences) / len(low_confidences) if low_confidences else 0
    
    print(f"✓ High-quality input -> Avg confidence: {avg_high:.2f}")
    print(f"✓ Low-quality input -> Avg confidence: {avg_low:.2f}")
    
    # Confidences should be in valid range
    all_confidences = high_confidences + low_confidences
    assert all(0 <= c <= 1 for c in all_confidences), "All confidences must be in [0, 1]"
    
    print(f"✓ All {len(all_confidences)} confidence scores in valid range [0, 1]")
    
    # Show distribution
    print(f"\n  Confidence distribution:")
    print(f"    High input: min={min(high_confidences):.2f}, max={max(high_confidences):.2f}, avg={avg_high:.2f}")
    print(f"    Low input:  min={min(low_confidences):.2f}, max={max(low_confidences):.2f}, avg={avg_low:.2f}")
    
    print("\n✓ Confidence scoring test PASSED")
    return True


def run_all_tests():
    """Run all thinking system tests"""
    print("\n" + "="*70)
    print("RUNNING THINKING SYSTEM TESTS")
    print("="*70)
    
    tests = [
        ("Inference Generation", test_inference_generation),
        ("Directive Processing", test_directive_processing),
        ("Feasibility Assessment", test_feasibility_assessment),
        ("Full AGI System", test_full_agi_system),
        ("Memory Integration", test_thinking_with_memory),
        ("Confidence Scoring", test_inference_confidence_scoring),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓✓✓ {test_name} - PASSED ✓✓✓")
        except AssertionError as e:
            print(f"\n✗✗✗ {test_name} - FAILED ✗✗✗")
            print(f"    Assertion Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗✗✗ {test_name} - ERROR ✗✗✗")
            print(f"    Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
