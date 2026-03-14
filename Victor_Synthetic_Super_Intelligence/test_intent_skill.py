#!/usr/bin/env python3
"""
Test script for Intent Skill
Tests the integration of intent recognition and slot-filling capabilities into Victor Hub
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from victor_hub.victor_boot import Task
from victor_hub.skills.intent_skill import IntentSkill


def test_intent_skill():
    """Test the Intent skill with various tasks"""
    
    print("=" * 80)
    print("VICTOR HUB - INTENT SKILL TEST")
    print("=" * 80)
    print()
    
    # Initialize the Intent skill
    print("Initializing Intent Skill...")
    intent_skill = IntentSkill()
    print(f"✓ Skill name: {intent_skill.name}")
    print(f"✓ Repository: {intent_skill.repo}")
    print(f"✓ Capabilities: {', '.join(intent_skill.capabilities)}")
    print(f"✓ Supported intents: {', '.join(intent_skill.intents)}")
    print()
    
    # Test 1: Summarization intent
    print("-" * 80)
    print("TEST 1: Summarization Intent")
    print("-" * 80)
    test_text = "Can you summarize this document for me?"
    task1 = Task(
        id="test-intent-1",
        type="intent",
        description="Detect intent",
        inputs={"text": test_text}
    )
    
    print(f"Input: {test_text}")
    print("Processing...")
    result1 = intent_skill.execute(task1, {})
    
    if result1.status == "success":
        print("✓ Status: SUCCESS")
        print(f"✓ Intent: {result1.output.get('intent')}")
        print(f"✓ Confidence: {result1.output.get('confidence', 0):.2%}")
        print(f"✓ Slots: {result1.output.get('slots', {})}")
    else:
        print(f"✗ Status: FAILED - {result1.error}")
    print()
    
    # Test 2: Entity extraction intent
    print("-" * 80)
    print("TEST 2: Entity Extraction Intent")
    print("-" * 80)
    test_text2 = "What entities can you extract from this text about Apple and Microsoft?"
    task2 = Task(
        id="test-intent-2",
        type="intent",
        description="Detect intent",
        inputs={"text": test_text2}
    )
    
    print(f"Input: {test_text2}")
    print("Processing...")
    result2 = intent_skill.execute(task2, {})
    
    if result2.status == "success":
        print("✓ Status: SUCCESS")
        print(f"✓ Intent: {result2.output.get('intent')}")
        print(f"✓ Confidence: {result2.output.get('confidence', 0):.2%}")
        slots = result2.output.get('slots', {})
        if 'entities' in slots and slots['entities']:
            print(f"✓ Extracted entities: {[e['text'] for e in slots['entities']]}")
    else:
        print(f"✗ Status: FAILED - {result2.error}")
    print()
    
    # Test 3: Sentiment analysis intent
    print("-" * 80)
    print("TEST 3: Sentiment Analysis Intent")
    print("-" * 80)
    test_text3 = "What's the sentiment of this text: I love this product!"
    task3 = Task(
        id="test-intent-3",
        type="intent",
        description="Detect intent",
        inputs={"text": test_text3}
    )
    
    print(f"Input: {test_text3}")
    print("Processing...")
    result3 = intent_skill.execute(task3, {})
    
    if result3.status == "success":
        print("✓ Status: SUCCESS")
        print(f"✓ Intent: {result3.output.get('intent')}")
        print(f"✓ Confidence: {result3.output.get('confidence', 0):.2%}")
    else:
        print(f"✗ Status: FAILED - {result3.error}")
    print()
    
    # Test 4: Slot extraction with quoted text
    print("-" * 80)
    print("TEST 4: Slot Extraction with Quoted Text")
    print("-" * 80)
    test_text4 = 'Run the command "ls -la" in the directory'
    task4 = Task(
        id="test-intent-4",
        type="intent",
        description="Detect intent",
        inputs={"text": test_text4}
    )
    
    print(f"Input: {test_text4}")
    print("Processing...")
    result4 = intent_skill.execute(task4, {})
    
    if result4.status == "success":
        print("✓ Status: SUCCESS")
        print(f"✓ Intent: {result4.output.get('intent')}")
        print(f"✓ Confidence: {result4.output.get('confidence', 0):.2%}")
        slots = result4.output.get('slots', {})
        if 'quoted' in slots:
            print(f"✓ Quoted arguments: {slots['quoted']}")
        if 'noun_chunks' in slots:
            print(f"✓ Noun chunks: {slots['noun_chunks'][:5]}")
    else:
        print(f"✗ Status: FAILED - {result4.error}")
    print()
    
    # Test 5: Search intent
    print("-" * 80)
    print("TEST 5: Search Intent")
    print("-" * 80)
    test_text5 = "Search for information about quantum computing"
    task5 = Task(
        id="test-intent-5",
        type="intent",
        description="Detect intent",
        inputs={"text": test_text5}
    )
    
    print(f"Input: {test_text5}")
    print("Processing...")
    result5 = intent_skill.execute(task5, {})
    
    if result5.status == "success":
        print("✓ Status: SUCCESS")
        print(f"✓ Intent: {result5.output.get('intent')}")
        print(f"✓ Confidence: {result5.output.get('confidence', 0):.2%}")
    else:
        print(f"✗ Status: FAILED - {result5.error}")
    print()
    
    print("=" * 80)
    print("INTENT SKILL TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_intent_skill()
        print("\n✓ All tests completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
