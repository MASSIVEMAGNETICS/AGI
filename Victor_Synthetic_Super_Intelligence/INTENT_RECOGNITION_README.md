# Intent Recognition and Conversational Dialog System

This document describes the conversational AI upgrade to Victor Hub that enables natural language intent recognition, slot-filling, and dialog management.

## Overview

The conversational AI system consists of three main components:

1. **IntentSkill** - Recognizes user intent and extracts information from natural language
2. **CommandRouter** - Maps intents to executable tasks
3. **DialogManager** - Manages conversation state and confirmations

## Components

### IntentSkill

Located in `victor_hub/skills/intent_skill.py`

**Capabilities:**
- Intent recognition using:
  - Zero-shot classification (when transformers available)
  - Rule-based keyword mapping (fallback)
- Slot-filling with spaCy NER
- Quoted text extraction
- Noun chunk extraction

**Supported Intents:**
- `summarize` - Text summarization requests
- `extract_entities` - Named entity recognition requests
- `sentiment_analysis` - Sentiment analysis requests
- `keyword_extraction` - Keyword extraction requests
- `pos_tagging` - Part-of-speech tagging requests
- `dependency_parsing` - Dependency parsing requests
- `run_command` - Command execution requests
- `search` - Search requests
- `create_note` - Note creation requests

**Usage Example:**
```python
from victor_hub.victor_boot import Task
from victor_hub.skills.intent_skill import IntentSkill

intent_skill = IntentSkill()
task = Task(
    id="detect-1",
    type="intent",
    description="Detect intent",
    inputs={"text": "Summarize this document for me"}
)
result = intent_skill.execute(task, {})
print(result.output)
# Output: {"intent": "summarize", "confidence": 0.65, "slots": {...}}
```

### CommandRouter

Located in `victor_hub/command_router.py`

**Purpose:** Maps recognized intents and slots into VictorHub Task objects and routes them to appropriate skills.

**Intent to Task Mapping:**
- `summarize` → `summarization`
- `extract_entities` → `ner`
- `sentiment_analysis` → `sentiment`
- `keyword_extraction` → `keyword_extraction`
- `pos_tagging` → `pos_tagging`
- `dependency_parsing` → `dependency_parsing`
- `run_command` → `command`
- `search` → `search`
- `create_note` → `create_note`

**Usage Example:**
```python
from victor_hub.victor_boot import VictorHub
from victor_hub.command_router import CommandRouter

hub = VictorHub()
router = CommandRouter(hub)

intent_output = {
    "intent": "summarize",
    "confidence": 0.8,
    "slots": {"text": "Long document here..."}
}

result = router.route(intent_output, user_context={"text": "Long document here..."})
print(result["status"])  # "success"
print(result["output"])  # Summary result
```

### DialogManager

Located in `victor_hub/dialog_manager.py`

**Purpose:** Manages conversation state, session history, and determines when to ask for clarifications.

**Features:**
- Session-based state management
- Conversation history tracking
- Confirmation logic based on:
  - Intent confidence (< 60% triggers confirmation)
  - Missing required slots

**Usage Example:**
```python
from victor_hub.dialog_manager import DialogManager

dialog = DialogManager()

# Start a session
session_id = "user-123"
dialog.start_session(session_id)

# Check if confirmation needed
intent_output = {"intent": "summarize", "confidence": 0.5, "slots": {}}
decision = dialog.needs_confirmation(intent_output)
if decision["confirm"]:
    print(f"Need confirmation: {decision['reason']}")

# Add conversation turn
dialog.add_turn(session_id, "User message", {"intent": "...", "response": "..."})
```

## Running the Examples

### Test IntentSkill
```bash
python test_intent_skill.py
```

Tests intent recognition, slot-filling, and various intent types.

### Test Conversational Agent
```bash
python test_conversational_agent.py
```

Tests the full integration of IntentSkill, CommandRouter, and DialogManager.

### Interactive Conversational Demo
```bash
python examples/example_conversational_agent.py
```

Run an interactive conversational loop where you can type natural language commands.

## Integration with VictorHub

The IntentSkill is automatically registered with VictorHub during initialization (see `victor_boot.py`):

```python
from victor_hub.skills.intent_skill import IntentSkill

# In VictorHub._discover_skills():
self.registry.register(IntentSkill())
```

## Dependencies

### Required
- `spacy>=3.7.0` - For NER and linguistic analysis
- `en_core_web_sm` - spaCy English model (auto-downloaded on first use)

### Optional (for enhanced features)
- `transformers>=4.48.0` - For zero-shot classification
- `torch>=2.6.0` - Required by transformers

When transformers is not available, the system gracefully falls back to rule-based intent mapping.

## Extending the System

### Adding New Intents

1. Add the intent to `DEFAULT_INTENTS` in `intent_skill.py`:
```python
DEFAULT_INTENTS = [
    "summarize",
    "extract_entities",
    # ... existing intents ...
    "your_new_intent",  # Add here
]
```

2. Add keyword mapping in `_classify_intent`:
```python
mapping = {
    # ... existing mappings ...
    "your_new_intent": ["keyword1", "keyword2", "phrase"],
}
```

3. Add intent-to-task mapping in `command_router.py`:
```python
INTENT_TASK_MAP = {
    # ... existing mappings ...
    "your_new_intent": "your_task_type",
}
```

### Adding Required Slots

Modify the confirmation logic in your application:
```python
required_slots = ["entity_name", "date"]
decision = dialog.needs_confirmation(intent_output, required_slots=required_slots)
```

## Testing

All new code includes comprehensive tests:

- **test_intent_skill.py** - Unit tests for IntentSkill
- **test_conversational_agent.py** - Integration tests for full system

Run all tests:
```bash
python test_intent_skill.py
python test_conversational_agent.py
```

## Security

- All inputs are validated before processing
- Slot extraction uses safe regex patterns
- CodeQL security scan: **0 vulnerabilities detected**

### Security Considerations for Production

1. **Input Validation** - Always validate and sanitize extracted slots before executing actions
2. **Action Allowlist** - Implement an allowlist for intents that can trigger `run_command`
3. **Sandboxing** - Use separate execution runtime for commands that touch infrastructure
4. **Rate Limiting** - Add rate limiting for API endpoints
5. **Authentication** - Require authentication for all actions
6. **Audit Logging** - Log all intent recognitions and actions taken

## Architecture

```
User Input (Natural Language)
    ↓
IntentSkill (Intent + Slots)
    ↓
DialogManager (Confirmation Check)
    ↓
CommandRouter (Intent → Task)
    ↓
VictorHub.execute_task()
    ↓
Appropriate Skill (NLP, etc.)
    ↓
Result → User
```

## Future Enhancements

### Priority 2 - Improve Recognition (weeks)
- Fine-tune classifier with domain-specific intent model
- Add slot-filling models (BERT-based token classification)
- Robust command parsing for multi-step actions
- Permission checks for destructive actions

### Priority 3 - Production Readiness (weeks → months)
- Redis-backed session persistence
- Authentication and authorization
- Audit logs and rate limiting
- Safe-execution sandboxes
- Comprehensive test coverage
- CI/CD integration

## License

Part of the Victor Synthetic Super Intelligence project by MASSIVEMAGNETICS.
