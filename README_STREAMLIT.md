# ClipsAI Streamlit Web Interface

A comprehensive web interface for the [ClipsAI](https://github.com/ClipsAI/clipsai) video processing library, built with Streamlit.

## 🚀 Features

- **Video Upload**: Support for MP4, AVI, MOV, MKV, FLV, WMV formats
- **Transcription**: Automatic speech-to-text using WhisperX
- **Clip Finding**: AI-powered identification of interesting video segments
- **Speaker Diarization**: Identify different speakers using Pyannote
- **Video Trimming**: Extract specific segments from videos
- **Video Resizing**: Convert videos to different aspect ratios (16:9, 9:16, 1:1, etc.)
- **Download**: Export processed videos

## 📋 Prerequisites

### System Dependencies

1. **Python 3.9+**
2. **FFmpeg**: Required for video processing
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/
   ```

3. **libmagic**: Required for file type detection
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libmagic1
   
   # macOS
   brew install libmagic
   ```

### Hugging Face Token

You'll need a Hugging Face access token for speaker diarization and video resizing:

1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new token
3. Accept the [Pyannote license](https://huggingface.co/pyannote/speaker-diarization-3.0)

## 🛠️ Installation

### Option 1: Automatic Setup (Recommended)

```bash
# Clone or download this repository
git clone <repository-url>
cd clipsai-streamlit

# Run the setup script
python install_app.py
```

### Option 2: Manual Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install WhisperX
pip install whisperx@git+https://github.com/m-bain/whisperx.git

# Install ClipsAI
pip install git+https://github.com/ClipsAI/clipsai.git
```

## 🎬 Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and go to `http://localhost:8501`

3. **Configure settings** in the sidebar:
   - Enter your Hugging Face token
   - Select Whisper model size
   - Adjust clip duration settings
   - Choose target aspect ratio

4. **Process your video**:
   - Upload a video file
   - Start transcription
   - Find clips automatically or select manually
   - Trim and/or resize the video
   - Download the processed result

## 📖 Step-by-Step Guide

### Step 1: Upload Video
- Click "Choose a video file" and select your video
- Supported formats: MP4, AVI, MOV, MKV, FLV, WMV
- The video will be displayed for preview

### Step 2: Transcription
- Click "Start Transcription" to generate text from audio
- Choose model size (larger = more accurate but slower)
- View the transcript and language detection results

### Step 3: Find Clips
- Click "Find Clips Automatically" to detect interesting segments
- Or use manual selection with start/end times
- Review the suggested clips in the table

### Step 4: Process Video
- **Trim Only**: Extract the selected segment
- **Trim + Resize**: Extract and convert to target aspect ratio
- Processing may take several minutes depending on video length

### Step 5: Download
- Preview the processed video
- Download the final result

## ⚙️ Configuration Options

### Model Settings
- **Whisper Model Size**: tiny, base, small, medium, large-v2
  - `tiny`: Fastest, least accurate
  - `large-v2`: Slowest, most accurate

### Clip Settings
- **Minimum Duration**: 5-60 seconds
- **Maximum Duration**: 60-1800 seconds (30 minutes)

### Aspect Ratios
- **16:9**: Standard landscape (YouTube, TV)
- **9:16**: Portrait mode (TikTok, Instagram Stories)
- **1:1**: Square (Instagram posts)
- **4:3**: Traditional TV format
- **Custom**: Define your own ratio

## 🔧 Troubleshooting

### Common Issues

1. **"ClipsAI is not installed"**
   - Run the installation commands again
   - Check that all dependencies installed successfully

2. **"ffmpeg not found"**
   - Install ffmpeg using the system-specific commands above
   - Restart your terminal/command prompt

3. **"Transcription failed"**
   - Check that your video has audio
   - Try a smaller model size
   - Ensure the video file isn't corrupted

4. **"Video resizing failed"**
   - Verify your Hugging Face token is correct
   - Ensure you've accepted the Pyannote license
   - Check your internet connection

5. **"Memory error"**
   - Try a smaller video file
   - Use a smaller Whisper model
   - Close other applications to free up RAM

### Performance Tips

- **Use GPU acceleration**: If you have a CUDA-compatible GPU, the models will automatically use it
- **Choose appropriate model size**: Balance between speed and accuracy
- **Shorter videos process faster**: Consider trimming long videos before processing
- **Close other applications**: Free up system resources for better performance

## 📊 Model Information

### Whisper Models
| Model | Size | VRAM | Speed | Accuracy |
|-------|------|------|--------|----------|
| tiny | 39 MB | ~1 GB | Fastest | Lower |
| base | 74 MB | ~1 GB | Fast | Good |
| small | 244 MB | ~2 GB | Medium | Better |
| medium | 769 MB | ~5 GB | Slow | High |
| large-v2 | 1550 MB | ~10 GB | Slowest | Highest |

## 🔒 Privacy & Security

- **Local Processing**: All video processing happens on your machine
- **Temporary Files**: Videos are stored temporarily and cleaned up automatically
- **Token Security**: Hugging Face tokens are entered securely and not stored
- **No Data Upload**: Your videos never leave your computer

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🆘 Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: [ClipsAI Official Docs](https://clipsai.com)
- **Community**: Join the discussion on GitHub

## 🔗 Related Projects

- [ClipsAI](https://github.com/ClipsAI/clipsai) - The core library
- [WhisperX](https://github.com/m-bain/whisperx) - Enhanced Whisper with word timestamps
- [Pyannote](https://github.com/pyannote/pyannote-audio) - Speaker diarization
- [Streamlit](https://streamlit.io/) - Web app framework

---

**Made with ❤️ using Streamlit and ClipsAI**