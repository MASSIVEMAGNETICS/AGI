"""
Generate video using Morpho-Temporal Dynamics
"""
import argparse
import torch
from src.hart_morphosis.core.temporal_engine import MorphoTemporalDynamics
from src.hart_morphosis.core.video_renderer import FractalVideoRenderer

def parse_args():
    parser = argparse.ArgumentParser(description='Generate video with Morpho-Temporal Dynamics')
    parser.add_argument('--prompt', type=str, required=True, help='Text prompt for video generation')
    parser.add_argument('--output', type=str, default='output.mp4', help='Output filename')
    parser.add_argument('--frames', type=int, default=30, help='Number of frames')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second')
    parser.add_argument('--zoom', type=int, default=2, help='Zoom level')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    return parser.parse_args()

def main():
    args = parse_args()
    
    print(f"Generating video for prompt: '{args.prompt}' ({args.frames} frames at {args.fps} fps)")
    
    # Initialize components
    engine = MorphoTemporalDynamics(grid_size=(16, 16))
    renderer = FractalVideoRenderer(base_resolution=(16, 16))
    
    # Generate video frames
    video_frames = engine.generate_video(
        prompt=args.prompt, 
        num_frames=args.frames, 
        fps=args.fps, 
        seed=args.seed
    )
    
    # Render at requested zoom level
    rendered_frames = renderer.render_video(video_frames, zoom_level=args.zoom, fps=args.fps)
    
    # Save result
    renderer.save_video(rendered_frames, args.output, fps=args.fps)
    print(f"Saved result to {args.output}")

if __name__ == '__main__':
    main()