#!/usr/bin/env python3
"""
Setup script for ClipsAI Streamlit Web Interface
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def check_system_dependencies():
    """Check if system dependencies are installed"""
    print("🔍 Checking system dependencies...")
    
    # Check ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ ffmpeg is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg not found. Please install ffmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        return False
    
    # Check Python version
    if sys.version_info < (3, 9):
        print(f"❌ Python 3.9+ required. Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version}")
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    commands = [
        ("pip install -r requirements.txt", "Installing basic Python dependencies"),
        ("pip install whisperx@git+https://github.com/m-bain/whisperx.git", "Installing WhisperX"),
        ("pip install git+https://github.com/ClipsAI/clipsai.git", "Installing ClipsAI")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def test_installation():
    """Test if the installation was successful"""
    print("\n🧪 Testing installation...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} installed")
    except ImportError:
        print("❌ Streamlit not installed")
        return False
    
    try:
        import clipsai
        print("✅ ClipsAI installed")
    except ImportError:
        print("❌ ClipsAI not installed")
        return False
    
    try:
        import whisperx
        print("✅ WhisperX installed")
    except ImportError:
        print("❌ WhisperX not installed")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 ClipsAI Streamlit Web Interface Setup")
    print("=" * 50)
    
    # Check system dependencies
    if not check_system_dependencies():
        print("\n❌ Please install system dependencies before continuing.")
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Failed to install Python dependencies.")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n🎬 To run the application:")
    print("   streamlit run app.py")
    print("\n📖 Make sure to:")
    print("   1. Get a Hugging Face token from https://huggingface.co/settings/tokens")
    print("   2. Accept the Pyannote license at https://huggingface.co/pyannote/speaker-diarization-3.0")
    print("   3. Upload a video file to start processing")

if __name__ == "__main__":
    main()