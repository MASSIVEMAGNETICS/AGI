# Advanced NLP - Quick Start Guide

## Installation

```bash
# Install core NLP dependencies
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm

# Optional: Install transformers for advanced features
pip install transformers torch
```

## Quick Usage

### 1. Basic Import
```python
from victor_hub.skills import AdvancedNLPSkill

nlp = AdvancedNLPSkill()
```

### 2. Named Entity Recognition
```python
from victor_hub.victor_boot import Task

task = Task(
    id="ner-1",
    type="ner",
    inputs={"text": "Apple Inc. was founded by Steve Jobs in California."}
)

result = nlp.execute(task, {})
print(result.output["entities"])
# Output: [{"text": "Apple Inc.", "label": "ORG"}, ...]
```

### 3. Sentiment Analysis
```python
task = Task(
    id="sentiment-1",
    type="sentiment",
    inputs={"text": "This is amazing!"}
)

result = nlp.execute(task, {})
print(result.output["overall_sentiment"])  # "POSITIVE"
print(result.output["confidence"])         # 0.95
```

### 4. Extract Keywords
```python
task = Task(
    id="keywords-1",
    type="keyword_extraction",
    inputs={"text": "Your article text here..."}
)

result = nlp.execute(task, {})
print(result.output["top_keywords"])
# Output: [{"keyword": "ai", "frequency": 5}, ...]
```

### 5. Summarize Text
```python
task = Task(
    id="summary-1",
    type="summarization",
    inputs={
        "text": "Long article...",
        "max_length": 130,
        "min_length": 30
    }
)

result = nlp.execute(task, {})
print(result.output["summary"])
```

### 6. Full Analysis
```python
task = Task(
    id="analyze-1",
    type="nlp",
    inputs={"text": "Your text..."}
)

result = nlp.execute(task, {})
print(result.output)
# Output: {
#   "statistics": {...},
#   "entities": {...},
#   "sentiment": {...},
#   "keywords": {...}
# }
```

## All Task Types

| Task Type | Description | Output |
|-----------|-------------|--------|
| `ner` | Extract named entities | Entities with labels and positions |
| `sentiment` | Analyze sentiment | Sentiment label + confidence |
| `summarization` | Summarize text | Summary + compression ratio |
| `keyword_extraction` | Extract keywords | Top keywords by frequency |
| `pos_tagging` | Part-of-speech tags | Token-level POS tags |
| `dependency_parsing` | Parse syntax | Dependency tree |
| `language_detection` | Detect language | Language code + confidence |
| `nlp` or `text_analysis` | Full analysis | All features combined |

## Integration with Victor Hub

```python
from victor_hub.victor_boot import VictorHub, SkillRegistry
from victor_hub.skills import AdvancedNLPSkill

# Create hub
hub = VictorHub()

# Register NLP skill
nlp_skill = AdvancedNLPSkill()
hub.registry.register(nlp_skill)

# Execute task
task = Task(id="1", type="ner", inputs={"text": "..."})
result = hub.execute_task(task)
```

## Testing

```bash
# Run NLP skill tests
python test_nlp_skill.py

# Run integration example
python example_nlp_integration.py
```

## Documentation

- **Full Documentation**: [NLP_INTEGRATION.md](NLP_INTEGRATION.md)
- **Implementation Details**: [NLP_IMPLEMENTATION_SUMMARY.md](NLP_IMPLEMENTATION_SUMMARY.md)
- **Main README**: [README.md](README.md)

## Troubleshooting

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### Transformers not available
- NLP skill works without transformers
- Sentiment uses rule-based fallback
- Summarization uses extractive method
- Install transformers for advanced features: `pip install transformers torch`

### Memory issues
- Models load lazily on first use
- Keep skill instance alive to avoid reloading
- Consider using spaCy-only mode (no transformers)

## Performance Tips

1. **Reuse skill instance** - Models stay in memory
2. **Batch processing** - Process multiple texts together
3. **Skip transformers** - Use spaCy-only for speed
4. **Limit text length** - Very long texts may be slow

## Examples

See `example_nlp_integration.py` for complete working examples.

---

**Status**: Production Ready ✅  
**Version**: 1.0.0
