#!/usr/bin/env python3
"""
Test script for ClipsAI Streamlit Web Interface
"""

import sys
import os
import tempfile
import shutil

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print(f"✅ Streamlit {st.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        import clipsai
        print("✅ ClipsAI imported successfully")
        
        # Test specific ClipsAI components
        from clipsai import Transcriber, ClipFinder, resize, MediaEditor
        print("✅ ClipsAI components imported successfully")
        
    except ImportError as e:
        print(f"❌ Failed to import ClipsAI: {e}")
        print("💡 Make sure you've installed ClipsAI: pip install git+https://github.com/ClipsAI/clipsai.git")
        return False
    
    try:
        import whisperx
        print("✅ WhisperX imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WhisperX: {e}")
        print("💡 Make sure you've installed WhisperX: pip install whisperx@git+https://github.com/m-bain/whisperx.git")
        return False
    
    # Test other dependencies
    required_modules = [
        'tempfile', 'os', 'shutil', 'pathlib', 'logging', 'pandas'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            return False
    
    return True

def test_app_structure():
    """Test that the app.py file has the expected structure"""
    print("\n🔍 Testing app structure...")
    
    if not os.path.exists('app.py'):
        print("❌ app.py not found")
        return False
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    required_functions = [
        'def initialize_session_state',
        'def save_uploaded_file',
        'def transcribe_video',
        'def find_clips',
        'def trim_video',
        'def resize_video',
        'def main'
    ]
    
    for func in required_functions:
        if func in content:
            print(f"✅ Found function: {func}")
        else:
            print(f"❌ Missing function: {func}")
            return False
    
    required_imports = [
        'import streamlit as st',
        'from clipsai import',
        'import tempfile',
        'import os'
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f"✅ Found import: {imp}")
        else:
            print(f"❌ Missing import: {imp}")
            return False
    
    return True

def test_requirements():
    """Test that requirements.txt exists and has necessary packages"""
    print("\n🔍 Testing requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
    
    required_packages = [
        'streamlit',
        'torch',
        'pyannote',
        'opencv-python',
        'pandas'
    ]
    
    for package in required_packages:
        if package in content:
            print(f"✅ Found package in requirements: {package}")
        else:
            print(f"❌ Missing package in requirements: {package}")
            return False
    
    return True

def test_temp_directory_operations():
    """Test temporary directory operations used in the app"""
    print("\n🔍 Testing temporary directory operations...")
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        print(f"✅ Created temporary directory: {temp_dir}")
        
        # Test file operations
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        print("✅ Created test file in temp directory")
        
        # Check file exists
        if os.path.exists(test_file):
            print("✅ File exists in temp directory")
        else:
            print("❌ File not found in temp directory")
            return False
        
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("✅ Cleaned up temporary directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Temporary directory operations failed: {e}")
        return False

def test_streamlit_syntax():
    """Test basic Streamlit syntax by running a simple validation"""
    print("\n🔍 Testing Streamlit syntax...")
    
    try:
        # Try to parse the app.py file for basic Streamlit syntax
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for common Streamlit patterns
        streamlit_patterns = [
            'st.title',
            'st.header',
            'st.sidebar',
            'st.file_uploader',
            'st.button',
            'st.success',
            'st.error',
            'st.spinner'
        ]
        
        for pattern in streamlit_patterns:
            if pattern in content:
                print(f"✅ Found Streamlit pattern: {pattern}")
            else:
                print(f"⚠️  Pattern not found (optional): {pattern}")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit syntax test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 ClipsAI Streamlit Web Interface - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("App Structure Test", test_app_structure),
        ("Requirements Test", test_requirements),
        ("Temp Directory Test", test_temp_directory_operations),
        ("Streamlit Syntax Test", test_streamlit_syntax)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should be ready to run.")
        print("\n🚀 To start the application:")
        print("   streamlit run app.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running the application.")
        print("\n💡 Common solutions:")
        print("   - Run: python install_app.py")
        print("   - Install missing dependencies")
        print("   - Check system requirements (ffmpeg, libmagic)")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)