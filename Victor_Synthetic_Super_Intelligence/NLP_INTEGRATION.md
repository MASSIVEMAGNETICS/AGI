# Advanced NLP Integration - Victor Hub

## Overview

This document describes the advanced Natural Language Processing (NLP) capabilities integrated into the Victor Synthetic Super Intelligence Hub. The integration provides state-of-the-art NLP features leveraging spaCy and Hugging Face Transformers.

## Features

### Core NLP Capabilities

1. **Named Entity Recognition (NER)**
   - Extracts entities like persons, organizations, locations, dates, etc.
   - Provides entity type classification and grouping
   - Returns character-level positions for each entity

2. **Sentiment Analysis**
   - Overall document sentiment (positive/negative)
   - Sentence-level sentiment breakdown
   - Confidence scores for predictions
   - Uses fine-tuned DistilBERT model

3. **Text Summarization**
   - Extractive summarization using BART
   - Configurable summary length
   - Compression ratio calculation
   - Intelligent handling of short texts

4. **Part-of-Speech (POS) Tagging**
   - Token-level POS tags
   - Lemmatization
   - POS distribution statistics
   - Dependency relation tagging

5. **Dependency Parsing**
   - Syntactic dependency trees
   - Head-child relationships
   - Detailed grammatical structure

6. **Keyword Extraction**
   - Noun chunk extraction
   - Named entity keywords
   - Frequency-based ranking
   - Stopword filtering

7. **Language Detection**
   - Text language identification
   - Confidence scoring

8. **Full Text Analysis**
   - Comprehensive analysis combining all features
   - Statistical metrics (word count, sentence count, etc.)
   - Multi-dimensional insights

## Installation

### Dependencies

The NLP skill requires the following packages:

```bash
pip install spacy>=3.7.0
pip install transformers>=4.48.0
pip install torch>=2.6.0
pip install sentencepiece>=0.2.0
pip install tokenizers>=0.19.0
```

All dependencies are included in the `requirements.txt` file.

### spaCy Model

The English language model is automatically downloaded on first use:

```bash
python -m spacy download en_core_web_sm
```

## Usage

### Basic Usage

```python
from victor_hub.victor_boot import Task
from victor_hub.skills.nlp_skill import AdvancedNLPSkill

# Initialize the skill
nlp_skill = AdvancedNLPSkill()

# Create a task
task = Task(
    id="nlp-1",
    type="ner",
    description="Extract entities",
    inputs={"text": "Apple Inc. was founded by Steve Jobs in California."}
)

# Execute
result = nlp_skill.execute(task, {})
print(result.output)
```

### Named Entity Recognition

```python
task = Task(
    id="ner-1",
    type="ner",
    inputs={"text": "Victor is an AI system developed by MASSIVEMAGNETICS."}
)
result = nlp_skill.execute(task, {})

# Output structure:
# {
#     "entities": [
#         {"text": "Victor", "label": "PERSON", "start": 0, "end": 6},
#         {"text": "MASSIVEMAGNETICS", "label": "ORG", "start": 45, "end": 61}
#     ],
#     "entity_count": 2,
#     "entity_types": {"PERSON": ["Victor"], "ORG": ["MASSIVEMAGNETICS"]}
# }
```

### Sentiment Analysis

```python
task = Task(
    id="sentiment-1",
    type="sentiment",
    inputs={"text": "This is an amazing AI system! I love it."}
)
result = nlp_skill.execute(task, {})

# Output:
# {
#     "overall_sentiment": "POSITIVE",
#     "confidence": 0.9998,
#     "sentence_sentiments": [...]
# }
```

### Text Summarization

```python
task = Task(
    id="summary-1",
    type="summarization",
    inputs={
        "text": "Long article text...",
        "max_length": 130,
        "min_length": 30
    }
)
result = nlp_skill.execute(task, {})
```

### Keyword Extraction

```python
task = Task(
    id="keywords-1",
    type="keyword_extraction",
    inputs={"text": "Your text here..."}
)
result = nlp_skill.execute(task, {})

# Output:
# {
#     "top_keywords": [
#         {"keyword": "artificial", "frequency": 5},
#         {"keyword": "intelligence", "frequency": 4}
#     ],
#     "noun_chunks": [...],
#     "named_entities": [...]
# }
```

