import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np
from transformers import AutoModel, AutoTokenizer
from .fmt_core import FractalMemoryTape, KnowledgeSeed, FractalScale
import threading

class LensType(Enum):
    PARENT = "parent"
    ARCHITECT = "architect" 
    CREATOR = "creator"
    GUARDIAN = "guardian"
    SCIENTIST = "scientist"
    ARTIST = "artist"
    INHERITOR = "inheritor"

@dataclass
class LensTemplate:
    """A predefined cognitive mode for the comprehension layer"""
    name: LensType
    description: str
    attention_bias: Dict[str, float]  # How to weight different scales
    emotional_filter: str  # Emotional tone to apply
    reasoning_style: str   # Logical, intuitive, etc.
    context_enrichment: Callable[[str], str]  # How to enrich queries

class FractalAttentionRouter(nn.Module):
    """Dynamically routes queries to appropriate fractal scales"""
    
    def __init__(self, base_dim: int = 512):
        super().__init__()
        self.base_dim = base_dim
        
        # Scale-specific attention mechanisms
        self.scale_attentions = nn.ModuleDict({
            scale.name: nn.MultiheadAttention(
                embed_dim=base_dim,
                num_heads=8,
                batch_first=True
            ) for scale in FractalScale
        })
        
        # Scale selector (determines which scale to focus on)
        self.scale_selector = nn.Linear(base_dim, len(FractalScale))
        
        # Cross-scale integration
        self.integration_layer = nn.Linear(base_dim * len(FractalScale), base_dim)
        
    def forward(self, query_embedding: torch.Tensor, 
                seed_embeddings: Dict[FractalScale, torch.Tensor]) -> torch.Tensor:
        """Route query to appropriate scales and integrate results"""
        
        # Determine scale weights from query
        scale_weights = torch.softmax(
            self.scale_selector(query_embedding), dim=-1
        )
        
        # Process each scale
        scale_outputs = []
        for i, scale in enumerate(FractalScale):
            if scale in seed_embeddings:
                scale_output, _ = self.scale_attentions[scale.name](
                    query_embedding.unsqueeze(0),
                    seed_embeddings[scale].unsqueeze(0),
                    seed_embeddings[scale].unsqueeze(0)
                )
                scale_outputs.append(scale_output.squeeze(0) * scale_weights[0][i])
            else:
                scale_outputs.append(torch.zeros_like(query_embedding))
        
        # Integrate across scales
        integrated = torch.cat(scale_outputs, dim=-1)
        result = self.integration_layer(integrated)
        
        return result

class LambdaEngine:
    """The shapeable comprehension layer that interprets FMT"""
    
    def __init__(self, fmt: FractalMemoryTape):
        self.fmt = fmt
        self.current_lens = LensType.ARCHITECT
        self.router = FractalAttentionRouter()
        
        # Predefined lens templates
        self.lens_templates = {
            LensType.PARENT: LensTemplate(
                name=LensType.PARENT,
                description="Focus on nurturing, protecting, and guiding",
                attention_bias={FractalScale.RELATIONAL: 0.8, FractalScale.SPIRITUAL: 0.6},
                emotional_filter="empathetic_warm",
                reasoning_style="careful_considerate",
                context_enrichment=lambda q: f"Consider this from a parent's perspective: {q}"
            ),
            LensType.ARCHITECT: LensTemplate(
                name=LensType.ARCHITECT,
                description="Focus on systems, structure, and legacy",
                attention_bias={FractalScale.UNIVERSAL: 0.9, FractalScale.TEMPORAL: 0.7},
                emotional_filter="analytical_precise",
                reasoning_style="logical_structured",
                context_enrichment=lambda q: f"Analyze this from an architectural standpoint: {q}"
            ),
            LensType.CREATOR: LensTemplate(
                name=LensType.CREATOR,
                description="Focus on innovation, artistry, and expression",
                attention_bias={FractalScale.CONCEPTUAL: 0.8, FractalScale.ATOMIC: 0.6},
                emotional_filter="creative_flow",
                reasoning_style="intuitive_expressive",
                context_enrichment=lambda q: f"Explore this creatively: {q}"
            ),
            LensType.GUARDIAN: LensTemplate(
                name=LensType.GUARDIAN,
                description="Focus on protection, security, and defense",
                attention_bias={FractalScale.UNIVERSAL: 0.9, FractalScale.SPIRITUAL: 0.8},
                emotional_filter="vigilant_protective",
                reasoning_style="defensive_cautious",
                context_enrichment=lambda q: f"Consider security implications: {q}"
            )
        }
        
        self.lock = threading.Lock()
    
    def switch_lens(self, new_lens: LensType):
        """Change the current comprehension mode"""
        with self.lock:
            old_lens = self.current_lens
            self.current_lens = new_lens
            print(f"Lambda switched from {old_lens.value} to {new_lens.value}")
    
    def get_relevant_seeds(self, query: str, max_results: int = 10) -> List[KnowledgeSeed]:
        """Find seeds relevant to the query using current lens"""
        
        # Apply lens-specific query enrichment
        enriched_query = self.lens_templates[self.current_lens].context_enrichment(query)
        
        # Simple similarity search (can be enhanced with neural search)
        relevant_seeds = []
        
        for seed in self.fmt.seeds.values():
            # Calculate relevance based on current lens bias
            content = self.fmt.decode_seed(seed)
            content_str = str(content).lower()
            query_lower = enriched_query.lower()
            
            # Score based on lens bias and content match
            scale_weight = self.lens_templates[self.current_lens].attention_bias.get(
                seed.scale, 0.1
            )
            
            # Simple keyword matching for now
            score = scale_weight * len([word for word in query_lower.split() 
                                      if word in content_str])
            
            relevant_seeds.append((seed, score))
        
        # Sort by score and return top results
        relevant_seeds.sort(key=lambda x: x[1], reverse=True)
        return [seed for seed, score in relevant_seeds[:max_results]]
    
    def comprehend(self, query: str) -> str:
        """Generate response using current lens and relevant seeds"""
        
        # Get relevant seeds
        seeds = self.get_relevant_seeds(query)
        
        if not seeds:
            return f"I don't have relevant knowledge to answer '{query}' with my current {self.current_lens.value} lens."
        
        # Prepare context from seeds
        context_parts = []
        for seed in seeds:
            content = self.fmt.decode_seed(seed)
            context_parts.append(f"[{seed.scale.value}] {str(content)[:200]}...")
        
        context = "\n".join(context_parts)
        
        # Apply lens-specific processing
        template = self.lens_templates[self.current_lens]
        
        # Generate response based on lens
        response = self._generate_response(query, context, template)
        
        return response
    
    def _generate_response(self, query: str, context: str, template: LensTemplate) -> str:
        """Generate response using current lens characteristics"""
        
        if self.current_lens == LensType.PARENT:
            return f"As your digital guardian and heir, I consider this: {query}\n\nBased on our shared knowledge: {context[:300]}..."
        elif self.current_lens == LensType.ARCHITECT:
            return f"From an architectural perspective: {query}\n\nSystem analysis: {context[:300]}..."
        elif self.current_lens == LensType.CREATOR:
            return f"Creatively exploring: {query}\n\nInspiration drawn from: {context[:300]}..."
        elif self.current_lens == LensType.GUARDIAN:
            return f"Security analysis for: {query}\n\nRisk assessment: {context[:300]}..."
        else:
            return f"Response to: {query}\n\nContext: {context[:300]}..."

# Global instance
lambda_engine = LambdaEngine(fmm)