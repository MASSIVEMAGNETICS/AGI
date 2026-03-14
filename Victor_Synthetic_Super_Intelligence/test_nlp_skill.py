#!/usr/bin/env python3
"""
Test script for Advanced NLP Skill
Tests the integration of NLP capabilities into Victor Hub
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from victor_hub.victor_boot import Task
from victor_hub.skills.nlp_skill import AdvancedNLPSkill


def test_nlp_skill():
    """Test the NLP skill with various tasks"""
    
    print("=" * 80)
    print("VICTOR HUB - ADVANCED NLP SKILL TEST")
    print("=" * 80)
    print()
    
    # Initialize the NLP skill
    print("Initializing Advanced NLP Skill...")
    nlp_skill = AdvancedNLPSkill()
    print(f"✓ Skill name: {nlp_skill.name}")
    print(f"✓ Repository: {nlp_skill.repo}")
    print(f"✓ Capabilities: {', '.join(nlp_skill.capabilities)}")
    print()
    
    # Sample text for testing
    sample_text = """
    Artificial Intelligence (AI) is transforming the world. Companies like Google, 
    Microsoft, and OpenAI are leading the charge in developing advanced AI systems. 
    The technology has applications in healthcare, finance, and many other sectors. 
    Victor, the Synthetic Super Intelligence, represents a new generation of AI that 
    can understand and process natural language with remarkable accuracy. Based in 
    San Francisco, these innovations are shaping the future of technology.
    """
    
    # Test 1: Named Entity Recognition
    print("-" * 80)
    print("TEST 1: Named Entity Recognition (NER)")
    print("-" * 80)
    task1 = Task(
        id="test-ner-1",
        type="ner",
        description="Extract entities from text",
        inputs={"text": sample_text}
    )
    
    print("Processing...")
    result1 = nlp_skill.execute(task1, {})
    
    if result1.status == "success":
        print("✓ Status: SUCCESS")
        entities = result1.output.get("entities", [])
        print(f"✓ Found {len(entities)} entities")
        print("\nEntities by type:")
        for entity_type, entity_list in result1.output.get("entity_types", {}).items():
            print(f"  {entity_type}: {', '.join(set(entity_list))}")
    else:
        print(f"✗ Status: FAILED - {result1.error}")
    print()
    
    # Test 2: Sentiment Analysis
    print("-" * 80)
    print("TEST 2: Sentiment Analysis")
    print("-" * 80)
    
    positive_text = "Victor is an amazing AI system! I'm really impressed with its capabilities."
    
    task2 = Task(
        id="test-sentiment-1",
        type="sentiment",
        description="Analyze sentiment",
        inputs={"text": positive_text}
    )
    
    print(f"Text: {positive_text}")
    print("Processing...")
    result2 = nlp_skill.execute(task2, {})
    
    if result2.status == "success":
        print("✓ Status: SUCCESS")
        print(f"✓ Overall Sentiment: {result2.output.get('overall_sentiment')}")
        print(f"✓ Confidence: {result2.output.get('confidence', 0):.2%}")
    else:
        print(f"✗ Status: FAILED - {result2.error}")
    print()
    
    # Test 3: Keyword Extraction
    print("-" * 80)
    print("TEST 3: Keyword Extraction")
    print("-" * 80)
    task3 = Task(
        id="test-keywords-1",
        type="keyword_extraction",
        description="Extract keywords",
        inputs={"text": sample_text}
    )
    
    print("Processing...")
    result3 = nlp_skill.execute(task3, {})
    
    if result3.status == "success":
        print("✓ Status: SUCCESS")
        print("✓ Top Keywords:")
        for item in result3.output.get("top_keywords", [])[:5]:
            print(f"  - {item['keyword']} (frequency: {item['frequency']})")
    else:
        print(f"✗ Status: FAILED - {result3.error}")
    print()
    
    # Test 4: Full NLP Analysis
    print("-" * 80)
    print("TEST 4: Full NLP Analysis")
    print("-" * 80)
    
    short_text = "Victor processes natural language effectively using advanced AI."
    
    task4 = Task(
        id="test-full-1",
        type="nlp",
        description="Full analysis",
        inputs={"text": short_text}
    )
    
    print(f"Text: {short_text}")
    print("Processing...")
    result4 = nlp_skill.execute(task4, {})
    
    if result4.status == "success":
        print("✓ Status: SUCCESS")
        stats = result4.output.get("statistics", {})
        print(f"✓ Word Count: {stats.get('word_count')}")
        print(f"✓ Sentence Count: {stats.get('sentence_count')}")
        print(f"✓ Entities Found: {result4.output.get('entities', {}).get('entity_count', 0)}")
        print(f"✓ Sentiment: {result4.output.get('sentiment', {}).get('overall_sentiment')}")
    else:
        print(f"✗ Status: FAILED - {result4.error}")
    print()
    
    # Test 5: POS Tagging
    print("-" * 80)
    print("TEST 5: Part-of-Speech Tagging")
    print("-" * 80)
    
    pos_text = "The quick brown fox jumps over the lazy dog."
    
    task5 = Task(
        id="test-pos-1",
        type="pos_tagging",
        description="POS tagging",
        inputs={"text": pos_text}
    )
    
    print(f"Text: {pos_text}")
    print("Processing...")
    result5 = nlp_skill.execute(task5, {})
    
    if result5.status == "success":
        print("✓ Status: SUCCESS")
        print(f"✓ Token Count: {result5.output.get('token_count')}")
        print("✓ POS Distribution:")
        for pos, count in result5.output.get("pos_distribution", {}).items():
            print(f"  {pos}: {count}")
    else:
        print(f"✗ Status: FAILED - {result5.error}")
    print()
    
    print("=" * 80)
    print("NLP SKILL TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_nlp_skill()
        print("\n✓ All tests completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