### Full Text Analysis

```python
task = Task(
    id="analysis-1",
    type="nlp",
    inputs={"text": "Your text here..."}
)
result = nlp_skill.execute(task, {})

# Returns comprehensive analysis including:
# - Statistics (word count, sentence count)
# - Named entities
# - Sentiment
# - Keywords
# - Language detection
```

## Architecture

### Models Used

1. **spaCy**: `en_core_web_sm`
   - Size: ~13 MB
   - Capabilities: NER, POS, Dependencies, Lemmatization
   - Speed: ~10,000 words/second

2. **Transformers - Sentiment**: `distilbert-base-uncased-finetuned-sst-2-english`
   - Size: ~255 MB
   - Accuracy: 91.3% on SST-2
   - Speed: ~1000 sentences/second

3. **Transformers - Summarization**: `facebook/bart-large-cnn`
   - Size: ~1.6 GB
   - ROUGE scores: R1: 44.16, R2: 21.28, RL: 40.90
   - Speed: ~100 words/second

### Performance Characteristics

- **Lazy Loading**: Models are loaded on first use to save memory
- **Caching**: Models remain in memory for subsequent requests
- **Batch Processing**: Efficient processing of multiple texts
- **Memory Usage**: ~2-3 GB RAM when all models loaded

### Cost Estimation

The skill provides computational cost estimation based on:
- Text length (characters/tokens)
- Task complexity
- Model requirements

Task complexity multipliers:
- NER: 1.0x
- Sentiment: 1.5x
- Summarization: 3.0x
- POS Tagging: 1.0x
- Dependency Parsing: 1.2x
- Keyword Extraction: 1.0x
- Full Analysis: 2.5x

## Integration with Victor Hub

### Skill Registration

The NLP skill automatically registers with Victor Hub's skill registry:

```python
from victor_hub.skills import AdvancedNLPSkill

# In victor_boot.py
registry = SkillRegistry()
nlp_skill = AdvancedNLPSkill()
registry.register(nlp_skill)
```

### Task Routing

Victor Hub routes tasks to the NLP skill based on task type:

```python
# Task types handled:
- "nlp"
- "ner"
- "sentiment"
- "summarization"
- "pos_tagging"
- "dependency_parsing"
- "text_classification"
- "language_detection"
- "entity_extraction"
- "keyword_extraction"
- "text_analysis"
```

## Testing

Run the test suite:

```bash
python test_nlp_skill.py
```

This will test:
- Named Entity Recognition
- Sentiment Analysis
- Keyword Extraction
- Full NLP Analysis
- Part-of-Speech Tagging

## Security Considerations

1. **Model Security**: Uses patched versions of transformers (>=4.48.0) to avoid deserialization vulnerabilities
2. **PyTorch Security**: Uses torch>=2.6.0 to avoid remote code execution vulnerabilities
3. **Input Validation**: Text inputs are validated and sanitized
4. **Token Limits**: Long texts are truncated to model limits (512 tokens for sentiment)

## Performance Tips

1. **Batch Processing**: Process multiple texts together for better throughput
2. **Model Caching**: Keep the skill instance alive to avoid reloading models
3. **Text Length**: For summarization, optimal text length is 100-1000 words
4. **Memory Management**: Consider unloading models if memory is constrained

## Future Enhancements

Potential additions:
- [ ] Multi-language support (additional spaCy models)
- [ ] Custom entity recognition training
- [ ] Question answering capabilities
- [ ] Text generation
- [ ] Language translation
- [ ] Document classification
- [ ] Relation extraction
- [ ] Coreference resolution

## References

- **spaCy**: https://spacy.io/
- **Hugging Face Transformers**: https://huggingface.co/transformers/
- **BART**: https://arxiv.org/abs/1910.13461
- **DistilBERT**: https://arxiv.org/abs/1910.01108

## License

Part of the Victor Synthetic Super Intelligence Hub  
© 2024 MASSIVE MAGNETICS

---

**Status**: Production Ready ✅  
**Version**: 1.0.0  
**Last Updated**: November 2025
