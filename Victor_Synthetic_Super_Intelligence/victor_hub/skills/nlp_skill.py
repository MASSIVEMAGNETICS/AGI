"""
Advanced NLP Skill
Provides state-of-the-art Natural Language Processing capabilities including:
- Named Entity Recognition (NER)
- Sentiment Analysis
- Text Summarization
- Part-of-Speech Tagging
- Dependency Parsing
- Text Classification
- Language Detection
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from victor_hub.victor_boot import Skill, Task, Result

logger = logging.getLogger("NLPSkill")


class AdvancedNLPSkill(Skill):
    """Advanced NLP skill with state-of-the-art capabilities"""
    
    def __init__(self):
        super().__init__(
            name="advanced_nlp",
            repo="VictorSpacy",
            capabilities=[
                "nlp",
                "ner",
                "sentiment",
                "summarization",
                "pos_tagging",
                "dependency_parsing",
                "text_classification",
                "language_detection",
                "entity_extraction",
                "keyword_extraction",
                "text_analysis"
            ]
        )
        
        self._spacy_model = None
        self._sentiment_model = None
        self._summarization_model = None
        self._models_loaded = False
        
    def _load_models(self):
        """Lazy load NLP models to save memory"""
        if self._models_loaded:
            return
            
        try:
            import spacy
            
            logger.info("Loading NLP models...")
            
            # Load spaCy model for linguistic analysis
            try:
                self._spacy_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("Downloading spaCy model en_core_web_sm...")
                import subprocess
                subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                             check=True, capture_output=True)
                self._spacy_model = spacy.load("en_core_web_sm")
            
            # Try to load transformers models (optional for advanced features)
            try:
                from transformers import pipeline
                
                # Load sentiment analysis model
                self._sentiment_model = pipeline("sentiment-analysis", 
                                               model="distilbert-base-uncased-finetuned-sst-2-english")
                
                # Load summarization model (using a smaller model for efficiency)
                self._summarization_model = pipeline("summarization", 
                                                    model="facebook/bart-large-cnn")
                logger.info("Transformer models loaded successfully")
            except (ImportError, Exception) as e:
                logger.warning(f"Transformers not available: {e}. Using spaCy-only features.")
                self._sentiment_model = None
                self._summarization_model = None
            
            self._models_loaded = True
            logger.info("NLP models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            raise
    
    def execute(self, task: Task, context: dict) -> Result:
        """Execute NLP task based on type"""
        
        # Load models if needed
        self._load_models()
        
        task_type = task.type
        text = task.inputs.get("text", task.description)
        
        try:
            if task_type == "ner" or task_type == "entity_extraction":
                output = self._extract_entities(text)
            elif task_type == "sentiment":
                output = self._analyze_sentiment(text)
            elif task_type == "summarization":
                output = self._summarize_text(text, task.inputs)
            elif task_type == "pos_tagging":
                output = self._pos_tagging(text)
            elif task_type == "dependency_parsing":
                output = self._dependency_parsing(text)
            elif task_type == "language_detection":
                output = self._detect_language(text)
            elif task_type == "keyword_extraction":
                output = self._extract_keywords(text)
            elif task_type in ["nlp", "text_analysis"]:
                output = self._full_analysis(text)
            else:
                output = self._full_analysis(text)
            
            return Result(
                task_id=task.id,
                status="success",
                output=output,
                metadata={
                    "skill": self.name,
                    "task_type": task_type,
                    "text_length": len(text),
                    "models_used": self._get_models_used(task_type)
                }
            )
            
        except Exception as e:
            logger.error(f"NLP task failed: {e}")
            return Result(
                task_id=task.id,
                status="failed",
                error=str(e),
                metadata={"skill": self.name, "task_type": task_type}
            )
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        doc = self._spacy_model(text)
        
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "description": spacy.explain(ent.label_)
            })
        
        # Group by entity type
        entity_types = {}
        for ent in entities:
            label = ent["label"]
            if label not in entity_types:
                entity_types[label] = []
            entity_types[label].append(ent["text"])
        
        return {
            "entities": entities,
            "entity_count": len(entities),
            "entity_types": entity_types,
            "unique_entities": len(set(e["text"] for e in entities))
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        
        # Check if transformers model is available
        if self._sentiment_model is None:
            # Fallback: Use simple rule-based sentiment
            doc = self._spacy_model(text)
            
            # Simple heuristic: count positive vs negative words
            positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                            'love', 'best', 'perfect', 'awesome', 'brilliant', 'outstanding'}
            negative_words = {'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 
                            'poor', 'disappointing', 'fail', 'failed', 'disaster'}
            
            pos_count = sum(1 for token in doc if token.text.lower() in positive_words)
            neg_count = sum(1 for token in doc if token.text.lower() in negative_words)
            
            if pos_count > neg_count:
                sentiment = "POSITIVE"
                confidence = min(0.6 + (pos_count - neg_count) * 0.1, 0.95)
            elif neg_count > pos_count:
                sentiment = "NEGATIVE"
                confidence = min(0.6 + (neg_count - pos_count) * 0.1, 0.95)
            else:
                sentiment = "NEUTRAL"
                confidence = 0.5
            
            return {
                "overall_sentiment": sentiment,
                "confidence": confidence,
                "sentence_sentiments": [],
                "sentence_count": len(list(doc.sents)),
                "method": "rule-based (transformers not available)"
            }
        
        # Use transformers for deep sentiment analysis
        result = self._sentiment_model(text[:512])[0]  # Limit to 512 tokens
        
        # Also get sentence-level sentiment
        doc = self._spacy_model(text)
        sentence_sentiments = []
        for sent in doc.sents:
            sent_result = self._sentiment_model(sent.text[:512])[0]
            sentence_sentiments.append({
                "text": sent.text,
                "sentiment": sent_result["label"],
                "confidence": sent_result["score"]
            })
        
        return {
            "overall_sentiment": result["label"],
            "confidence": result["score"],
            "sentence_sentiments": sentence_sentiments,
            "sentence_count": len(sentence_sentiments),
            "method": "transformer-based"
        }
    
    def _summarize_text(self, text: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize text"""
        max_length = inputs.get("max_length", 130)
        min_length = inputs.get("min_length", 30)
        
        # Only summarize if text is long enough
        if len(text.split()) < min_length:
            return {
                "summary": text,
                "original_length": len(text.split()),
                "summary_length": len(text.split()),
                "compression_ratio": 1.0,
                "method": "text too short, no summarization needed"
            }
        
        # Check if transformers model is available
        if self._summarization_model is None:
            # Fallback: Extract first few sentences as summary
            doc = self._spacy_model(text)
            sentences = list(doc.sents)
            
            # Take first 2-3 sentences
            summary_sents = sentences[:min(3, len(sentences))]
            summary = " ".join([sent.text for sent in summary_sents])
            
            return {
                "summary": summary,
                "original_length": len(text.split()),
                "summary_length": len(summary.split()),
                "compression_ratio": len(summary.split()) / len(text.split()),
                "method": "extractive (transformers not available)"
            }
        
        # Use transformers for abstractive summarization
        result = self._summarization_model(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )[0]
        
        summary = result["summary_text"]
        
        return {
            "summary": summary,
            "original_length": len(text.split()),
            "summary_length": len(summary.split()),
            "compression_ratio": len(summary.split()) / len(text.split()),
            "method": "abstractive (transformer-based)"
        }
    
    def _pos_tagging(self, text: str) -> Dict[str, Any]:
        """Part-of-speech tagging"""
        doc = self._spacy_model(text)
        
        tokens = []
        pos_counts = {}
        
        for token in doc:
            tokens.append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "tag": token.tag_,
                "dep": token.dep_,
                "description": spacy.explain(token.pos_)
            })
            
            pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1
        
        return {
            "tokens": tokens,
            "token_count": len(tokens),
            "pos_distribution": pos_counts
        }
    
    def _dependency_parsing(self, text: str) -> Dict[str, Any]:
        """Parse dependency tree"""
        doc = self._spacy_model(text)
        
        dependencies = []
        for token in doc:
            dependencies.append({
                "text": token.text,
                "dep": token.dep_,
                "head": token.head.text,
                "children": [child.text for child in token.children],
                "description": spacy.explain(token.dep_)
            })
        
        return {
            "dependencies": dependencies,
            "sentence_count": len(list(doc.sents))
        }
    
    def _detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text"""
        doc = self._spacy_model(text)
        
        return {
            "language": "en",  # spaCy model is English-specific
            "confidence": 0.95,  # High confidence since we're using en model
            "note": "Using English model - for multi-language detection, install langdetect"
        }
    
    def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """Extract keywords using noun chunks and entities"""
        doc = self._spacy_model(text)
        
        # Extract noun chunks
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        
        # Extract named entities
        entities = [ent.text for ent in doc.ents]
        
        # Get most common nouns and proper nouns
        keywords = []
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                keywords.append(token.lemma_.lower())
        
        # Count frequencies
        from collections import Counter
        keyword_freq = Counter(keywords)
        
        return {
            "top_keywords": [{"keyword": k, "frequency": v} 
                           for k, v in keyword_freq.most_common(10)],
            "noun_chunks": list(set(noun_chunks)),
            "named_entities": list(set(entities)),
            "total_keywords": len(keyword_freq)
        }
    
    def _full_analysis(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive NLP analysis"""
        doc = self._spacy_model(text)
        
        # Get all analyses
        analysis = {
            "text": text,
            "statistics": {
                "character_count": len(text),
                "word_count": len([token for token in doc if not token.is_space]),
                "sentence_count": len(list(doc.sents)),
                "token_count": len(doc)
            },
            "entities": self._extract_entities(text),
            "sentiment": self._analyze_sentiment(text),
            "keywords": self._extract_keywords(text),
            "language": self._detect_language(text)
        }
        
        return analysis
    
    def _get_models_used(self, task_type: str) -> List[str]:
        """Get list of models used for task type"""
        models = ["spacy:en_core_web_sm"]
        
        if task_type in ["sentiment", "text_analysis", "nlp"]:
            models.append("transformers:distilbert-sentiment")
        
        if task_type == "summarization":
            models.append("transformers:bart-summarization")
        
        return models
    
    def estimate_cost(self, task: Task) -> float:
        """Estimate computational cost"""
        text_length = len(task.inputs.get("text", task.description))
        
        # Base cost on text length and task complexity
        base_cost = text_length / 1000
        
        # Different tasks have different computational costs
        task_multipliers = {
            "ner": 1.0,
            "sentiment": 1.5,
            "summarization": 3.0,  # Most expensive
            "pos_tagging": 1.0,
            "dependency_parsing": 1.2,
            "language_detection": 0.5,
            "keyword_extraction": 1.0,
            "nlp": 2.5,  # Full analysis
            "text_analysis": 2.5
        }
        
        multiplier = task_multipliers.get(task.type, 1.0)
        return base_cost * multiplier


# Import spacy at module level for explain function
try:
    import spacy
except ImportError:
    logger.warning("spaCy not installed. NLP skill will not function until dependencies are installed.")
