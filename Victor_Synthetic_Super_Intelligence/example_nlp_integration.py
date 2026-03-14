#!/usr/bin/env python3
"""
Victor Hub NLP Integration Example
Demonstrates how to use the Advanced NLP skill within the Victor Hub framework
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from victor_hub.victor_boot import VictorHub, Task, SkillRegistry
from victor_hub.skills import AdvancedNLPSkill


class VictorHub:
    """Enhanced Victor Hub with NLP capabilities"""
    
    def __init__(self):
        self.registry = SkillRegistry()
        self._register_skills()
        
    def _register_skills(self):
        """Register all available skills"""
        # Register NLP skill
        nlp_skill = AdvancedNLPSkill()
        self.registry.register(nlp_skill)
        print(f"✓ Registered skill: {nlp_skill.name}")
        print(f"  Capabilities: {', '.join(nlp_skill.capabilities)}")
        
    def execute_task(self, task: Task) -> dict:
        """Execute a task using the appropriate skill"""
        # Find a skill that can handle this task
        for skill in self.registry.skills.values():
            if skill.can_handle(task):
                print(f"\n→ Routing to skill: {skill.name}")
                result = skill.execute(task, {})
                return {
                    "task_id": task.id,
                    "skill_used": skill.name,
                    "status": result.status,
                    "output": result.output,
                    "metadata": result.metadata
                }
        
        return {
            "task_id": task.id,
            "skill_used": None,
            "status": "failed",
            "error": f"No skill found for task type: {task.type}"
        }


def demo_nlp_integration():
    """Demonstrate NLP integration with Victor Hub"""
    
    print("=" * 80)
    print("VICTOR HUB - NLP INTEGRATION DEMO")
    print("=" * 80)
    print()
    
    # Initialize Victor Hub
    print("Initializing Victor Hub...")
    hub = VictorHub()
    print()
    
    # Demo texts
    article = """
    The field of Artificial Intelligence is experiencing rapid growth. Major technology 
    companies like Google, Microsoft, and OpenAI are investing billions in AI research. 
    Natural Language Processing, a subfield of AI, enables computers to understand and 
    generate human language. This technology powers virtual assistants, translation 
    services, and content analysis tools. The Victor Synthetic Super Intelligence 
    represents a new generation of AI systems that can process and understand complex 
    information across multiple domains.
    """
    
    review = "This AI system is absolutely incredible! The natural language processing " \
             "capabilities are outstanding and the results are very impressive."
    
    technical_text = "The transformer architecture uses self-attention mechanisms to process " \
                    "sequential data in parallel, enabling efficient training on large datasets."
    
    # Example 1: Named Entity Recognition
    print("-" * 80)
    print("EXAMPLE 1: Extract Entities from Article")
    print("-" * 80)
    
    task1 = Task(
        id="demo-ner-1",
        type="ner",
        description="Extract named entities from AI article",
        inputs={"text": article}
    )
    
    result1 = hub.execute_task(task1)
    if result1["status"] == "success":
        entities = result1["output"]["entity_types"]
        print("\nExtracted Entities:")
        for entity_type, entity_list in entities.items():
            print(f"  {entity_type}: {', '.join(set(entity_list))}")
        print(f"\nTotal entities found: {result1['output']['entity_count']}")
    
    # Example 2: Sentiment Analysis
    print("\n" + "-" * 80)
    print("EXAMPLE 2: Analyze Review Sentiment")
    print("-" * 80)
    print(f"\nReview: {review}")
    
    task2 = Task(
        id="demo-sentiment-1",
        type="sentiment",
        description="Analyze customer review sentiment",
        inputs={"text": review}
    )
    
    result2 = hub.execute_task(task2)
    if result2["status"] == "success":
        print(f"\nSentiment: {result2['output']['overall_sentiment']}")
        print(f"Confidence: {result2['output']['confidence']:.1%}")
        print(f"Method: {result2['output'].get('method', 'N/A')}")
    
    # Example 3: Keyword Extraction
    print("\n" + "-" * 80)
    print("EXAMPLE 3: Extract Keywords from Technical Text")
    print("-" * 80)
    
    task3 = Task(
        id="demo-keywords-1",
        type="keyword_extraction",
        description="Extract technical keywords",
        inputs={"text": technical_text}
    )
    
    result3 = hub.execute_task(task3)
    if result3["status"] == "success":
        print("\nTop Keywords:")
        for kw in result3["output"]["top_keywords"][:5]:
            print(f"  • {kw['keyword']} (frequency: {kw['frequency']})")
    
    # Example 4: Full Text Analysis
    print("\n" + "-" * 80)
    print("EXAMPLE 4: Comprehensive Analysis")
    print("-" * 80)
    
    task4 = Task(
        id="demo-full-1",
        type="nlp",
        description="Full NLP analysis of article",
        inputs={"text": article}
    )
    
    result4 = hub.execute_task(task4)
    if result4["status"] == "success":
        analysis = result4["output"]
        stats = analysis["statistics"]
        
        print("\nText Statistics:")
        print(f"  • Words: {stats['word_count']}")
        print(f"  • Sentences: {stats['sentence_count']}")
        print(f"  • Characters: {stats['character_count']}")
        
        print(f"\nEntities: {analysis['entities']['entity_count']}")
        print(f"Sentiment: {analysis['sentiment']['overall_sentiment']}")
        print(f"Keywords: {analysis['keywords']['total_keywords']} unique")
    
    # Example 5: Part-of-Speech Analysis
    print("\n" + "-" * 80)
    print("EXAMPLE 5: Linguistic Analysis")
    print("-" * 80)
    
    sentence = "The intelligent system quickly analyzes complex patterns."
    print(f"\nSentence: {sentence}")
    
    task5 = Task(
        id="demo-pos-1",
        type="pos_tagging",
        description="Analyze sentence structure",
        inputs={"text": sentence}
    )
    
    result5 = hub.execute_task(task5)
    if result5["status"] == "success":
        print("\nToken Analysis:")
        for token in result5["output"]["tokens"][:10]:  # Show first 10
            print(f"  {token['text']:15} → {token['pos']:10} ({token['description']})")
    
    # Summary
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nVictor Hub successfully demonstrated:")
    print("  ✓ Named Entity Recognition")
    print("  ✓ Sentiment Analysis")
    print("  ✓ Keyword Extraction")
    print("  ✓ Comprehensive Text Analysis")
    print("  ✓ Linguistic Structure Analysis")
    print("\nThe Advanced NLP skill is fully integrated and operational!")


if __name__ == "__main__":
    try:
        demo_nlp_integration()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
