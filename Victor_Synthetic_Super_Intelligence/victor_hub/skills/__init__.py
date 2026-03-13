"""
Victor Hub Skills Package
Contains all skill implementations for the Victor Hub

Version 2.0.0 - November 2025 Update
New modules added from MASSIVEMAGNETICS repository scan:
- ConsciousnessRiverSkill (conscious-river repo)
- BrainSimulationSkill (brain_ai repo)
- WorldModelHybridSkill (LARGE-LANG-WORLD-HYBRID repo)
- AGICouncilSkill (agi_council repo)
- MusicVideoPipelineSkill (THE-PIPE-LINE repo)
- FlowerOfLifeSkill (project-fol repo)
"""

__version__ = "2.0.0"

# Import all skills for easy registration
from .echo_skill import EchoSkill
from .content_generator import ContentGeneratorSkill
from .research_agent import ResearchAgentSkill
from .nlp_skill import AdvancedNLPSkill
from .intent_skill import IntentSkill

# NEW: November 2025 Skills from repository scan
from .consciousness_skill import ConsciousnessRiverSkill
from .brain_simulation_skill import BrainSimulationSkill
from .world_model_skill import WorldModelHybridSkill
from .agi_council_skill import AGICouncilSkill
from .music_video_skill import MusicVideoPipelineSkill
from .flower_of_life_skill import FlowerOfLifeSkill

__all__ = [
    # Original skills
    "EchoSkill",
    "ContentGeneratorSkill", 
    "ResearchAgentSkill",
    "AdvancedNLPSkill",
    "IntentSkill",
    # NEW: November 2025 Skills
    "ConsciousnessRiverSkill",
    "BrainSimulationSkill",
    "WorldModelHybridSkill",
    "AGICouncilSkill",
    "MusicVideoPipelineSkill",
    "FlowerOfLifeSkill"
]
