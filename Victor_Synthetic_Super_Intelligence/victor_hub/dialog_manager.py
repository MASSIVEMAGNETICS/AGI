#!/usr/bin/env python3
"""
DialogManager - session-based minimal dialog manager for clarifications and confirmations.
Keeps simple state per session_id and can decide whether to ask clarifying questions.
"""
from typing import Dict, Any

class DialogManager:
    def __init__(self):
        # ephemeral session store: {session_id: context}
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def start_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {"history": [], "pending": None}
        return self.sessions[session_id]

    def add_turn(self, session_id: str, user_text: str, system_action: Dict[str, Any]):
        s = self.start_session(session_id)
        s["history"].append({"user": user_text, "system": system_action})

    def needs_confirmation(self, intent_output: Dict[str, Any], required_slots: list = None) -> Dict[str, Any]:
        """
        Determine whether we should ask the user to confirm or clarify.
        Returns a dict:
          {"confirm": bool, "reason": str, "missing_slots": [...]}
        """
        missing = []
        slots = intent_output.get("slots", {})
        # if low confidence -> confirm
        if intent_output.get("confidence", 0) < 0.6:
            return {"confirm": True, "reason": "low_confidence", "missing_slots": []}

        if required_slots:
            for s in required_slots:
                if s not in slots or not slots.get(s):
                    missing.append(s)
            if missing:
                return {"confirm": True, "reason": "missing_slots", "missing_slots": missing}
        return {"confirm": False, "reason": "ok", "missing_slots": []}
