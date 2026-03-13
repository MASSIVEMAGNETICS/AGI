#!/usr/bin/env python3
"""
IntentSkill - recognize intent and extract slots/arguments from free text.
Lightweight: uses transformers zero-shot (if available) + spaCy entity extraction.
Fallback: rule-based keyword mapper.
"""
import logging
import re
import subprocess
import sys
from typing import Dict, Any, List, Optional

# Integrate with VictorHub Skill/Task/Result patterns
from victor_hub.victor_boot import Skill, Task, Result

logger = logging.getLogger("IntentSkill")

DEFAULT_INTENTS = [
    "summarize",
    "extract_entities",
    "sentiment_analysis",
    "keyword_extraction",
    "pos_tagging",
    "dependency_parsing",
    "run_command",
    "search",
    "create_note",
]

class IntentSkill(Skill):
    def __init__(self, intents: Optional[List[str]] = None):
        super().__init__(
            name="intent_skill",
            repo="VictorIntent",
            capabilities=["intent_recognition", "slot_filling", "command_parsing", "intent"]
        )
        self.intents = intents or DEFAULT_INTENTS
        self._models_loaded = False
        self._zero_shot = None
        self._spacy = None

    def _load_models(self):
        if self._models_loaded:
            return
        try:
            # spaCy for slot/NER extraction fallback
            import spacy
            try:
                self._spacy = spacy.load("en_core_web_sm")
            except OSError:
                subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                             check=True, capture_output=True)
                self._spacy = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"spaCy unavailable: {e}. Slot-filling will be degraded.")
            self._spacy = None

        try:
            from transformers import pipeline
            # zero-shot classification is flexible for intent detection
            self._zero_shot = pipeline("zero-shot-classification", device=-1)
            logger.info("Zero-shot pipeline loaded")
        except Exception as e:
            logger.warning(f"Transformers zero-shot unavailable: {e}. Using rule-based intent mapping.")
            self._zero_shot = None

        self._models_loaded = True

    def execute(self, task: Task, context: dict) -> Result:
        """
        task.inputs expected:
          - text: user utterance
          - session_id (optional)
        returns Result.output with keys: intent, confidence, slots
        """
        self._load_models()
        text = task.inputs.get("text", task.description or "")
        try:
            intent, confidence = self._classify_intent(text)
            slots = self._extract_slots(text)
            return Result(
                task_id=task.id,
                status="success",
                output={"intent": intent, "confidence": confidence, "slots": slots},
                metadata={"skill": self.name}
            )
        except Exception as e:
            logger.exception("Intent recognition failed")
            return Result(task_id=task.id, status="failed", error=str(e), metadata={"skill": self.name})

    def _classify_intent(self, text: str):
        # Try zero-shot first
        if self._zero_shot:
            try:
                res = self._zero_shot(text, self.intents, multi_label=False)
                label = res["labels"][0]
                score = float(res["scores"][0])
                # map model label to canonical intent string
                return label, score
            except Exception as e:
                logger.warning(f"Zero-shot step failed: {e}")

        # Fallback: simple keyword mapping
        low = text.lower()
        mapping = {
            "summarize": ["summarize", "brief", "shorten", "tl;dr"],
            "extract_entities": ["who", "what", "extract entities", "entities", "named entity"],
            "sentiment_analysis": ["sentiment", "feel", "opinion", "attitude"],
            "keyword_extraction": ["keywords", "key words", "important terms"],
            "pos_tagging": ["part of speech", "pos tag", "pos-tag"],
            "dependency_parsing": ["dependency", "parse", "syntax tree"],
            "run_command": ["run", "execute", "do", "perform", "start"],
            "search": ["search", "find", "look up"],
            "create_note": ["note", "save", "remember"]
        }
        for intent, kws in mapping.items():
            for kw in kws:
                if kw in low:
                    return intent, 0.65
        # default fallback
        return "run_command", 0.4

    def _extract_slots(self, text: str) -> Dict[str, Any]:
        slots = {}
        # Use spaCy NER for common slots: PERSON, ORG, GPE, DATE, TIME, MONEY, PERCENT
        if self._spacy:
            doc = self._spacy(text)
            entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
            slots["entities"] = entities
            # simple noun chunk extraction as potential arguments
            slots["noun_chunks"] = [chunk.text for chunk in doc.noun_chunks][:12]
        else:
            # basic heuristics
            words = text.split()
            slots["entities"] = []
            slots["noun_chunks"] = words[:6]
        # Try to extract quoted arguments: "..." or '...'
        quotes = re.findall(r'["\'](.*?)["\']', text)
        if quotes:
            slots["quoted"] = quotes
        return slots
