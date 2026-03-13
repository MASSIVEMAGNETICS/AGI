# Add these imports
from src.hart_morphosis.core.sono_morphosis import SonoMorphosis
from src.hart_morphosis.core.morpho_temporal import MorphoTemporalDynamics
from src.hart_morphosis.core.image2video import Image2VideoGenerator

# Add tabs for audio and video
tab1, tab2, tab3 = st.tabs(["Image Generation", "Audio Generation", "Video Generation"])

with tab1:
    # Existing image generation code
    pass

with tab2:
    st.header("🎵 Audio Generation")
    audio_prompt = st.text_input("Enter audio prompt:", "heartbeat in space")
    audio_duration = st.slider("Duration (seconds):", 1, 10, 3)
    audio_generate_btn = st.button("Generate Audio", key="audio_btn")
    
    if audio_generate_btn:
        with st.spinner("Generating audio..."):
            sono = SonoMorphosis(duration=audio_duration)
            audio = sono.synthesize_audio(audio_prompt, seed=42)
            sono.save_audio(audio, "generated_audio.wav")
            
            st.audio("generated_audio.wav")
            st.download_button(
                label="Download Audio",
                data=open("generated_audio.wav", "rb").read(),
                file_name="generated_audio.wav",
                mime="audio/wav"
            )

with tab3:
    st.header("🎬 Video Generation")
    video_type = st.radio("Video Type:", ["Growing Pattern", "Image-to-Video"])
    
    if video_type == "Growing Pattern":
        video_prompt = st.text_input("Enter video prompt:", "growing tree")
        video_duration = st.slider("Duration (seconds):", 1, 10, 3)
        video_generate_btn = st.button("Generate Video", key="video_btn")
        
        if video_generate_btn:
            with st.spinner("Generating video..."):
                temporal = MorphoTemporalDynamics(frame_size=(64, 64), fps=12, duration=video_duration)
                frames = temporal.generate_video(video_prompt, seed=42)
                temporal.save_video(frames, "generated_video.gif", zoom_level=2)
                
                st.image("generated_video.gif", caption="Generated Video", use_column_width=True)
                st.download_button(
                    label="Download Video",
                    data=open("generated_video.gif", "rb").read(),
                    file_name="generated_video.gif",
                    mime="image/gif"
                )
    else:  # Image-to-Video
        uploaded_file = st.file_uploader("Upload an image:", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            # Save uploaded file
            with open("uploaded_image.png", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            video_duration = st.slider("Duration (seconds):", 1, 10, 3)
            video_generate_btn = st.button("Generate Video from Image", key="img2vid_btn")
            
            if video_generate_btn:
                with st.spinner("Generating video from image..."):
                    generator = Image2VideoGenerator(frame_size=(64, 64), fps=12, duration=video_duration)
                    frames = generator.generate_hart_refined_video("uploaded_image.png", seed=42)
                    generator.save_video(frames, "img2vid_output.gif", zoom_level=2)
                    
                    st.image("img2vid_output.gif", caption="Generated Video", use_column_width=True)
                    st.download_button(
                        label="Download Video",
                        data=open("img2vid_output.gif", "rb").read(),
                        file_name="img2vid_output.gif",
                        mime="image/gif"
                    )