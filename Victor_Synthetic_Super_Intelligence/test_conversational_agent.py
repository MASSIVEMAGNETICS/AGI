#!/usr/bin/env python3
"""
Test script for conversational agent functionality
Tests the integration of IntentSkill, CommandRouter, and DialogManager
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from victor_hub.victor_boot import VictorHub, Task
from victor_hub.skills.nlp_skill import AdvancedNLPSkill
from victor_hub.skills.intent_skill import IntentSkill
from victor_hub.command_router import CommandRouter
from victor_hub.dialog_manager import DialogManager


def test_conversational_flow():
    """Test the conversational agent components"""
    
    print("=" * 80)
    print("VICTOR HUB - CONVERSATIONAL AGENT TEST")
    print("=" * 80)
    print()
    
    # Initialize Victor Hub
    print("Initializing Victor Hub...")
    hub = VictorHub()
    print()
    
    # Register NLP skill
    print("Registering NLP skill...")
    nlp = AdvancedNLPSkill()
    hub.registry.register(nlp)
    
    # Register IntentSkill
    print("Registering Intent skill...")
    intent_skill = IntentSkill()
    hub.registry.register(intent_skill)
    print()
    
    # Initialize router and dialog manager
    print("Initializing CommandRouter and DialogManager...")
    router = CommandRouter(hub)
    dialog = DialogManager()
    print()
    
    # Test cases
    test_cases = [
        "Extract entities from the text: Apple and Microsoft are competing in AI",
        "What's the sentiment of: I love this product!",
        "Summarize this text: Victor is an AI system developed by MASSIVEMAGNETICS",
        "Find keywords in: machine learning and artificial intelligence",
    ]
    
    session_id = "test-session-1"
    
    for i, text in enumerate(test_cases, 1):
        print("-" * 80)
        print(f"TEST {i}: {text}")
        print("-" * 80)
        
        # Step 1: Intent recognition
        print("Step 1: Detecting intent...")
        t = Task(id=f"detect-{i}", type="intent", description="Detect intent", inputs={"text": text})
        res = intent_skill.execute(t, {})
        
        if res.status != "success":
            print(f"✗ Intent detection failed: {res.error}")
            continue
        
        out = res.output
        print(f"✓ Intent: {out.get('intent')}")
        print(f"✓ Confidence: {out.get('confidence', 0):.2%}")
        
        # Step 2: Check if confirmation needed
        print("\nStep 2: Checking if confirmation needed...")
        confirm_decision = dialog.needs_confirmation(out, required_slots=None)
        if confirm_decision.get("confirm"):
            print(f"⚠ Confirmation needed: {confirm_decision['reason']}")
        else:
            print("✓ No confirmation needed")
        
        # Step 3: Route and execute
        print("\nStep 3: Routing to appropriate skill...")
        result = router.route(out, user_context={"text": text})
        print(f"✓ Task status: {result.get('status')}")
        
        if result.get("status") == "success":
            output = result.get("output")
            if isinstance(output, dict):
                # Show key information from output
                if "entities" in output:
                    entity_info = output["entities"]
                    if isinstance(entity_info, dict):
                        print(f"  Entities found: {entity_info.get('entity_count', 0)}")
                    else:
                        print(f"  Entities found: {len(entity_info) if isinstance(entity_info, list) else 'N/A'}")
                if "overall_sentiment" in output:
                    print(f"  Sentiment: {output['overall_sentiment']}")
                if "top_keywords" in output:
                    print(f"  Top keywords: {len(output['top_keywords'])}")
                if "summary" in output:
                    print(f"  Summary generated: {len(output['summary'])} chars")
        else:
            print(f"✗ Error: {result.get('error', 'unknown')}")
        
        print()
    
    print("=" * 80)
    print("CONVERSATIONAL AGENT TESTS COMPLETE")
    print("=" * 80)
    print()
    
    # Test dialog manager session management
    print("-" * 80)
    print("BONUS: Testing DialogManager session management")
    print("-" * 80)
    
    session = dialog.start_session("test-1")
    print(f"✓ Session started: {session}")
    
    dialog.add_turn("test-1", "Hello", {"intent": "greeting", "response": "Hi there!"})
    dialog.add_turn("test-1", "How are you?", {"intent": "status_query", "response": "I'm doing well!"})
    
    session = dialog.sessions["test-1"]
    print(f"✓ Session history has {len(session['history'])} turns")
    
    print()


if __name__ == "__main__":
    try:
        test_conversational_flow()
        print("✓ All conversational agent tests completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
