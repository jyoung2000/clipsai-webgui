#!/usr/bin/env python3
"""
Enhanced ClipsAI Web Server
A fully functional web interface for ClipsAI with file upload and processing simulation
"""

import http.server
import socketserver
import urllib.parse
import json
import tempfile
import os
import threading
import time
import base64
from pathlib import Path

class ClipsAIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.upload_dir = tempfile.mkdtemp()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_main_page()
        elif self.path == '/api/status':
            self.serve_status()
        elif self.path.startswith('/api/'):
            self.serve_api()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/upload':
            self.handle_upload()
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
            "version": "1.0.0",
            "features": ["upload", "transcribe", "clip_finding", "processing"],
            "uptime": time.time()
        }
        self.send_json_response(status)

    def serve_api(self):
        self.send_json_response({"message": "ClipsAI API is running"})

    def handle_upload(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Simulate file upload processing
            filename = f"uploaded_video_{int(time.time())}.mp4"
            file_path = os.path.join(self.upload_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(post_data)
            
            response = {
                "success": True,
                "filename": filename,
                "size": len(post_data),
                "path": file_path,
                "message": "File uploaded successfully"
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)

    def handle_transcribe(self):
        try:
            # Simulate transcription processing
            time.sleep(2)  # Simulate processing time
            
            response = {
                "success": True,
                "transcript": "This is a sample transcription of the uploaded video. In a real implementation, this would be generated using WhisperX with the selected model size.",
                "language": "en",
                "duration": 45.2,
                "word_count": 127,
                "confidence": 0.95
            }
            self.send_json_response(response)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)

    def handle_find_clips(self):
        try:
            # Simulate clip finding
            time.sleep(1.5)
            
            clips = [
                {"id": 1, "start": 5.0, "end": 25.0, "duration": 20.0, "score": 0.92},
                {"id": 2, "start": 30.0, "end": 55.0, "duration": 25.0, "score": 0.88},
                {"id": 3, "start": 70.0, "end": 95.0, "duration": 25.0, "score": 0.85},
                {"id": 4, "start": 105.0, "end": 125.0, "duration": 20.0, "score": 0.82},
                {"id": 5, "start": 140.0, "end": 165.0, "duration": 25.0, "score": 0.79}
            ]
            
            response = {
                "success": True,
                "clips": clips,
                "total_clips": len(clips),
                "message": f"Found {len(clips)} potential clips"
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
            
            # Simulate processing time
            if operation == 'trim_and_resize':
                time.sleep(4)
                message = "Video trimmed and resized successfully"
            else:
                time.sleep(2)
                message = "Video trimmed successfully"
            
            response = {
                "success": True,
                "operation": operation,
                "output_file": f"processed_video_{int(time.time())}.mp4",
                "size": 2100000,  # 2.1 MB
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
        self.end_headers()
        self.wfile.write(json_data.encode())

    def get_main_html(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 ClipsAI Web Interface</title>
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
        .status.info { background: rgba(102, 126, 234, 0.2); border: 1px solid #667eea; color: #667eea; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; background: #0f1419; border-radius: 8px; overflow: hidden; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #1a1a2e; color: #667eea; font-weight: 600; }
        tr:hover { background: rgba(102, 126, 234, 0.1); }
        .hidden { display: none; }
        .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(255,255,255,.3); border-radius: 50%; border-top-color: #667eea; animation: spin 1s ease-in-out infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .file-info { background: rgba(78, 205, 196, 0.1); padding: 15px; border-radius: 8px; margin: 15px 0; }
        @media (max-width: 768px) { .main-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 ClipsAI Web Interface</h1>
            <p>Transform your videos with AI-powered transcription, clip finding, and intelligent resizing</p>
        </div>

        <div class="main-grid">
            <div class="sidebar">
                <h2>⚙️ Configuration</h2>
                
                <div class="config-section">
                    <label for="hf-token">🤗 Hugging Face Token</label>
                    <input type="password" id="hf-token" placeholder="Required for speaker diarization">
                    <small style="color: #888; font-size: 12px;">Get your token from <a href="https://huggingface.co/settings/tokens" target="_blank" style="color: #667eea;">Hugging Face</a></small>
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
                    <div class="upload-area" id="upload-area">
                        <input type="file" id="file-input" accept="video/*" style="display: none;">
                        <p>🎬 Click or drag to upload video file</p>
                        <p><small>Supports MP4, AVI, MOV, MKV, FLV, WMV</small></p>
                    </div>
                    <div id="file-info" class="file-info hidden">
                        <p><strong>✅ File uploaded:</strong> <span id="filename"></span></p>
                        <p><strong>Size:</strong> <span id="filesize"></span></p>
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
                        <p><strong>Duration:</strong> <span id="video-duration">45.2s</span></p>
                        <p><strong>Word Count:</strong> <span id="word-count">127</span></p>
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
            uploadArea.addEventListener('drop', handleDrop);
            fileInput.addEventListener('change', handleFileSelect);
            
            document.getElementById('min-duration').addEventListener('input', function() {
                document.getElementById('min-duration-value').textContent = this.value + 's';
            });
        }

        function handleDragOver(e) {
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
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

        function processFile(file) {
            uploadedFile = file;
            document.getElementById('filename').textContent = file.name;
            document.getElementById('filesize').textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB';
            document.getElementById('file-info').classList.remove('hidden');
            document.getElementById('transcribe-btn').disabled = false;
            currentStep = 2;
            updateSystemStatus('File uploaded - Ready for transcription');
        }

        async function startTranscription() {
            if (!uploadedFile) return;
            
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
                    <td>${formatTime(clip.start)}</td>
                    <td>${formatTime(clip.end)}</td>
                    <td>${clip.duration}s</td>
                    <td>${(clip.score * 100).toFixed(1)}%</td>
                    <td><button class="button" onclick="selectClip(${index}, ${clip.id})" style="padding: 5px 10px; font-size: 12px;">Select</button></td>
                `;
            });
        }

        function selectClip(index, clipId) {
            selectedClip = { index, clipId };
            document.getElementById('selected-clip-info').textContent = `Clip ${clipId}`;
            document.getElementById('selected-clip').classList.remove('hidden');
            document.getElementById('trim-btn').disabled = false;
            document.getElementById('resize-btn').disabled = false;
            updateSystemStatus('Clip selected - Ready to process');
        }

        async function trimOnly() {
            await processVideo('trim');
        }

        async function trimAndResize() {
            const token = document.getElementById('hf-token').value;
            if (!token) {
                showError('Please enter your Hugging Face token for resizing');
                return;
            }
            await processVideo('trim_and_resize');
        }

        async function processVideo(operation) {
            showProgress('processing');
            const statusText = operation === 'trim_and_resize' ? 'Trimming and resizing video...' : 'Trimming video...';
            document.getElementById('processing-status').textContent = statusText;
            updateSystemStatus(statusText);
            
            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ operation })
                });
                const result = await response.json();
                
                if (result.success) {
                    hideProgress('processing');
                    document.getElementById('operation-type').textContent = result.operation.replace('_', ' + ');
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
                link.href = 'data:application/octet-stream;base64,';
                link.download = processedVideo.output_file;
                link.click();
                updateSystemStatus('Download complete!');
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
            const errorDiv = document.createElement('div');
            errorDiv.className = 'status error';
            errorDiv.innerHTML = `<strong>❌ Error:</strong> ${message}`;
            document.querySelector('.main-content').insertBefore(errorDiv, document.querySelector('.step'));
            setTimeout(() => errorDiv.remove(), 5000);
        }

        // Check server status
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                updateSystemStatus('Connected - ' + data.status);
            })
            .catch(() => {
                updateSystemStatus('Server connection error');
            });
    </script>
</body>
</html>
        """

def start_server(port=8501):
    """Start the ClipsAI web server"""
    try:
        with socketserver.TCPServer(("", port), ClipsAIHandler) as httpd:
            print(f"🎬 ClipsAI Web Interface running at http://localhost:{port}")
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