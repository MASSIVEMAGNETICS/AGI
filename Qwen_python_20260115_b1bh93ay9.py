"""
Image-to-Video Generation Demo
"""
from src.hart_morphosis.core.image2video import Image2VideoGenerator

# Initialize image-to-video generator
generator = Image2VideoGenerator(frame_size=(64, 64), fps=12, duration=3.0)

# Generate video from input image
print("Generating continuous video from input image...")
frames = generator.generate_hart_refined_video("examples/input_image.png", seed=42)
generator.save_video(frames, "continuous_video.gif", zoom_level=2)

print("Done! Check the generated .gif file.")