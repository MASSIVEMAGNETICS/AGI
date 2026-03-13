#!/usr/bin/env python3
"""
CommandRouter - maps recognized intent + slots into VictorHub Task objects and invokes Hub.execute_task.
This module expects a VictorHub instance with execute_task(task) method and a SkillRegistry.
"""
from typing import Dict, Any
from victor_hub.victor_boot import Task

# Simple intent->task_type mapping (extendable)
INTENT_TASK_MAP = {
    "summarize": "summarization",
    "extract_entities": "ner",
    "sentiment_analysis": "sentiment",
    "keyword_extraction": "keyword_extraction",
    "pos_tagging": "pos_tagging",
    "dependency_parsing": "dependency_parsing",
    "run_command": "command",  # custom handler
    "search": "search",
    "create_note": "create_note"
}

class CommandRouter:
    def __init__(self, hub):
        self.hub = hub

    def route(self, intent_output: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build a Task from intent output and dispatch to hub.execute_task.
        intent_output: {"intent": str, "confidence": float, "slots": {...}}
        Returns hub.execute_task() result dict.
        """
        intent = intent_output.get("intent")
        slots = intent_output.get("slots", {})
        task_type = INTENT_TASK_MAP.get(intent, "nlp")

        # Extract text from user_context or slots
        if user_context and "text" in user_context:
            text = user_context["text"]
        elif "quoted" in slots and slots["quoted"]:
            text = " ".join(slots["quoted"]) if isinstance(slots["quoted"], list) else slots["quoted"]
        elif "noun_chunks" in slots and slots["noun_chunks"]:
            text = " ".join(slots["noun_chunks"]) if isinstance(slots["noun_chunks"], list) else slots["noun_chunks"]
        else:
            text = ""

        # Build Task
        task = Task(
            id=f"intent-{intent}",
            type=task_type,
            description=f"Auto-generated task for intent: {intent}",
            inputs={"text": text}
        )

        # If special 'command' intent, include slots so command skill can parse
        task.inputs["slots"] = slots
        # Dispatch
        result = self.hub.execute_task(task)
        
        # Convert Result object to dict for compatibility
        return {
            "task_id": result.task_id,
            "status": result.status,
            "output": result.output,
            "error": result.error,
            "metadata": result.metadata
        }
