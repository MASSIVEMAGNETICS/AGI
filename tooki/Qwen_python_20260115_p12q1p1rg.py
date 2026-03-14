"""
Image-to-Video Generator: Continuous Evolution from Input Image
"""
import torch
import numpy as np
from typing import Tuple, List, Dict, Any
from PIL import Image

class ImageToVideoGenerator:
    """Generates continuous video from input image using morpho-temporal dynamics"""
    
    def __init__(self, grid_size: Tuple[int, int] = (16, 16), device: str = 'cpu'):
        self.grid_size = grid_size
        self.device = torch.device(device)
        self.temporal_engine = None  # Will be initialized with first call
        
    def initialize_temporal(self, seed: Optional[int] = None):
        """Initialize temporal engine"""
        if self.temporal_engine is None:
            from src.hart_morphosis.core.temporal_engine import MorphoTemporalDynamics
            self.temporal_engine = MorphoTemporalDynamics(grid_size=self.grid_size, device=self.device)
            if seed is not None:
                np.random.seed(seed)
                torch.manual_seed(seed)
    
    def load_image(self, image_path: str) -> torch.Tensor:
        """Load and preprocess image"""
        img = Image.open(image_path).convert('RGB')
        img = img.resize((self.grid_size[1], self.grid_size[0]), Image.LANCZOS)
        img_tensor = torch.from_numpy(np.array(img)).float() / 255.0
        return img_tensor.permute(2, 0, 1)  # [C, H, W]
    
    def encode_image(self, img_tensor: torch.Tensor) -> torch.Tensor:
        """Encode image into morphogenetic state"""
        # Simple encoding: use RGB channels as morphogen concentrations
        # A = R, B = G, C = B (for simplicity)
        morphogen_A = img_tensor[0]  # Red channel
        morphogen_B = img_tensor[1]  # Green channel
        
        # Create state dictionary
        state = {
            'A': morphogen_A.unsqueeze(0).unsqueeze(0),  # [1, 1, H, W]
            'B': morphogen_B.unsqueeze(0).unsqueeze(0),  # [1, 1, H, W]
        }
        
        return state
    
    def generate_video_from_image(self, image_path: str, num_frames: int = 30, fps: int = 30, seed: Optional[int] = None) -> List[torch.Tensor]:
        """Generate video from input image"""
        self.initialize_temporal(seed)
        
        # Load and encode image
        img_tensor = self.load_image(image_path)
        initial_state = self.encode_image(img_tensor)
        
        # Generate video frames
        video_frames = []
        
        # Use temporal morphogenesis to evolve the image
        for frame in range(num_frames):
            # Apply reaction-diffusion step
            next_state = self.temporal_engine.temporal_morpho.morpho_engine.reaction_diffusion_step(initial_state)
            initial_state = next_state
            
            # Extract current frame
            frame_data = next_state['A'].squeeze().cpu().detach()
            video_frames.append(frame_data)
            
        return video_frames

# Example usage
if __name__ == "__main__":
    generator = ImageToVideoGenerator(grid_size=(16, 16))
    video = generator.generate_video_from_image("input_image.png", num_frames=10, fps=5, seed=42)
    print(f"Generated {len(video)} frames from input image")
    print(f"First frame shape: {video[0].shape}")