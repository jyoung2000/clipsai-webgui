import streamlit as st
import tempfile
import os
import shutil
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import ClipsAI components
try:
    from clipsai import Transcriber, ClipFinder, resize, MediaEditor, Clip
    from clipsai.transcribe.transcription import Transcription
    from clipsai.media.video_file import VideoFile
    CLIPSAI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ClipsAI not available: {e}")
    CLIPSAI_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="ClipsAI Web Interface",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'uploaded_video' not in st.session_state:
        st.session_state.uploaded_video = None
    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
    if 'transcription' not in st.session_state:
        st.session_state.transcription = None
    if 'clips' not in st.session_state:
        st.session_state.clips = []
    if 'selected_clip' not in st.session_state:
        st.session_state.selected_clip = None
    if 'processed_video_path' not in st.session_state:
        st.session_state.processed_video_path = None
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()

def cleanup_temp_files():
    """Clean up temporary files"""
    if 'temp_dir' in st.session_state and os.path.exists(st.session_state.temp_dir):
        shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)

def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temporary directory"""
    if uploaded_file is not None:
        temp_path = os.path.join(st.session_state.temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return temp_path
    return None

def transcribe_video(video_path: str, model_size: str = "base") -> Optional[Transcription]:
    """Transcribe video using ClipsAI Transcriber"""
    if not CLIPSAI_AVAILABLE:
        st.error("ClipsAI is not installed. Please install dependencies.")
        return None
    
    try:
        with st.spinner("Transcribing video... This may take a few minutes."):
            transcriber = Transcriber(model_size=model_size)
            transcription = transcriber.transcribe(video_path)
            return transcription
    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        logger.error(f"Transcription error: {e}")
        return None

def find_clips(transcription: Transcription, min_duration: int = 15, max_duration: int = 900) -> List[Clip]:
    """Find clips using ClipsAI ClipFinder"""
    if not CLIPSAI_AVAILABLE:
        st.error("ClipsAI is not installed. Please install dependencies.")
        return []
    
    try:
        with st.spinner("Finding clips in the video..."):
            clipfinder = ClipFinder(
                min_clip_duration=min_duration,
                max_clip_duration=max_duration
            )
            clips = clipfinder.find_clips(transcription)
            return clips
    except Exception as e:
        st.error(f"Clip finding failed: {str(e)}")
        logger.error(f"Clip finding error: {e}")
        return []

def trim_video(video_path: str, start_time: float, end_time: float, output_path: str) -> Optional[str]:
    """Trim video using ClipsAI MediaEditor"""
    if not CLIPSAI_AVAILABLE:
        st.error("ClipsAI is not installed. Please install dependencies.")
        return None
    
    try:
        with st.spinner("Trimming video..."):
            editor = MediaEditor()
            video_file = VideoFile(video_path)
            trimmed_video = editor.trim(
                media_file=video_file,
                start_time=start_time,
                end_time=end_time,
                trimmed_media_file_path=output_path
            )
            return trimmed_video.path if trimmed_video else None
    except Exception as e:
        st.error(f"Video trimming failed: {str(e)}")
        logger.error(f"Video trimming error: {e}")
        return None

def resize_video(video_path: str, hf_token: str, aspect_ratio: tuple, output_path: str) -> Optional[str]:
    """Resize video using ClipsAI resize function"""
    if not CLIPSAI_AVAILABLE:
        st.error("ClipsAI is not installed. Please install dependencies.")
        return None
    
    if not hf_token:
        st.error("Hugging Face token is required for video resizing.")
        return None
    
    try:
        with st.spinner("Resizing video... This may take several minutes."):
            crops = resize(
                video_file_path=video_path,
                pyannote_auth_token=hf_token,
                aspect_ratio=aspect_ratio
            )
            
            # Apply the crops to create resized video
            editor = MediaEditor()
            video_file = VideoFile(video_path)
            
            # Use the resize functionality to create the final video
            resized_video = editor.resize_video(
                original_video_file=video_file,
                resized_video_file_path=output_path,
                width=aspect_ratio[0] * 100,  # Scale appropriately
                height=aspect_ratio[1] * 100,
                segments=crops.segments
            )
            
            return resized_video.path if resized_video else None
    except Exception as e:
        st.error(f"Video resizing failed: {str(e)}")
        logger.error(f"Video resizing error: {e}")
        return None

def display_clip_info(clips: List[Clip]) -> pd.DataFrame:
    """Display clips information in a table"""
    if not clips:
        return pd.DataFrame()
    
    clip_data = []
    for i, clip in enumerate(clips):
        clip_data.append({
            'Clip #': i + 1,
            'Start Time (s)': f"{clip.start_time:.2f}",
            'End Time (s)': f"{clip.end_time:.2f}",
            'Duration (s)': f"{clip.end_time - clip.start_time:.2f}",
            'Start Char': clip.start_char,
            'End Char': clip.end_char
        })
    
    return pd.DataFrame(clip_data)

def format_time(seconds: float) -> str:
    """Format seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Title and description
    st.title("🎬 ClipsAI Web Interface")
    st.markdown("""
    Welcome to the ClipsAI Web Interface! This tool allows you to:
    - Upload videos and transcribe them using WhisperX
    - Find interesting clips automatically using AI
    - Perform speaker diarization
    - Trim and resize videos to different aspect ratios
    - Download processed videos
    """)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Hugging Face token input
    st.sidebar.markdown("### 🤗 Hugging Face Token")
    st.sidebar.markdown("""
    Required for speaker diarization and video resizing.
    Get your token from [Hugging Face](https://huggingface.co/settings/tokens)
    """)
    hf_token = st.sidebar.text_input(
        "Hugging Face Token",
        type="password",
        help="Required for Pyannote speaker diarization"
    )
    
    # Model configuration
    st.sidebar.markdown("### 🎯 Model Settings")
    model_size = st.sidebar.selectbox(
        "Whisper Model Size",
        ["tiny", "base", "small", "medium", "large-v2"],
        index=1,
        help="Larger models are more accurate but slower"
    )
    
    # Clip settings
    st.sidebar.markdown("### ✂️ Clip Settings")
    min_clip_duration = st.sidebar.slider(
        "Minimum Clip Duration (seconds)",
        min_value=5,
        max_value=60,
        value=15,
        help="Minimum length for automatically found clips"
    )
    
    max_clip_duration = st.sidebar.slider(
        "Maximum Clip Duration (seconds)",
        min_value=60,
        max_value=1800,
        value=900,
        help="Maximum length for automatically found clips"
    )
    
    # Aspect ratio settings
    st.sidebar.markdown("### 📐 Aspect Ratio")
    aspect_ratio_option = st.sidebar.selectbox(
        "Target Aspect Ratio",
        ["16:9 (Landscape)", "9:16 (Portrait/Shorts)", "1:1 (Square)", "4:3 (Standard)", "Custom"],
        index=1
    )
    
    aspect_ratios = {
        "16:9 (Landscape)": (16, 9),
        "9:16 (Portrait/Shorts)": (9, 16),
        "1:1 (Square)": (1, 1),
        "4:3 (Standard)": (4, 3),
    }
    
    if aspect_ratio_option == "Custom":
        col1, col2 = st.sidebar.columns(2)
        custom_width = col1.number_input("Width", min_value=1, value=9)
        custom_height = col2.number_input("Height", min_value=1, value=16)
        selected_aspect_ratio = (custom_width, custom_height)
    else:
        selected_aspect_ratio = aspect_ratios[aspect_ratio_option]
    
    # Main content area
    # Step 1: Video Upload
    st.header("📹 Step 1: Upload Video")
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'],
        help="Upload a video file to process with ClipsAI"
    )
    
    if uploaded_file is not None:
        if st.session_state.uploaded_video != uploaded_file.name:
            # New file uploaded, reset session state
            st.session_state.uploaded_video = uploaded_file.name
            st.session_state.video_path = save_uploaded_file(uploaded_file)
            st.session_state.transcription = None
            st.session_state.clips = []
            st.session_state.selected_clip = None
            st.session_state.processed_video_path = None
        
        st.success(f"✅ Video uploaded: {uploaded_file.name}")
        
        # Display video
        try:
            st.video(st.session_state.video_path)
        except Exception as e:
            st.warning(f"Could not display video preview: {e}")
        
        # Show file info
        file_size = len(uploaded_file.getbuffer()) / 1024 / 1024  # MB
        st.info(f"File size: {file_size:.2f} MB")
        
        # Step 2: Transcription
        st.header("🎤 Step 2: Transcription")
        
        if not CLIPSAI_AVAILABLE:
            st.error("❌ ClipsAI is not installed. Please install the required dependencies.")
            st.code("""
# Install ClipsAI and dependencies
pip install -r requirements.txt
pip install whisperx@git+https://github.com/m-bain/whisperx.git
pip install git+https://github.com/ClipsAI/clipsai.git

# Install system dependencies
# Ubuntu/Debian: apt-get install ffmpeg libmagic1
# macOS: brew install ffmpeg libmagic
# Windows: See installation instructions in requirements.txt
            """)
            return
        
        if st.button("🎯 Start Transcription", type="primary"):
            st.session_state.transcription = transcribe_video(st.session_state.video_path, model_size)
        
        if st.session_state.transcription:
            st.success("✅ Transcription completed!")
            
            # Display transcription
            with st.expander("📝 View Full Transcript", expanded=False):
                transcript_text = ""
                for sentence_info in st.session_state.transcription.get_sentence_info():
                    transcript_text += sentence_info['sentence'] + " "
                st.text_area("Transcript", transcript_text, height=200)
            
            # Show transcription stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration", f"{st.session_state.transcription.end_time:.1f}s")
            with col2:
                st.metric("Language", st.session_state.transcription.language.upper())
            with col3:
                word_count = len([w for w in transcript_text.split() if w])
                st.metric("Word Count", word_count)
            
            # Step 3: Find Clips
            st.header("🔍 Step 3: Find Clips")
            
            if st.button("🎬 Find Clips Automatically", type="primary"):
                st.session_state.clips = find_clips(
                    st.session_state.transcription,
                    min_clip_duration,
                    max_clip_duration
                )
            
            if st.session_state.clips:
                st.success(f"✅ Found {len(st.session_state.clips)} clips!")
                
                # Display clips table
                clips_df = display_clip_info(st.session_state.clips)
                st.dataframe(clips_df, use_container_width=True)
                
                # Clip selection
                st.subheader("📋 Select a Clip")
                clip_options = [f"Clip {i+1}: {format_time(clip.start_time)} - {format_time(clip.end_time)}" 
                              for i, clip in enumerate(st.session_state.clips)]
                
                selected_clip_idx = st.selectbox(
                    "Choose a clip to process",
                    range(len(clip_options)),
                    format_func=lambda x: clip_options[x]
                )
                
                if selected_clip_idx is not None:
                    st.session_state.selected_clip = st.session_state.clips[selected_clip_idx]
                    
                    # Show selected clip info
                    clip = st.session_state.selected_clip
                    st.info(f"""
                    **Selected Clip:**
                    - Duration: {clip.end_time - clip.start_time:.1f} seconds
                    - Start: {format_time(clip.start_time)}
                    - End: {format_time(clip.end_time)}
                    """)
            
            # Step 4: Manual Clip Selection (Alternative)
            st.header("✂️ Step 4: Manual Clip Selection (Optional)")
            st.markdown("Alternatively, you can manually specify start and end times:")
            
            col1, col2 = st.columns(2)
            with col1:
                manual_start = st.number_input(
                    "Start Time (seconds)",
                    min_value=0.0,
                    max_value=float(st.session_state.transcription.end_time),
                    value=0.0,
                    step=0.1
                )
            with col2:
                manual_end = st.number_input(
                    "End Time (seconds)",
                    min_value=manual_start,
                    max_value=float(st.session_state.transcription.end_time),
                    value=min(manual_start + 30, float(st.session_state.transcription.end_time)),
                    step=0.1
                )
            
            use_manual_selection = st.checkbox("Use manual selection instead of auto-found clips")
            
            # Step 5: Process Video
            st.header("🎬 Step 5: Process Video")
            
            if st.session_state.selected_clip or use_manual_selection:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✂️ Trim Only", type="secondary"):
                        if use_manual_selection:
                            start_time, end_time = manual_start, manual_end
                        else:
                            start_time = st.session_state.selected_clip.start_time
                            end_time = st.session_state.selected_clip.end_time
                        
                        output_path = os.path.join(st.session_state.temp_dir, "trimmed_video.mp4")
                        st.session_state.processed_video_path = trim_video(
                            st.session_state.video_path,
                            start_time,
                            end_time,
                            output_path
                        )
                
                with col2:
                    if st.button("📐 Trim + Resize", type="primary"):
                        if not hf_token:
                            st.error("Please provide a Hugging Face token for resizing.")
                        else:
                            if use_manual_selection:
                                start_time, end_time = manual_start, manual_end
                                # First trim the video
                                trimmed_path = os.path.join(st.session_state.temp_dir, "temp_trimmed.mp4")
                                trimmed_video_path = trim_video(
                                    st.session_state.video_path,
                                    start_time,
                                    end_time,
                                    trimmed_path
                                )
                                if trimmed_video_path:
                                    video_to_resize = trimmed_video_path
                                else:
                                    st.error("Failed to trim video")
                                    video_to_resize = None
                            else:
                                clip = st.session_state.selected_clip
                                # First trim the video
                                trimmed_path = os.path.join(st.session_state.temp_dir, "temp_trimmed.mp4")
                                trimmed_video_path = trim_video(
                                    st.session_state.video_path,
                                    clip.start_time,
                                    clip.end_time,
                                    trimmed_path
                                )
                                if trimmed_video_path:
                                    video_to_resize = trimmed_video_path
                                else:
                                    st.error("Failed to trim video")
                                    video_to_resize = None
                            
                            if video_to_resize:
                                output_path = os.path.join(st.session_state.temp_dir, "resized_video.mp4")
                                st.session_state.processed_video_path = resize_video(
                                    video_to_resize,
                                    hf_token,
                                    selected_aspect_ratio,
                                    output_path
                                )
                
                # Step 6: Download
                if st.session_state.processed_video_path:
                    st.header("⬇️ Step 6: Download Processed Video")
                    
                    if os.path.exists(st.session_state.processed_video_path):
                        st.success("✅ Video processing completed!")
                        
                        # Show processed video
                        try:
                            st.video(st.session_state.processed_video_path)
                        except Exception as e:
                            st.warning(f"Could not display processed video: {e}")
                        
                        # Download button
                        with open(st.session_state.processed_video_path, "rb") as file:
                            file_data = file.read()
                            
                        filename = f"processed_{uploaded_file.name}"
                        st.download_button(
                            label="📥 Download Processed Video",
                            data=file_data,
                            file_name=filename,
                            mime="video/mp4",
                            type="primary"
                        )
                        
                        # Show file size
                        file_size = len(file_data) / 1024 / 1024  # MB
                        st.info(f"Processed file size: {file_size:.2f} MB")
                    else:
                        st.error("❌ Processed video file not found.")
    else:
        st.info("👆 Please upload a video file to get started.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Built with ❤️ using <a href='https://streamlit.io/'>Streamlit</a> and <a href='https://github.com/ClipsAI/clipsai'>ClipsAI</a></p>
        <p><strong>Note:</strong> This application requires ffmpeg and libmagic to be installed on your system.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    finally:
        # Cleanup on app termination
        cleanup_temp_files()