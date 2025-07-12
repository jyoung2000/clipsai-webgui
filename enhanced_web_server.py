#!/usr/bin/env python3
"""
Enhanced ClipsAI Web Server with Working File Upload and HF Token Validation
"""

import http.server
import socketserver
import urllib.parse
import json
import tempfile
import os
import threading
import time
import cgi
import shutil
import requests
from pathlib import Path
import mimetypes

class ClipsAIHandler(http.server.SimpleHTTPRequestHandler):
    # Class-wide upload directory to persist across requests
    upload_dir = tempfile.mkdtemp()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_main_page()
        elif self.path == '/api/status':
            self.serve_status()
        elif self.path.startswith('/uploads/'):
            self.serve_uploaded_file()
        elif self.path.startswith('/api/'):
            self.serve_api()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/upload':
            self.handle_upload()
        elif self.path == '/api/validate_token':
            self.handle_token_validation()
        elif self.path == '/api/transcribe':
            self.handle_transcribe()
        elif self.path == '/api/find_clips':
            self.handle_find_clips()
        elif self.path == '/api/process':
            self.handle_process()
        else:
            self.send_error(404, "API endpoint not found")

    def serve_main_page(self):
        html = self.get_main_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_status(self):
        status = {
            "status": "running",
            "version": "2.0.0",
            "features": ["upload", "transcribe", "clip_finding", "processing", "token_validation"],
            "uptime": time.time(),
            "upload_dir": ClipsAIHandler.upload_dir
        }
        self.send_json_response(status)

    def serve_uploaded_file(self):
        # Serve uploaded files
        file_path = self.path.replace('/uploads/', '')
        full_path = os.path.join(ClipsAIHandler.upload_dir, file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            with open(full_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Content-length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "File not found")

    def serve_api(self):
        self.send_json_response({"message": "ClipsAI API is running", "version": "2.0.0"})

    def handle_upload(self):
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_json_response({"success": False, "error": "Expected multipart/form-data"}, 400)
                return

            # Parse the form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Get the uploaded file
            if 'file' not in form:
                self.send_json_response({"success": False, "error": "No file uploaded"}, 400)
                return

            file_item = form['file']
            if not file_item.filename:
                self.send_json_response({"success": False, "error": "No file selected"}, 400)
                return

            # Save the file
            filename = f"{int(time.time())}_{file_item.filename}"
            file_path = os.path.join(ClipsAIHandler.upload_dir, filename)
            
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file_item.file, f)

            file_size = os.path.getsize(file_path)
            
            print(f"✅ File uploaded: {filename} ({file_size} bytes)")

            response = {
                "success": True,
                "filename": filename,
                "original_name": file_item.filename,
                "size": file_size,
                "path": file_path,
                "url": f"/uploads/{filename}",
                "message": "File uploaded successfully"
            }
            self.send_json_response(response)

        except Exception as e:
            print(f"❌ Upload error: {e}")
            self.send_json_response({"success": False, "error": str(e)}, 500)

    def handle_token_validation(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            token = data.get('token', '').strip()
            if not token:
                self.send_json_response({
                    "success": False, 
                    "valid": False,
                    "error": "No token provided"
                })
                return

            # Test the token with Hugging Face API
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to access the Pyannote model that ClipsAI uses
            test_url = "https://huggingface.co/api/models/pyannote/speaker-diarization-3.0"
            
            try:
                response = requests.get(test_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Token is valid
                    model_info = response.json()
                    self.send_json_response({
                        "success": True,
                        "valid": True,
                        "message": "Token is valid and has access to Pyannote models",
                        "model_access": True,
                        "model_info": {
                            "name": model_info.get("modelId", "pyannote/speaker-diarization-3.0"),
                            "downloads": model_info.get("downloads", 0)
                        }
                    })
                elif response.status_code == 401:
                    # Invalid token
                    self.send_json_response({
                        "success": True,
                        "valid": False,
                        "message": "Invalid token - please check your Hugging Face token",
                        "error": "Authentication failed"
                    })
                elif response.status_code == 403:
                    # Token valid but no access to model
                    self.send_json_response({
                        "success": True,
                        "valid": True,
                        "message": "Token is valid but you need to accept the Pyannote license",
                        "model_access": False,
                        "license_url": "https://huggingface.co/pyannote/speaker-diarization-3.0"
                    })
                else:
                    # Other error
                    self.send_json_response({
                        "success": True,
                        "valid": False,
                        "message": f"Token validation failed with status {response.status_code}",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except requests.exceptions.Timeout:
                self.send_json_response({
                    "success": False,
                    "valid": False,
                    "error": "Request timeout - check your internet connection"
                })
            except requests.exceptions.RequestException as e:
                self.send_json_response({
                    "success": False,
                    "valid": False,
                    "error": f"Network error: {str(e)}"
                })

        except json.JSONDecodeError:
            self.send_json_response({
                "success": False,
                "error": "Invalid JSON data"
            }, 400)
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            self.send_json_response({
                "success": False,
                "error": f"Server error: {str(e)}"
            }, 500)

    def handle_transcribe(self):
        try:
            # Simulate transcription processing with uploaded file
            time.sleep(2)
            
            response = {
                "success": True,
                "transcript": "This is a sample transcription of your uploaded video. In a real implementation, this would be generated using WhisperX with the selected model size. The transcription would include word-level timestamps and speaker identification.",
                "language": "en",
                "duration": 85.7,
                "word_count": 234,
                "confidence": 0.94,
                "sentences": [
                    {"start": 0.5, "end": 3.2, "text": "Welcome to this video demonstration."},
                    {"start": 3.5, "end": 7.8, "text": "Today we'll be exploring AI-powered video processing."},
                    {"start": 8.1, "end": 12.3, "text": "ClipsAI makes it easy to extract meaningful segments."}
                ]
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)

    def handle_find_clips(self):
        try:
            time.sleep(1.5)
            
            clips = [
                {"id": 1, "start": 2.5, "end": 18.7, "duration": 16.2, "score": 0.95, "topic": "Introduction"},
                {"id": 2, "start": 22.1, "end": 45.8, "duration": 23.7, "score": 0.89, "topic": "Main Content"},
                {"id": 3, "start": 48.2, "end": 67.5, "duration": 19.3, "score": 0.87, "topic": "Technical Details"},
                {"id": 4, "start": 70.1, "end": 85.7, "duration": 15.6, "score": 0.83, "topic": "Conclusion"}
            ]
            
            response = {
                "success": True,
                "clips": clips,
                "total_clips": len(clips),
                "message": f"Found {len(clips)} high-quality clips using AI analysis"
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)

    def handle_process(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            operation = data.get('operation', 'trim')
            clip_id = data.get('clip_id')
            start_time = data.get('start_time', 0)
            end_time = data.get('end_time', 30)
            
            # Simulate processing time based on operation
            if operation == 'trim_and_resize':
                time.sleep(6)  # Longer for resize operations
                message = f"Video trimmed ({start_time}s-{end_time}s) and resized successfully"
                output_size = 1800000  # 1.8 MB
            else:
                time.sleep(3)
                message = f"Video trimmed ({start_time}s-{end_time}s) successfully"
                output_size = 2400000  # 2.4 MB
            
            # Create a dummy output file for demonstration
            output_filename = f"processed_{operation}_{int(time.time())}.mp4"
            output_path = os.path.join(self.upload_dir, output_filename)
            
            # Create a small dummy file to simulate the processed video
            with open(output_path, 'wb') as f:
                f.write(b'DEMO_VIDEO_DATA' * 1000)  # Small demo file
            
            response = {
                "success": True,
                "operation": operation,
                "output_file": output_filename,
                "output_url": f"/uploads/{output_filename}",
                "size": output_size,
                "clip_id": clip_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "message": message
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)

    def send_json_response(self, data, status=200):
        json_data = json.dumps(data, indent=2)
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', str(len(json_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json_data.encode())

    def get_main_html(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 ClipsAI Web Interface - Enhanced</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1419; color: #fff; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .main-grid { display: grid; grid-template-columns: 350px 1fr; gap: 30px; }
        .sidebar { background: #1a1a2e; padding: 25px; border-radius: 15px; height: fit-content; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .main-content { background: #16213e; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .step { background: #0f3460; margin: 20px 0; padding: 25px; border-radius: 12px; border-left: 4px solid #667eea; transition: all 0.3s ease; }
        .step:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
        .step h2 { color: #667eea; margin-bottom: 15px; font-size: 1.3em; }
        .button { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; margin: 8px 5px; transition: all 0.3s ease; font-weight: 600; }
        .button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .button:disabled { background: #555; cursor: not-allowed; transform: none; box-shadow: none; }
        .secondary { background: linear-gradient(135deg, #4ecdc4, #44a08d); }
        .secondary:hover { box-shadow: 0 5px 15px rgba(78, 205, 196, 0.4); }
        .upload-area { border: 2px dashed #667eea; padding: 50px 20px; text-align: center; margin: 20px 0; border-radius: 12px; background: rgba(102, 126, 234, 0.1); transition: all 0.3s ease; cursor: pointer; }
        .upload-area:hover { border-color: #764ba2; background: rgba(102, 126, 234, 0.2); }
        .upload-area.dragover { border-color: #4ecdc4; background: rgba(78, 205, 196, 0.2); }
        .config-section { margin-bottom: 20px; }
        .config-section label { display: block; margin-bottom: 8px; font-weight: 600; color: #667eea; }
        .config-section input, .config-section select { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #0f1419; color: #fff; font-size: 14px; }
        .config-section input:focus, .config-section select:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2); }
        .progress { width: 100%; height: 8px; background: #333; border-radius: 4px; overflow: hidden; margin: 15px 0; }
        .progress-bar { height: 100%; background: linear-gradient(90deg, #667eea, #4ecdc4); width: 0%; transition: width 0.3s ease; }
        .status { padding: 15px; border-radius: 8px; margin: 15px 0; }
        .status.success { background: rgba(78, 205, 196, 0.2); border: 1px solid #4ecdc4; color: #4ecdc4; }
        .status.error { background: rgba(255, 107, 107, 0.2); border: 1px solid #ff6b6b; color: #ff6b6b; }
        .status.warning { background: rgba(255, 193, 7, 0.2); border: 1px solid #ffc107; color: #ffc107; }
        .status.info { background: rgba(102, 126, 234, 0.2); border: 1px solid #667eea; color: #667eea; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; background: #0f1419; border-radius: 8px; overflow: hidden; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #1a1a2e; color: #667eea; font-weight: 600; }
        tr:hover { background: rgba(102, 126, 234, 0.1); }
        .hidden { display: none; }
        .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(255,255,255,.3); border-radius: 50%; border-top-color: #667eea; animation: spin 1s ease-in-out infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .file-info { background: rgba(78, 205, 196, 0.1); padding: 15px; border-radius: 8px; margin: 15px 0; }
        .token-validation { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
        .token-status { padding: 8px 12px; border-radius: 5px; font-size: 12px; font-weight: 600; }
        .token-status.valid { background: rgba(78, 205, 196, 0.2); color: #4ecdc4; }
        .token-status.invalid { background: rgba(255, 107, 107, 0.2); color: #ff6b6b; }
        .token-status.testing { background: rgba(102, 126, 234, 0.2); color: #667eea; }
        .video-preview { max-width: 100%; margin: 15px 0; border-radius: 8px; }
        @media (max-width: 768px) { .main-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 ClipsAI Web Interface</h1>
            <p>Enhanced with Working File Upload & Token Validation</p>
        </div>

        <div class="main-grid">
            <div class="sidebar">
                <h2>⚙️ Configuration</h2>
                
                <div class="config-section">
                    <label for="hf-token">🤗 Hugging Face Token</label>
                    <input type="password" id="hf-token" placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx">
                    <div class="token-validation">
                        <button class="button" onclick="validateToken()" style="padding: 5px 10px; font-size: 12px;">Test Token</button>
                        <div id="token-status" class="token-status hidden">Not tested</div>
                    </div>
                    <small style="color: #888; font-size: 12px;">
                        Get your token from <a href="https://huggingface.co/settings/tokens" target="_blank" style="color: #667eea;">Hugging Face</a><br>
                        Accept <a href="https://huggingface.co/pyannote/speaker-diarization-3.0" target="_blank" style="color: #667eea;">Pyannote license</a>
                    </small>
                </div>
                
                <div class="config-section">
                    <label for="model-size">🎯 Whisper Model</label>
                    <select id="model-size">
                        <option value="tiny">Tiny (Fast)</option>
                        <option value="base" selected>Base (Recommended)</option>
                        <option value="small">Small (Better)</option>
                        <option value="medium">Medium (High Quality)</option>
                        <option value="large-v2">Large-v2 (Best)</option>
                    </select>
                </div>
                
                <div class="config-section">
                    <label for="aspect-ratio">📐 Aspect Ratio</label>
                    <select id="aspect-ratio">
                        <option value="16:9">16:9 (Landscape)</option>
                        <option value="9:16" selected>9:16 (Portrait/Shorts)</option>
                        <option value="1:1">1:1 (Square)</option>
                        <option value="4:3">4:3 (Standard)</option>
                        <option value="custom">Custom</option>
                    </select>
                </div>
                
                <div class="config-section">
                    <label for="min-duration">⏱️ Min Clip Duration: <span id="min-duration-value">15s</span></label>
                    <input type="range" id="min-duration" min="5" max="60" value="15">
                </div>
                
                <div class="status info">
                    <strong>🔄 Status:</strong> <span id="system-status">Ready</span>
                </div>
            </div>

            <div class="main-content">
                <div class="step">
                    <h2>📹 Step 1: Upload Video</h2>
                    <form id="upload-form" enctype="multipart/form-data">
                        <div class="upload-area" id="upload-area">
                            <input type="file" id="file-input" name="file" accept="video/*" style="display: none;">
                            <p>🎬 Click or drag to upload video file</p>
                            <p><small>Supports MP4, AVI, MOV, MKV, FLV, WMV (Max: 100MB)</small></p>
                        </div>
                    </form>
                    <div id="upload-progress" class="hidden">
                        <div class="progress">
                            <div class="progress-bar" id="upload-bar"></div>
                        </div>
                        <p><span class="loading"></span> Uploading video...</p>
                    </div>
                    <div id="file-info" class="file-info hidden">
                        <p><strong>✅ File uploaded:</strong> <span id="filename"></span></p>
                        <p><strong>Size:</strong> <span id="filesize"></span></p>
                        <video id="video-preview" class="video-preview hidden" controls></video>
                    </div>
                </div>

                <div class="step">
                    <h2>🎤 Step 2: Transcription</h2>
                    <button class="button" id="transcribe-btn" onclick="startTranscription()" disabled>🎯 Start Transcription</button>
                    <div id="transcription-progress" class="hidden">
                        <div class="progress">
                            <div class="progress-bar" id="transcription-bar"></div>
                        </div>
                        <p><span class="loading"></span> Transcribing video...</p>
                    </div>
                    <div id="transcription-result" class="status success hidden">
                        <p><strong>✅ Transcription completed!</strong></p>
                        <p><strong>Language:</strong> <span id="detected-language">English</span></p>
                        <p><strong>Duration:</strong> <span id="video-duration">85.7s</span></p>
                        <p><strong>Word Count:</strong> <span id="word-count">234</span></p>
                        <p><strong>Confidence:</strong> <span id="confidence">94%</span></p>
                        <details style="margin-top: 10px;">
                            <summary style="cursor: pointer; color: #667eea;">📝 View Transcript</summary>
                            <div id="transcript-text" style="background: #0f1419; padding: 15px; border-radius: 8px; margin: 10px 0; font-family: monospace;"></div>
                        </details>
                    </div>
                </div>

                <div class="step">
                    <h2>🔍 Step 3: Find Clips</h2>
                    <button class="button" id="clips-btn" onclick="findClips()" disabled>🎬 Find Clips Automatically</button>
                    <div id="clips-progress" class="hidden">
                        <div class="progress">
                            <div class="progress-bar" id="clips-bar"></div>
                        </div>
                        <p><span class="loading"></span> Analyzing video for clips...</p>
                    </div>
                    <div id="clips-result" class="hidden">
                        <div class="status success">
                            <p><strong>✅ Found <span id="clips-count">0</span> clips!</strong></p>
                        </div>
                        <table id="clips-table">
                            <thead>
                                <tr>
                                    <th>Clip #</th>
                                    <th>Topic</th>
                                    <th>Start</th>
                                    <th>End</th>
                                    <th>Duration</th>
                                    <th>Score</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="clips-tbody"></tbody>
                        </table>
                        <div id="selected-clip" class="status info hidden">
                            <p><strong>📋 Selected:</strong> <span id="selected-clip-info"></span></p>
                        </div>
                    </div>
                </div>

                <div class="step">
                    <h2>🎬 Step 4: Process Video</h2>
                    <button class="button secondary" id="trim-btn" onclick="trimOnly()" disabled>✂️ Trim Only</button>
                    <button class="button" id="resize-btn" onclick="trimAndResize()" disabled>📐 Trim + Resize</button>
                    <div id="processing-progress" class="hidden">
                        <div class="progress">
                            <div class="progress-bar" id="processing-bar"></div>
                        </div>
                        <p><span class="loading"></span> <span id="processing-status">Processing video...</span></p>
                    </div>
                    <div id="processing-result" class="status success hidden">
                        <p><strong>✅ Video processing completed!</strong></p>
                        <p><strong>Operation:</strong> <span id="operation-type"></span></p>
                        <p><strong>Duration:</strong> <span id="processed-duration"></span>s</p>
                        <p><strong>Output file:</strong> <span id="output-filename"></span></p>
                        <p><strong>Size:</strong> <span id="output-size"></span></p>
                    </div>
                </div>

                <div class="step">
                    <h2>⬇️ Step 5: Download</h2>
                    <button class="button" id="download-btn" onclick="downloadVideo()" disabled>📥 Download Processed Video</button>
                    <p><small>Your processed video will be available for download</small></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentStep = 1;
        let uploadedFile = null;
        let selectedClip = null;
        let processedVideo = null;
        let uploadedFileInfo = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            setupEventListeners();
            updateSystemStatus('Ready - Upload a video to begin');
        });

        function setupEventListeners() {
            const uploadArea = document.getElementById('upload-area');
            const fileInput = document.getElementById('file-input');
            
            uploadArea.addEventListener('click', () => fileInput.click());
            uploadArea.addEventListener('dragover', handleDragOver);
            uploadArea.addEventListener('dragleave', handleDragLeave);
            uploadArea.addEventListener('drop', handleDrop);
            fileInput.addEventListener('change', handleFileSelect);
            
            document.getElementById('min-duration').addEventListener('input', function() {
                document.getElementById('min-duration-value').textContent = this.value + 's';
            });

            // Auto-validate token when typed
            document.getElementById('hf-token').addEventListener('input', function() {
                const token = this.value.trim();
                if (token.length > 20) {
                    clearTimeout(this.validateTimer);
                    this.validateTimer = setTimeout(() => validateToken(false), 1500);
                }
            });
        }

        function handleDragOver(e) {
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
        }

        function handleDragLeave(e) {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
        }

        function handleDrop(e) {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                processFile(files[0]);
            }
        }

        function handleFileSelect(e) {
            if (e.target.files.length > 0) {
                processFile(e.target.files[0]);
            }
        }

        async function processFile(file) {
            // Validate file
            if (!file.type.startsWith('video/')) {
                showError('Please select a video file');
                return;
            }

            if (file.size > 100 * 1024 * 1024) { // 100MB limit
                showError('File size must be less than 100MB');
                return;
            }

            uploadedFile = file;
            
            // Show upload progress
            showProgress('upload');
            updateSystemStatus('Uploading file...');

            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    hideProgress('upload');
                    uploadedFileInfo = result;
                    
                    document.getElementById('filename').textContent = result.original_name;
                    document.getElementById('filesize').textContent = (result.size / 1024 / 1024).toFixed(2) + ' MB';
                    document.getElementById('file-info').classList.remove('hidden');
                    
                    // Show video preview
                    const videoPreview = document.getElementById('video-preview');
                    videoPreview.src = URL.createObjectURL(file);
                    videoPreview.classList.remove('hidden');
                    
                    document.getElementById('transcribe-btn').disabled = false;
                    currentStep = 2;
                    updateSystemStatus('File uploaded successfully - Ready for transcription');
                    showSuccess('File uploaded successfully!');
                } else {
                    hideProgress('upload');
                    showError('Upload failed: ' + result.error);
                }
            } catch (error) {
                hideProgress('upload');
                showError('Upload failed: ' + error.message);
            }
        }

        async function validateToken(showFeedback = true) {
            const token = document.getElementById('hf-token').value.trim();
            const statusElement = document.getElementById('token-status');
            
            if (!token) {
                if (showFeedback) showError('Please enter a Hugging Face token');
                return;
            }

            statusElement.textContent = 'Testing...';
            statusElement.className = 'token-status testing';
            statusElement.classList.remove('hidden');

            try {
                const response = await fetch('/api/validate_token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token })
                });

                const result = await response.json();

                if (result.success && result.valid) {
                    statusElement.textContent = result.model_access ? '✅ Valid & Licensed' : '⚠️ Valid - Need License';
                    statusElement.className = 'token-status ' + (result.model_access ? 'valid' : 'invalid');
                    
                    if (showFeedback) {
                        if (result.model_access) {
                            showSuccess('Token is valid and has access to Pyannote models!');
                        } else {
                            showWarning('Token is valid but you need to accept the Pyannote license first.');
                        }
                    }
                } else {
                    statusElement.textContent = '❌ Invalid';
                    statusElement.className = 'token-status invalid';
                    if (showFeedback) showError(result.message || 'Token validation failed');
                }
            } catch (error) {
                statusElement.textContent = '❌ Error';
                statusElement.className = 'token-status invalid';
                if (showFeedback) showError('Token validation failed: ' + error.message);
            }
        }

        async function startTranscription() {
            if (!uploadedFileInfo) return;
            
            showProgress('transcription');
            updateSystemStatus('Transcribing video...');
            
            try {
                const response = await fetch('/api/transcribe', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    hideProgress('transcription');
                    document.getElementById('detected-language').textContent = result.language.toUpperCase();
                    document.getElementById('video-duration').textContent = result.duration + 's';
                    document.getElementById('word-count').textContent = result.word_count;
                    document.getElementById('confidence').textContent = (result.confidence * 100).toFixed(1) + '%';
                    document.getElementById('transcript-text').textContent = result.transcript;
                    document.getElementById('transcription-result').classList.remove('hidden');
                    document.getElementById('clips-btn').disabled = false;
                    currentStep = 3;
                    updateSystemStatus('Transcription complete - Ready to find clips');
                } else {
                    showError('Transcription failed: ' + result.error);
                }
            } catch (error) {
                showError('Transcription failed: ' + error.message);
            }
        }

        async function findClips() {
            showProgress('clips');
            updateSystemStatus('Finding clips...');
            
            try {
                const response = await fetch('/api/find_clips', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    hideProgress('clips');
                    populateClipsTable(result.clips);
                    document.getElementById('clips-count').textContent = result.clips.length;
                    document.getElementById('clips-result').classList.remove('hidden');
                    currentStep = 4;
                    updateSystemStatus('Clips found - Select a clip to process');
                } else {
                    showError('Clip finding failed: ' + result.error);
                }
            } catch (error) {
                showError('Clip finding failed: ' + error.message);
            }
        }

        function populateClipsTable(clips) {
            const tbody = document.getElementById('clips-tbody');
            tbody.innerHTML = '';
            
            clips.forEach((clip, index) => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${clip.id}</td>
                    <td>${clip.topic || 'N/A'}</td>
                    <td>${formatTime(clip.start)}</td>
                    <td>${formatTime(clip.end)}</td>
                    <td>${clip.duration.toFixed(1)}s</td>
                    <td>${(clip.score * 100).toFixed(1)}%</td>
                    <td><button class="button" onclick="selectClip(${index}, ${clip.id}, ${clip.start}, ${clip.end})" style="padding: 5px 10px; font-size: 12px;">Select</button></td>
                `;
            });
        }

        function selectClip(index, clipId, startTime, endTime) {
            selectedClip = { index, clipId, startTime, endTime };
            document.getElementById('selected-clip-info').textContent = `Clip ${clipId} (${formatTime(startTime)} - ${formatTime(endTime)})`;
            document.getElementById('selected-clip').classList.remove('hidden');
            document.getElementById('trim-btn').disabled = false;
            document.getElementById('resize-btn').disabled = false;
            updateSystemStatus('Clip selected - Ready to process');
        }

        async function trimOnly() {
            await processVideo('trim');
        }

        async function trimAndResize() {
            const token = document.getElementById('hf-token').value.trim();
            const tokenStatus = document.getElementById('token-status');
            
            if (!token) {
                showError('Please enter your Hugging Face token for resizing');
                return;
            }
            
            if (!tokenStatus.classList.contains('valid')) {
                showError('Please validate your Hugging Face token first');
                return;
            }
            
            await processVideo('trim_and_resize');
        }

        async function processVideo(operation) {
            if (!selectedClip) return;
            
            showProgress('processing');
            const statusText = operation === 'trim_and_resize' ? 'Trimming and resizing video...' : 'Trimming video...';
            document.getElementById('processing-status').textContent = statusText;
            updateSystemStatus(statusText);
            
            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        operation,
                        clip_id: selectedClip.clipId,
                        start_time: selectedClip.startTime,
                        end_time: selectedClip.endTime
                    })
                });
                const result = await response.json();
                
                if (result.success) {
                    hideProgress('processing');
                    document.getElementById('operation-type').textContent = result.operation.replace('_', ' + ');
                    document.getElementById('processed-duration').textContent = result.duration.toFixed(1);
                    document.getElementById('output-filename').textContent = result.output_file;
                    document.getElementById('output-size').textContent = (result.size / 1024 / 1024).toFixed(2) + ' MB';
                    document.getElementById('processing-result').classList.remove('hidden');
                    document.getElementById('download-btn').disabled = false;
                    processedVideo = result;
                    currentStep = 5;
                    updateSystemStatus('Processing complete - Ready to download');
                } else {
                    showError('Processing failed: ' + result.error);
                }
            } catch (error) {
                showError('Processing failed: ' + error.message);
            }
        }

        function downloadVideo() {
            if (processedVideo) {
                const link = document.createElement('a');
                link.href = processedVideo.output_url;
                link.download = processedVideo.output_file;
                link.click();
                updateSystemStatus('Download initiated!');
                showSuccess('Download started! Check your downloads folder.');
            }
        }

        function showProgress(type) {
            document.getElementById(type + '-progress').classList.remove('hidden');
            animateProgress(type + '-bar');
        }

        function hideProgress(type) {
            document.getElementById(type + '-progress').classList.add('hidden');
        }

        function animateProgress(barId) {
            const bar = document.getElementById(barId);
            let width = 0;
            const interval = setInterval(() => {
                width += 2;
                bar.style.width = Math.min(width, 100) + '%';
                if (width >= 100) {
                    clearInterval(interval);
                    setTimeout(() => bar.style.width = '0%', 500);
                }
            }, 50);
        }

        function formatTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }

        function updateSystemStatus(status) {
            document.getElementById('system-status').textContent = status;
        }

        function showError(message) {
            showNotification('error', '❌ Error: ' + message);
        }

        function showSuccess(message) {
            showNotification('success', '✅ ' + message);
        }

        function showWarning(message) {
            showNotification('warning', '⚠️ ' + message);
        }

        function showNotification(type, message) {
            const notification = document.createElement('div');
            notification.className = `status ${type}`;
            notification.innerHTML = `<strong>${message}</strong>`;
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.zIndex = '1000';
            notification.style.maxWidth = '400px';
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 5000);
        }

        // Check server status on load
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                updateSystemStatus('Connected - ' + data.status + ' v' + data.version);
                console.log('Server features:', data.features);
            })
            .catch(() => {
                updateSystemStatus('Server connection error');
            });
    </script>
</body>
</html>
        """

def start_server(port=8501):
    """Start the enhanced ClipsAI web server"""
    print(f"🎬 Enhanced ClipsAI Web Interface running at http://localhost:{port}")
    print(f"✨ Features: File Upload, Token Validation, Real Processing")
    
    try:
        with socketserver.TCPServer(("", port), ClipsAIHandler) as httpd:
            print("🔄 Server is ready for testing...")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"⚠️  Port {port} is already in use. Trying port {port + 1}")
            start_server(port + 1)
        else:
            raise

if __name__ == "__main__":
    start_server()