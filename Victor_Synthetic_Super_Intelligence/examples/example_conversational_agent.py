#!/usr/bin/env python3
"""
Example conversational loop that uses IntentSkill + CommandRouter + DialogManager to convert
natural-language statements into Tasks that VictorHub executes.
Run: python examples/example_conversational_agent.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from victor_hub.victor_boot import VictorHub, Task
from victor_hub.skills.nlp_skill import AdvancedNLPSkill
from victor_hub.skills.intent_skill import IntentSkill
from victor_hub.command_router import CommandRouter
from victor_hub.dialog_manager import DialogManager

def demo_conversation():
    hub = VictorHub()
    # Ensure NLP skill is registered (Example repo pattern)
    nlp = AdvancedNLPSkill()
    hub.registry.register(nlp)

    # Register IntentSkill (or ensure it's registered in your skill registry)
    intent_skill = IntentSkill()
    hub.registry.register(intent_skill)

    router = CommandRouter(hub)
    dialog = DialogManager()

    print("Conversational demo. Type messages (type 'quit' to exit).")
    session_id = "user-demo-1"
    while True:
        text = input("You: ").strip()
        if not text or text.lower() in ("quit", "exit"):
            break
        # Create a Task for intent recognition
        t = Task(id="detect-1", type="intent", description="Detect intent", inputs={"text": text})
        res = intent_skill.execute(t, {})
        out = res.output if res.status == "success" else {}
        # Ask for confirmation if needed
        confirm_decision = dialog.needs_confirmation(out, required_slots=None)
        if confirm_decision.get("confirm"):
            print(f"System: I didn't understand fully ({confirm_decision['reason']}). Can you clarify or confirm?")
            clarification = input("You (clarify): ").strip()
            if clarification:
                # naive: re-run intent detection on clarified text
                t2 = Task(id="detect-2", type="intent", description="Detect intent", inputs={"text": clarification})
                res2 = intent_skill.execute(t2, {})
                out = res2.output if res2.status == "success" else out

        # Route and execute
        result = router.route(out, user_context={"text": text})
        print("System:", result.get("status"))
        if result.get("status") == "success":
            print("Output:", result.get("output"))
        else:
            print("Error:", result.get("error", "unknown"))

if __name__ == "__main__":
    try:
        demo_conversation()
    except KeyboardInterrupt:
        print("\nBye")
        sys.exit(0)
