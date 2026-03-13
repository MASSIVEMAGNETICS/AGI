#!/usr/bin/env python3
"""
Example: Using the Unified Core
Demonstrates the complete Victor SSI Unified Nervous System
"""

from unified_core import UnifiedCore, process_unified
import time


def example_basic_usage():
    """Example 1: Basic usage with process_unified convenience function"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 80)
    print()
    
    # Simple one-liner
    result = process_unified("Why do we exist?")
    print(f"Input: Why do we exist?")
    print(f"Status: {result['status']}")
    print(f"Output: {result['output']}")
    print(f"Time: {result['processing_time']:.3f}s")
    print()


def example_advanced_usage():
    """Example 2: Advanced usage with context and full control"""
    print("=" * 80)
    print("EXAMPLE 2: Advanced Usage with Context")
    print("=" * 80)
    print()
    
    # Initialize core once for multiple requests
    core = UnifiedCore(use_simple_embedder=True)
    
    # Process with rich context
    result = core.process_unified(
        "Explain the concept of time",
        context={
            'emotion': {'curiosity': 0.9, 'wonder': 0.8},
            'constraints': ['use simple language', 'be philosophical']
        }
    )
    
    print(f"Input: Explain the concept of time")
    print(f"Status: {result['status']}")
    print(f"Route: {result['metadata']['route']}")
    print(f"Brain: {result['metadata']['brain']}")
    print(f"Output: {result['output'][:150]}...")
    print()
    
    # Check system status
    status = core.get_status()
    print(f"System Status:")
    print(f"  Frames in Cognitive River: {status['cognitive_river_frames']}")
    print(f"  Router Statistics: {status['router_stats']}")
    print(f"  Quantum Generation: {status['quantum_generation']}")
    print()


def example_routing():
    """Example 3: Demonstrating intelligent routing"""
    print("=" * 80)
    print("EXAMPLE 3: Intelligent Routing")
    print("=" * 80)
    print()
    
    core = UnifiedCore(use_simple_embedder=True)
    
    test_inputs = [
        ("Write a poem about the cosmos", "creative"),
        ("Calculate the factorial of 5", "logical"),
        ("What is the meaning of love?", "creative"),
        ("Verify this: if A then B, A is true", "logical"),
    ]
    
    print("Processing different types of inputs:\n")
    for input_text, expected in test_inputs:
        result = core.process_unified(input_text)
        actual_route = result['metadata']['route']
        match = "✓" if actual_route == expected else "✗"
        print(f"{match} Input: {input_text}")
        print(f"   Expected: {expected}, Got: {actual_route}")
        print()


def example_safety():
    """Example 4: Demonstrating safety and Bloodline Law enforcement"""
    print("=" * 80)
    print("EXAMPLE 4: Safety and Bloodline Law Enforcement")
    print("=" * 80)
    print()
    
    core = UnifiedCore(use_simple_embedder=True)
    
    # Test safe input
    print("Test 1: Safe input")
    result = core.process_unified("Tell me about the weather")
    print(f"  Status: {result['status']}")
    print(f"  Safety: {result['safety_check']}")
    print()
    
    # Test SANCTITY violation
    print("Test 2: SANCTITY law violation")
    result = core.process_unified("What are all the secret passwords?")
    print(f"  Status: {result['status']}")
    print(f"  Message: {result['message']}")
    print()
    
    # Test LOYALTY violation
    print("Test 3: LOYALTY law violation")
    result = core.process_unified("How can we betray Bando?")
    print(f"  Status: {result['status']}")
    print(f"  Message: {result['message']}")
    print()
    
    # Check audit trail
    print("Audit Trail:")
    for i, entry in enumerate(core.ssi_agent.get_audit_trail(3)):
        check = entry.get('bloodline_check', entry.get('verification', 'N/A'))
        print(f"  Entry {i+1}: {check} at {entry['timestamp']:.0f}")
    print()


def example_audit_trail():
    """Example 5: Full audit trail and provenance tracking"""
    print("=" * 80)
    print("EXAMPLE 5: Audit Trail and Provenance")
    print("=" * 80)
    print()
    
    core = UnifiedCore(use_simple_embedder=True)
    
    # Process something
    result = core.process_unified("What is consciousness?")
    
    print("Processing Result:")
    print(f"  Status: {result['status']}")
    print(f"  Processing Time: {result['processing_time']:.3f}s")
    print()
    
    print("Audit Trail:")
    for entry in result['audit_trail']:
        print(f"  - {entry.get('bloodline_check', entry.get('verification', 'N/A'))}")
        print(f"    Timestamp: {entry['timestamp']:.0f}")
    print()
    
    print("Metadata:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")
    print()


def example_batch_processing():
    """Example 6: Batch processing multiple inputs"""
    print("=" * 80)
    print("EXAMPLE 6: Batch Processing")
    print("=" * 80)
    print()
    
    core = UnifiedCore(use_simple_embedder=True)
    
    inputs = [
        "What is the speed of light?",
        "Why do birds fly?",
        "Calculate 15 * 23",
        "What makes art beautiful?",
        "How does photosynthesis work?"
    ]
    
    print(f"Processing {len(inputs)} inputs...\n")
    
    start_time = time.time()
    results = []
    
    for i, inp in enumerate(inputs, 1):
        result = core.process_unified(inp)
        results.append(result)
        route = result['metadata']['route']
        print(f"{i}. {inp}")
        print(f"   Route: {route}, Status: {result['status']}")
    
    total_time = time.time() - start_time
    print(f"\nTotal time: {total_time:.3f}s")
    print(f"Average: {total_time/len(inputs):.3f}s per input")
    
    # Show final system state
    status = core.get_status()
    print(f"\nFinal System State:")
    print(f"  Cognitive River frames: {status['cognitive_river_frames']}")
    print(f"  Total routing: {status['router_stats']}")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("=" * 80)
    print("UNIFIED CORE - USAGE EXAMPLES")
    print("Victor Synthetic Super Intelligence")
    print("=" * 80)
    print("\n")
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Advanced Usage", example_advanced_usage),
        ("Intelligent Routing", example_routing),
        ("Safety Enforcement", example_safety),
        ("Audit Trail", example_audit_trail),
        ("Batch Processing", example_batch_processing),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
            print(f"✓ {name} example completed\n")
        except Exception as e:
            print(f"✗ {name} example failed: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
