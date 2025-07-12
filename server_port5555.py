#!/usr/bin/env python3
"""
ClipsAI Web Server - Port 5555 Version
Configured for Docker deployment with proper permissions
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
import sys

# Get port from environment variable or default to 5555
PORT = int(os.environ.get('PORT', '5555'))

class ClipsAIHandler(http.server.SimpleHTTPRequestHandler):
    # Use environment variable for upload directory or create temp
    upload_dir = os.environ.get('UPLOAD_DIR', tempfile.mkdtemp())
    
    @classmethod
    def initialize_upload_dir(cls):
        """Initialize upload directory if it doesn't exist"""
        os.makedirs(cls.upload_dir, exist_ok=True)
        print(f"📁 Upload directory initialized: {cls.upload_dir}")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_main_page()
        elif self.path == '/api/status':
            self.serve_status()
        elif self.path == '/api/health':
            self.serve_health()
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

    def serve_health(self):
        """Health check endpoint for Docker"""
        health = {
            "status": "healthy",
            "timestamp": time.time(),
            "upload_dir": os.path.exists(self.upload_dir),
            "port": PORT
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health).encode())

    def serve_main_page(self):
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 ClipsAI Web GUI</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f1419;
            color: #e1e8ed;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 40px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .token-section {{
            background: #1a1f29;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }}
        
        .token-input-group {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }}
        
        .token-input {{
            flex: 1;
            padding: 12px;
            background: #253341;
            border: 2px solid #364152;
            border-radius: 8px;
            color: #e1e8ed;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        
        .token-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .button {{
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .button:disabled {{
            background: #364152;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }}
        
        .button.secondary {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .main-content {{
            display: grid;
            gap: 30px;
        }}
        
        .step {{
            background: #1a1f29;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }}
        
        .step h2 {{
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        .upload-section {{
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .upload-area {{
            flex: 1;
            min-width: 300px;
            border: 3px dashed #364152;
            border-radius: 12px;
            padding: 60px 20px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            background: #253341;
        }}
        
        .upload-area:hover, .upload-area.drag-over {{
            border-color: #667eea;
            background: #2a3847;
            transform: scale(1.02);
        }}
        
        .upload-area p {{
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        
        .upload-button-area {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: center;
        }}
        
        .upload-button {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 15px 30px;
            font-size: 18px;
        }}
        
        .file-info {{
            background: #253341;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}
        
        .file-info p {{
            margin: 5px 0;
        }}
        
        .progress {{
            background: #364152;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .progress-bar {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            width: 0%;
            transition: width 0.3s;
            border-radius: 15px;
        }}
        
        .status {{
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .status.success {{
            background: #1a3a2e;
            border: 1px solid #22543d;
        }}
        
        .status.error {{
            background: #3a1a1a;
            border: 1px solid #543d22;
        }}
        
        .status.info {{
            background: #1a2a3a;
            border: 1px solid #22343d;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #364152;
        }}
        
        th {{
            background: #253341;
            font-weight: 600;
            color: #667eea;
        }}
        
        tr:hover {{
            background: #253341;
        }}
        
        .hidden {{
            display: none;
        }}
        
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #364152;
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .token-status {{
            margin-top: 10px;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
        }}
        
        .token-status.valid {{
            background: #1a3a2e;
            color: #68d391;
            border: 1px solid #22543d;
        }}
        
        .token-status.invalid {{
            background: #3a1a1a;
            color: #fc8181;
            border: 1px solid #742a2a;
        }}
        
        input[type="file"] {{
            display: none;
        }}
        
        .status-indicator {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            display: inline-block;
            margin-left: 10px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        
        .status-indicator.loading {{
            background: #667eea;
            animation: pulse 1.5s ease-in-out infinite alternate;
        }}
        
        .status-indicator.valid {{
            background: #68d391;
            border-color: #22543d;
            box-shadow: 0 0 10px rgba(104, 211, 145, 0.3);
        }}
        
        .status-indicator.invalid {{
            background: #fc8181;
            border-color: #742a2a;
            box-shadow: 0 0 10px rgba(252, 129, 129, 0.3);
        }}
        
        .status-indicator.hidden {{
            display: none;
        }}
        
        @keyframes pulse {{
            from {{ opacity: 0.5; }}
            to {{ opacity: 1; }}
        }}
        
        .token-input-with-status {{
            display: flex;
            align-items: center;
            position: relative;
        }}
        
        .token-input-with-status .token-input {{
            flex: 1;
            padding-right: 40px;
        }}
        
        .token-status-circle {{
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 ClipsAI Web GUI</h1>
            <p>AI-Powered Video Transcription, Clip Finding & Intelligent Resizing</p>
            <p style="font-size: 0.9em; opacity: 0.7;">Running on port {PORT}</p>
        </div>
        
        <div class="token-section">
            <h2>🔑 Hugging Face Token Configuration</h2>
            <p style="margin-bottom: 15px; opacity: 0.8;">Required for speaker diarization and advanced features</p>
            
            <div style="background: #1a2a3a; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #667eea;">
                <h4 style="margin: 0 0 8px 0; color: #667eea;">📋 Token Requirements:</h4>
                <ul style="margin: 0; padding-left: 20px; font-size: 14px; opacity: 0.9;">
                    <li><strong>Read access</strong> to repositories (required)</li>
                    <li>Must be a <strong>User Access Token</strong> (not Organization)</li>
                    <li>Token should start with <code>hf_</code></li>
                    <li>Required for <strong>pyannote/speaker-diarization-3.1</strong> model</li>
                    <li>Generate at: <a href="https://huggingface.co/settings/tokens" target="_blank" style="color: #667eea;">huggingface.co/settings/tokens</a></li>
                </ul>
                <p style="margin: 8px 0 0 0; font-size: 13px; opacity: 0.7;">💡 <strong>Tip:</strong> Create a new token if validation fails, even with existing permissions.</p>
            </div>
            <div class="token-input-group">
                <div class="token-input-with-status">
                    <input type="text" 
                           id="hf-token" 
                           class="token-input" 
                           placeholder="Enter your Hugging Face API token (hf_...)"
                           autocomplete="off">
                    <div id="token-status-circle" class="status-indicator hidden token-status-circle"></div>
                </div>
                <button class="button" id="validate-token-btn">✓ Validate Token</button>
            </div>
            <div id="token-status" class="token-status hidden"></div>
        </div>
        
        <div class="main-content">
            <div class="workflow">
                <div class="step">
                    <h2>📤 Step 1: Upload Video</h2>
                    <div class="upload-section">
                        <div class="upload-area" id="upload-area">
                            <p>🎬 Drag & Drop Video Here</p>
                            <small>or click to browse</small>
                        </div>
                        <div class="upload-button-area">
                            <button class="button upload-button" id="upload-btn">
                                📁 Choose Video File
                            </button>
                            <small>Supported: MP4, MOV, AVI, MKV</small>
                        </div>
                    </div>
                    <input type="file" id="file-input" accept="video/*" hidden>
                    
                    <div id="file-info" class="file-info hidden">
                        <p><strong>✅ File uploaded:</strong> <span id="filename"></span></p>
                        <p><strong>Size:</strong> <span id="filesize"></span></p>
                        <p><strong>Download URL:</strong> <a href="#" id="download-url" target="_blank">View uploaded file</a></p>
                    </div>
                    
                    <div id="upload-progress" class="hidden">
                        <div class="progress">
                            <div class="progress-bar" id="upload-bar"></div>
                        </div>
                        <p><span class="loading"></span> Uploading file...</p>
                    </div>
                </div>

                <div class="step">
                    <h2>🎤 Step 2: Transcription</h2>
                    <button class="button" id="transcribe-btn" disabled>🎯 Start Transcription</button>
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
                    <button class="button" id="clips-btn" disabled>🎬 Find Clips Automatically</button>
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
                    <button class="button secondary" id="trim-btn" disabled>✂️ Trim Only</button>
                    <button class="button" id="resize-btn" disabled>📐 Trim + Resize</button>
                    <div id="processing-progress" class="hidden">
                        <div class="progress">
                            <div class="progress-bar" id="processing-bar"></div>
                        </div>
                        <p><span class="loading"></span> <span id="processing-status">Processing video...</span></p>
                    </div>
                    <div id="processing-result" class="status success hidden">
                        <p><strong>✅ Video processing completed!</strong></p>
                        <p><strong>Operation:</strong> <span id="operation-type"></span></p>
                        <p><strong>Duration:</strong> <span id="output-duration"></span>s</p>
                        <p><strong>Output file:</strong> <span id="output-filename"></span></p>
                        <p><strong>Size:</strong> <span id="output-size"></span></p>
                    </div>
                </div>

                <div class="step">
                    <h2>⬇️ Step 5: Download</h2>
                    <button class="button" id="download-btn" disabled>📥 Download Processed Video</button>
                    <p><small>Your processed video will be available for download</small></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global state
        let uploadedFile = null;
        let selectedClip = null;
        let processedVideoUrl = null;
        let hfToken = '';

        // Get elements
        const fileInput = document.getElementById('file-input');
        const uploadArea = document.getElementById('upload-area');
        const uploadBtn = document.getElementById('upload-btn');
        const fileInfo = document.getElementById('file-info');
        const uploadProgress = document.getElementById('upload-progress');
        const uploadBar = document.getElementById('upload-bar');
        const transcribeBtn = document.getElementById('transcribe-btn');
        const clipsBtn = document.getElementById('clips-btn');
        const trimBtn = document.getElementById('trim-btn');
        const resizeBtn = document.getElementById('resize-btn');
        const downloadBtn = document.getElementById('download-btn');

        // Token validation
        function validateToken() {{
            const tokenInput = document.getElementById('hf-token');
            const token = tokenInput.value.trim();
            const statusDiv = document.getElementById('token-status');
            const statusCircle = document.getElementById('token-status-circle');
            
            if (!token) {{
                statusDiv.textContent = '❌ Please enter a token';
                statusDiv.className = 'token-status invalid';
                statusDiv.classList.remove('hidden');
                statusCircle.className = 'status-indicator invalid token-status-circle';
                return;
            }}
            
            // Show loading
            statusDiv.innerHTML = '⏳ Validating token and checking model access...';
            statusDiv.className = 'token-status';
            statusDiv.classList.remove('hidden');
            statusCircle.className = 'status-indicator loading token-status-circle';
            
            // Send validation request
            fetch('/api/validate_token', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ token: token }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.valid) {{
                    if (data.model_access) {{
                        statusDiv.innerHTML = `✅ Valid token with model access! User: <strong>${{data.username || 'Unknown'}}</strong>`;
                        statusCircle.className = 'status-indicator valid token-status-circle';
                    }} else {{
                        statusDiv.innerHTML = `⚠️ Token valid but limited model access. User: <strong>${{data.username || 'Unknown'}}</strong><br><small>${{data.warning || ''}}</small>`;
                        statusCircle.className = 'status-indicator invalid token-status-circle';
                    }}
                    statusDiv.className = 'token-status valid';
                    hfToken = token;
                }} else {{
                    const errorMsg = data.error || 'Invalid token';
                    const hintMsg = data.hint ? `<br><small>${{data.hint}}</small>` : '';
                    statusDiv.innerHTML = `❌ ${{errorMsg}}${{hintMsg}}`;
                    statusDiv.className = 'token-status invalid';
                    statusCircle.className = 'status-indicator invalid token-status-circle';
                }}
            }})
            .catch(error => {{
                statusDiv.textContent = '❌ Error validating token';
                statusDiv.className = 'token-status invalid';
                statusCircle.className = 'status-indicator invalid token-status-circle';
                console.error('Token validation error:', error);
            }});
        }}

        // Add event listener for validate button
        document.getElementById('validate-token-btn').addEventListener('click', validateToken);

        // File upload handling
        function setupEventListeners() {{
            // Upload area click
            uploadArea.addEventListener('click', () => fileInput.click());
            
            // Upload button click
            uploadBtn.addEventListener('click', () => fileInput.click());
            
            // File input change
            fileInput.addEventListener('change', handleFileSelect);
            
            // Drag and drop
            uploadArea.addEventListener('dragover', handleDragOver);
            uploadArea.addEventListener('dragleave', handleDragLeave);
            uploadArea.addEventListener('drop', handleDrop);
        }}

        function handleDragOver(e) {{
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        }}

        function handleDragLeave(e) {{
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        }}

        function handleDrop(e) {{
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {{
                const file = files[0];
                if (file.type.startsWith('video/')) {{
                    uploadFile(file);
                }} else {{
                    alert('Please upload a video file');
                }}
            }}
        }}

        function handleFileSelect(e) {{
            const file = e.target.files[0];
            if (file) {{
                uploadFile(file);
            }}
        }}

        function uploadFile(file) {{
            console.log('Uploading file:', file.name, file.size);
            
            // Show progress
            uploadProgress.classList.remove('hidden');
            fileInfo.classList.add('hidden');
            
            // Create form data
            const formData = new FormData();
            formData.append('video', file);
            
            // Simulate upload progress
            let progress = 0;
            const progressInterval = setInterval(() => {{
                progress += 10;
                uploadBar.style.width = progress + '%';
                
                if (progress >= 90) {{
                    clearInterval(progressInterval);
                }}
            }}, 200);
            
            // Upload file
            fetch('/api/upload', {{
                method: 'POST',
                body: formData
            }})
            .then(response => response.json())
            .then(data => {{
                clearInterval(progressInterval);
                uploadBar.style.width = '100%';
                
                setTimeout(() => {{
                    uploadProgress.classList.add('hidden');
                    
                    if (data.success) {{
                        uploadedFile = data;
                        
                        // Show file info
                        document.getElementById('filename').textContent = data.filename;
                        document.getElementById('filesize').textContent = formatFileSize(data.size);
                        const downloadLink = document.getElementById('download-url');
                        downloadLink.href = data.url;
                        fileInfo.classList.remove('hidden');
                        
                        // Enable next step
                        transcribeBtn.disabled = false;
                        
                        // Reset progress bar
                        uploadBar.style.width = '0%';
                    }} else {{
                        alert('Upload failed: ' + (data.error || 'Unknown error'));
                    }}
                }}, 500);
            }})
            .catch(error => {{
                clearInterval(progressInterval);
                uploadProgress.classList.add('hidden');
                alert('Upload error: ' + error.message);
                console.error('Upload error:', error);
            }});
        }}

        function formatFileSize(bytes) {{
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            if (bytes === 0) return '0 Bytes';
            const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
            return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
        }}

        // Transcription handling
        transcribeBtn.addEventListener('click', () => {{
            const progressDiv = document.getElementById('transcription-progress');
            const resultDiv = document.getElementById('transcription-result');
            const progressBar = document.getElementById('transcription-bar');
            
            progressDiv.classList.remove('hidden');
            resultDiv.classList.add('hidden');
            
            // Simulate progress
            let progress = 0;
            const interval = setInterval(() => {{
                progress += Math.random() * 20;
                if (progress > 100) progress = 100;
                progressBar.style.width = progress + '%';
                if (progress === 100) clearInterval(interval);
            }}, 500);
            
            // Make API call
            fetch('/api/transcribe', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    video_id: uploadedFile.video_id,
                    hf_token: hfToken
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                clearInterval(interval);
                progressBar.style.width = '100%';
                
                setTimeout(() => {{
                    progressDiv.classList.add('hidden');
                    if (data.success) {{
                        // Update UI with results
                        document.getElementById('detected-language').textContent = data.language || 'English';
                        document.getElementById('video-duration').textContent = data.duration + 's';
                        document.getElementById('word-count').textContent = data.word_count;
                        document.getElementById('confidence').textContent = data.confidence + '%';
                        document.getElementById('transcript-text').textContent = data.transcript;
                        
                        resultDiv.classList.remove('hidden');
                        clipsBtn.disabled = false;
                    }} else {{
                        alert('Transcription failed: ' + data.error);
                    }}
                }}, 500);
            }})
            .catch(error => {{
                clearInterval(interval);
                progressDiv.classList.add('hidden');
                alert('Transcription error: ' + error.message);
            }});
        }});

        // Clip finding
        clipsBtn.addEventListener('click', () => {{
            const progressDiv = document.getElementById('clips-progress');
            const resultDiv = document.getElementById('clips-result');
            const progressBar = document.getElementById('clips-bar');
            
            progressDiv.classList.remove('hidden');
            resultDiv.classList.add('hidden');
            
            // Simulate progress
            let progress = 0;
            const interval = setInterval(() => {{
                progress += Math.random() * 15;
                if (progress > 100) progress = 100;
                progressBar.style.width = progress + '%';
                if (progress === 100) clearInterval(interval);
            }}, 400);
            
            // Make API call
            fetch('/api/find_clips', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    video_id: uploadedFile.video_id
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                clearInterval(interval);
                progressBar.style.width = '100%';
                
                setTimeout(() => {{
                    progressDiv.classList.add('hidden');
                    if (data.success) {{
                        displayClips(data.clips);
                        resultDiv.classList.remove('hidden');
                    }} else {{
                        alert('Clip finding failed: ' + data.error);
                    }}
                }}, 500);
            }});
        }});

        function displayClips(clips) {{
            document.getElementById('clips-count').textContent = clips.length;
            const tbody = document.getElementById('clips-tbody');
            tbody.innerHTML = '';
            
            clips.forEach((clip, index) => {{
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>#${{index + 1}}</td>
                    <td>${{clip.topic}}</td>
                    <td>${{formatTime(clip.start_time)}}</td>
                    <td>${{formatTime(clip.end_time)}}</td>
                    <td>${{(clip.end_time - clip.start_time).toFixed(1)}}s</td>
                    <td>${{(clip.score * 100).toFixed(0)}}%</td>
                    <td><button class="button" onclick="selectClip(${{index}})">Select</button></td>
                `;
            }});
            
            window.clipsData = clips;
        }}

        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${{mins}}:${{secs.toString().padStart(2, '0')}}`;
        }}

        function selectClip(index) {{
            selectedClip = window.clipsData[index];
            const info = `Clip #${{index + 1}} - ${{selectedClip.topic}} (${{formatTime(selectedClip.start_time)}} - ${{formatTime(selectedClip.end_time)}})`;
            document.getElementById('selected-clip-info').textContent = info;
            document.getElementById('selected-clip').classList.remove('hidden');
            
            // Enable processing buttons
            trimBtn.disabled = false;
            resizeBtn.disabled = false;
        }}

        // Video processing
        function processVideo(operation) {{
            const progressDiv = document.getElementById('processing-progress');
            const resultDiv = document.getElementById('processing-result');
            const progressBar = document.getElementById('processing-bar');
            const statusText = document.getElementById('processing-status');
            
            progressDiv.classList.remove('hidden');
            resultDiv.classList.add('hidden');
            
            statusText.textContent = operation === 'trim' ? 'Trimming video...' : 'Trimming and resizing video...';
            
            // Simulate progress
            let progress = 0;
            const interval = setInterval(() => {{
                progress += Math.random() * 10;
                if (progress > 100) progress = 100;
                progressBar.style.width = progress + '%';
                if (progress === 100) clearInterval(interval);
            }}, 600);
            
            // Make API call
            fetch('/api/process', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    video_id: uploadedFile.video_id,
                    operation: operation,
                    start_time: selectedClip.start_time,
                    end_time: selectedClip.end_time,
                    aspect_ratio: '9:16' // Default for mobile
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                clearInterval(interval);
                progressBar.style.width = '100%';
                
                setTimeout(() => {{
                    progressDiv.classList.add('hidden');
                    if (data.success) {{
                        processedVideoUrl = data.download_url;
                        
                        // Update UI
                        document.getElementById('operation-type').textContent = 
                            operation === 'trim' ? 'Trim only' : 'Trim + Resize (9:16)';
                        document.getElementById('output-duration').textContent = 
                            (selectedClip.end_time - selectedClip.start_time).toFixed(1);
                        document.getElementById('output-filename').textContent = data.filename;
                        document.getElementById('output-size').textContent = formatFileSize(data.size);
                        
                        resultDiv.classList.remove('hidden');
                        downloadBtn.disabled = false;
                    }} else {{
                        alert('Processing failed: ' + data.error);
                    }}
                }}, 500);
            }});
        }}

        trimBtn.addEventListener('click', () => processVideo('trim'));
        resizeBtn.addEventListener('click', () => processVideo('resize'));

        // Download handling
        downloadBtn.addEventListener('click', () => {{
            if (processedVideoUrl) {{
                window.open(processedVideoUrl, '_blank');
            }}
        }});

        // Initialize
        setupEventListeners();
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_status(self):
        """Serve API status"""
        status = {
            "status": "online",
            "version": "1.0.0",
            "endpoints": [
                "/api/upload",
                "/api/validate_token", 
                "/api/transcribe",
                "/api/find_clips",
                "/api/process"
            ],
            "upload_directory": self.upload_dir,
            "port": PORT
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())

    def handle_upload(self):
        """Handle file upload with multipart/form-data"""
        try:
            # Parse the form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': self.headers['Content-Type']}
            )
            
            # Get the uploaded file
            fileitem = form['video']
            
            # Check if file was uploaded
            if fileitem.filename:
                # Create unique filename
                import uuid
                file_id = str(uuid.uuid4())
                file_ext = os.path.splitext(fileitem.filename)[1]
                new_filename = f"video_{file_id}{file_ext}"
                
                # Save file
                filepath = os.path.join(self.upload_dir, new_filename)
                with open(filepath, 'wb') as f:
                    f.write(fileitem.file.read())
                
                # Get file size
                file_size = os.path.getsize(filepath)
                
                # Prepare response
                response = {
                    "success": True,
                    "filename": fileitem.filename,
                    "video_id": file_id,
                    "size": file_size,
                    "url": f"/uploads/{new_filename}",
                    "message": "File uploaded successfully"
                }
                
                print(f"✅ File uploaded: {fileitem.filename} -> {new_filename} ({file_size} bytes)")
            else:
                response = {
                    "success": False,
                    "error": "No file uploaded"
                }
        
        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            response = {
                "success": False,
                "error": str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_token_validation(self):
        """Validate Hugging Face token"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            token = data.get('token', '').strip()
            
            if not token:
                response = {
                    "valid": False,
                    "error": "No token provided"
                }
            elif not token.startswith('hf_'):
                response = {
                    "valid": False,
                    "error": "Invalid token format. HF tokens start with 'hf_'"
                }
            else:
                # Test token with HF API
                headers = {"Authorization": f"Bearer {token}"}
                api_url = "https://huggingface.co/api/whoami"
                
                try:
                    r = requests.get(api_url, headers=headers, timeout=10)
                    if r.status_code == 200:
                        user_data = r.json()
                        # Test access to pyannote model
                        model_url = "https://huggingface.co/api/models/pyannote/speaker-diarization-3.1"
                        model_r = requests.get(model_url, headers=headers, timeout=5)
                        
                        if model_r.status_code == 200:
                            response = {
                                "valid": True,
                                "username": user_data.get('name', 'Unknown'),
                                "message": "Token is valid and has pyannote model access",
                                "model_access": True
                            }
                            print(f"✅ Valid HF token for user: {user_data.get('name')} with model access")
                        else:
                            response = {
                                "valid": True,
                                "username": user_data.get('name', 'Unknown'),
                                "message": "Token valid but no pyannote model access. Check repository permissions.",
                                "model_access": False,
                                "warning": "You may need to accept the license for pyannote/speaker-diarization-3.1"
                            }
                            print(f"⚠️ Valid token but no model access: {model_r.status_code}")
                    elif r.status_code == 401:
                        response = {
                            "valid": False,
                            "error": "Invalid token. Please check your token or create a new one.",
                            "hint": "Generate a new token at https://huggingface.co/settings/tokens"
                        }
                        print(f"❌ Invalid HF token: 401 Unauthorized")
                    else:
                        response = {
                            "valid": False,
                            "error": f"API error (HTTP {r.status_code}). Please try again.",
                            "hint": "Check your internet connection or try a new token"
                        }
                        print(f"❌ HF API error: {r.status_code}")
                except requests.Timeout:
                    response = {
                        "valid": False,
                        "error": "Request timeout. Please check your internet connection."
                    }
                    print(f"❌ HF API timeout")
                except Exception as e:
                    response = {
                        "valid": False,
                        "error": f"Connection error: {str(e)}",
                        "hint": "Check your internet connection"
                    }
                    print(f"❌ HF API error: {str(e)}")
        
        except Exception as e:
            response = {
                "valid": False,
                "error": str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_transcribe(self):
        """Handle transcription request"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Simulate transcription
            time.sleep(2)  # Simulate processing
            
            response = {
                "success": True,
                "language": "English",
                "duration": 85.7,
                "word_count": 234,
                "confidence": 94,
                "transcript": "This is a sample transcription of your video. In a real implementation, this would contain the actual transcribed text from WhisperX with speaker diarization information if a Hugging Face token was provided. The transcription would include timestamps and speaker labels for each segment of speech detected in the video."
            }
        
        except Exception as e:
            response = {
                "success": False,
                "error": str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_find_clips(self):
        """Handle clip finding request"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Simulate clip finding
            time.sleep(1.5)
            
            clips = [
                {
                    "topic": "Introduction and Overview",
                    "start_time": 0,
                    "end_time": 15.5,
                    "score": 0.92
                },
                {
                    "topic": "Main Product Features",
                    "start_time": 15.5,
                    "end_time": 45.2,
                    "score": 0.88
                },
                {
                    "topic": "Customer Testimonial",
                    "start_time": 45.2,
                    "end_time": 62.8,
                    "score": 0.95
                },
                {
                    "topic": "Pricing and Availability",
                    "start_time": 62.8,
                    "end_time": 80.0,
                    "score": 0.85
                },
                {
                    "topic": "Call to Action",
                    "start_time": 80.0,
                    "end_time": 85.7,
                    "score": 0.90
                }
            ]
            
            response = {
                "success": True,
                "clips": clips,
                "total_clips": len(clips)
            }
        
        except Exception as e:
            response = {
                "success": False,
                "error": str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_process(self):
        """Handle video processing request"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Simulate processing
            time.sleep(3)
            
            operation = data.get('operation', 'trim')
            filename = f"processed_video_{data.get('video_id', 'unknown')}_{operation}.mp4"
            
            response = {
                "success": True,
                "filename": filename,
                "size": 2457600,  # ~2.4MB
                "download_url": f"/downloads/{filename}",
                "operation": operation,
                "message": f"Video {operation} completed successfully"
            }
        
        except Exception as e:
            response = {
                "success": False,
                "error": str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def serve_uploaded_file(self):
        """Serve uploaded files"""
        try:
            # Extract filename from path
            filename = os.path.basename(self.path)
            filepath = os.path.join(self.upload_dir, filename)
            
            if os.path.exists(filepath):
                # Determine content type
                content_type, _ = mimetypes.guess_type(filepath)
                if content_type is None:
                    content_type = 'application/octet-stream'
                
                # Send file
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Content-length', str(os.path.getsize(filepath)))
                self.end_headers()
                
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def serve_api(self):
        """Serve other API endpoints"""
        endpoints = {
            "/api/status": {"status": "online", "version": "1.0.0"},
            "/api/health": {"status": "healthy", "timestamp": time.time()}
        }
        
        if self.path in endpoints:
            response = endpoints[self.path]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "API endpoint not found")

# Initialize upload directory
ClipsAIHandler.initialize_upload_dir()

if __name__ == "__main__":
    print(f"\n🎬 ClipsAI Web Server Starting...")
    print(f"📁 Upload directory: {ClipsAIHandler.upload_dir}")
    print(f"🌐 Port: {PORT}")
    
    with socketserver.TCPServer(("", PORT), ClipsAIHandler) as httpd:
        print(f"\n✅ Server running at http://localhost:{PORT}")
        print(f"🐳 Ready for Docker deployment")
        print("\nPress Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")
            # Cleanup
            if os.path.exists(ClipsAIHandler.upload_dir):
                shutil.rmtree(ClipsAIHandler.upload_dir)
                print(f"🧹 Cleaned up upload directory")