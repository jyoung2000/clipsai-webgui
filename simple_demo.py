#!/usr/bin/env python3
"""
Simple demonstration of the ClipsAI Web Interface
This creates a basic HTML version of the interface for demonstration
"""

import http.server
import socketserver
import webbrowser
import threading
import time

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 ClipsAI Web Interface - Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f0f2f6; }
        .header { text-align: center; background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .step { background: white; margin: 15px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .step h2 { color: #FF6B6B; margin-top: 0; }
        .button { background: #FF6B6B; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px 5px; }
        .button:hover { background: #FF5252; }
        .secondary { background: #4ECDC4; }
        .secondary:hover { background: #26A69A; }
        .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; border-radius: 10px; }
        .upload-area:hover { border-color: #FF6B6B; background: #f9f9f9; }
        .sidebar { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .config-section { margin-bottom: 15px; }
        .config-section label { display: block; margin-bottom: 5px; font-weight: bold; }
        .config-section input, .config-section select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
        .demo-note { background: #FFF3CD; border: 1px solid #FFEAA7; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .feature-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
        .feature-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .feature-card h3 { margin-top: 0; color: #4ECDC4; }
        .progress { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-bar { height: 100%; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); width: 0%; transition: width 0.3s; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 ClipsAI Web Interface</h1>
        <p>Transform your videos with AI-powered transcription, clip finding, and intelligent resizing</p>
    </div>

    <div class="demo-note">
        <strong>📺 Demo Mode:</strong> This is a visual demonstration of the ClipsAI Streamlit interface. 
        To run the actual application with full functionality, use: <code>streamlit run app.py</code>
    </div>

    <div class="grid">
        <div class="sidebar">
            <h2>⚙️ Configuration</h2>
            
            <div class="config-section">
                <label for="hf-token">🤗 Hugging Face Token:</label>
                <input type="password" id="hf-token" placeholder="Required for speaker diarization">
                <small>Get your token from <a href="https://huggingface.co/settings/tokens" target="_blank">Hugging Face</a></small>
            </div>
            
            <div class="config-section">
                <label for="model-size">🎯 Whisper Model:</label>
                <select id="model-size">
                    <option value="tiny">Tiny (Fast)</option>
                    <option value="base" selected>Base (Recommended)</option>
                    <option value="small">Small (Better)</option>
                    <option value="medium">Medium (High Quality)</option>
                    <option value="large-v2">Large-v2 (Best)</option>
                </select>
            </div>
            
            <div class="config-section">
                <label for="aspect-ratio">📐 Aspect Ratio:</label>
                <select id="aspect-ratio">
                    <option value="16:9">16:9 (Landscape)</option>
                    <option value="9:16" selected>9:16 (Portrait/Shorts)</option>
                    <option value="1:1">1:1 (Square)</option>
                    <option value="4:3">4:3 (Standard)</option>
                    <option value="custom">Custom</option>
                </select>
            </div>
            
            <div class="config-section">
                <label for="min-duration">⏱️ Min Clip Duration:</label>
                <input type="range" id="min-duration" min="5" max="60" value="15">
                <span id="min-duration-value">15 seconds</span>
            </div>
        </div>

        <div class="main-content">
            <div class="step">
                <h2>📹 Step 1: Upload Video</h2>
                <div class="upload-area" onclick="document.getElementById('file-input').click()">
                    <input type="file" id="file-input" accept="video/*" style="display: none;" onchange="handleFileUpload()">
                    <p>🎬 Click to upload video file</p>
                    <p><small>Supports MP4, AVI, MOV, MKV, FLV, WMV</small></p>
                </div>
                <div id="file-info" style="display: none;">
                    <p>✅ Video uploaded: <span id="filename"></span></p>
                    <p>File size: <span id="filesize"></span> MB</p>
                </div>
            </div>

            <div class="step">
                <h2>🎤 Step 2: Transcription</h2>
                <button class="button" onclick="startTranscription()">🎯 Start Transcription</button>
                <div id="transcription-progress" style="display: none;">
                    <div class="progress">
                        <div class="progress-bar" id="transcription-bar"></div>
                    </div>
                    <p>Transcribing video... This may take a few minutes.</p>
                </div>
                <div id="transcription-result" style="display: none;">
                    <p>✅ Transcription completed!</p>
                    <p><strong>Language:</strong> <span id="detected-language">English</span></p>
                    <p><strong>Duration:</strong> <span id="video-duration">45.2s</span></p>
                    <p><strong>Word Count:</strong> <span id="word-count">127</span></p>
                    <details>
                        <summary>📝 View Full Transcript</summary>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                            <p>This is a demo transcript. In the actual application, you would see the complete speech-to-text transcription of your video here, with accurate timestamps and speaker identification.</p>
                        </div>
                    </details>
                </div>
            </div>

            <div class="step">
                <h2>🔍 Step 3: Find Clips</h2>
                <button class="button" onclick="findClips()">🎬 Find Clips Automatically</button>
                <div id="clips-progress" style="display: none;">
                    <div class="progress">
                        <div class="progress-bar" id="clips-bar"></div>
                    </div>
                    <p>Analyzing video for interesting segments...</p>
                </div>
                <div id="clips-result" style="display: none;">
                    <p>✅ Found 5 clips!</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Clip #</th>
                                <th>Start Time</th>
                                <th>End Time</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>1</td>
                                <td>00:05</td>
                                <td>00:25</td>
                                <td>20s</td>
                            </tr>
                            <tr style="background: #e3f2fd;">
                                <td>2</td>
                                <td>00:30</td>
                                <td>00:55</td>
                                <td>25s</td>
                            </tr>
                            <tr>
                                <td>3</td>
                                <td>01:10</td>
                                <td>01:35</td>
                                <td>25s</td>
                            </tr>
                        </tbody>
                    </table>
                    <p><strong>Selected:</strong> Clip 2 (00:30 - 00:55)</p>
                </div>
            </div>

            <div class="step">
                <h2>🎬 Step 4: Process Video</h2>
                <button class="button secondary" onclick="trimOnly()">✂️ Trim Only</button>
                <button class="button" onclick="trimAndResize()">📐 Trim + Resize</button>
                <div id="processing-progress" style="display: none;">
                    <div class="progress">
                        <div class="progress-bar" id="processing-bar"></div>
                    </div>
                    <p id="processing-status">Processing video...</p>
                </div>
                <div id="processing-result" style="display: none;">
                    <p>✅ Video processing completed!</p>
                    <p><strong>Output:</strong> Trimmed and resized to 9:16 aspect ratio</p>
                    <p><strong>New file size:</strong> 2.1 MB</p>
                </div>
            </div>

            <div class="step">
                <h2>⬇️ Step 5: Download</h2>
                <button class="button" onclick="downloadVideo()" disabled id="download-btn">📥 Download Processed Video</button>
                <p><small>Your processed video will be downloaded as an MP4 file</small></p>
            </div>
        </div>
    </div>

    <div class="feature-list">
        <div class="feature-card">
            <h3>🎯 Smart Transcription</h3>
            <p>Powered by WhisperX with 5 model sizes for speed/accuracy balance</p>
        </div>
        <div class="feature-card">
            <h3>🤖 AI Clip Detection</h3>
            <p>Automatically finds the most interesting segments in your video</p>
        </div>
        <div class="feature-card">
            <h3>👥 Speaker Diarization</h3>
            <p>Identifies different speakers using Pyannote AI technology</p>
        </div>
        <div class="feature-card">
            <h3>📱 Smart Resizing</h3>
            <p>Intelligently crops videos for social media formats</p>
        </div>
    </div>

    <script>
        let currentStep = 1;
        
        function handleFileUpload() {
            const fileInput = document.getElementById('file-input');
            const file = fileInput.files[0];
            if (file) {
                document.getElementById('filename').textContent = file.name;
                document.getElementById('filesize').textContent = (file.size / 1024 / 1024).toFixed(2);
                document.getElementById('file-info').style.display = 'block';
                currentStep = 2;
            }
        }
        
        function startTranscription() {
            if (currentStep < 2) return alert('Please upload a video first!');
            
            document.getElementById('transcription-progress').style.display = 'block';
            animateProgress('transcription-bar', 3000, () => {
                document.getElementById('transcription-progress').style.display = 'none';
                document.getElementById('transcription-result').style.display = 'block';
                currentStep = 3;
            });
        }
        
        function findClips() {
            if (currentStep < 3) return alert('Please complete transcription first!');
            
            document.getElementById('clips-progress').style.display = 'block';
            animateProgress('clips-bar', 2000, () => {
                document.getElementById('clips-progress').style.display = 'none';
                document.getElementById('clips-result').style.display = 'block';
                currentStep = 4;
            });
        }
        
        function trimOnly() {
            processVideo('Trimming video...');
        }
        
        function trimAndResize() {
            const token = document.getElementById('hf-token').value;
            if (!token) return alert('Please enter your Hugging Face token for resizing!');
            processVideo('Trimming and resizing video...');
        }
        
        function processVideo(statusText) {
            if (currentStep < 4) return alert('Please find clips first!');
            
            document.getElementById('processing-progress').style.display = 'block';
            document.getElementById('processing-status').textContent = statusText;
            animateProgress('processing-bar', 4000, () => {
                document.getElementById('processing-progress').style.display = 'none';
                document.getElementById('processing-result').style.display = 'block';
                document.getElementById('download-btn').disabled = false;
                currentStep = 5;
            });
        }
        
        function downloadVideo() {
            alert('🎉 In the actual application, your processed video would download now!\\n\\nThis is a demo interface. Run "streamlit run app.py" for full functionality.');
        }
        
        function animateProgress(barId, duration, callback) {
            const bar = document.getElementById(barId);
            let width = 0;
            const interval = setInterval(() => {
                width += 100 / (duration / 50);
                bar.style.width = Math.min(width, 100) + '%';
                if (width >= 100) {
                    clearInterval(interval);
                    setTimeout(callback, 500);
                }
            }, 50);
        }
        
        // Update slider value display
        document.getElementById('min-duration').addEventListener('input', function() {
            document.getElementById('min-duration-value').textContent = this.value + ' seconds';
        });
    </script>
</body>
</html>
"""

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode())
        else:
            super().do_GET()

def start_server():
    PORT = 8501
    
    with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
        print(f"🎬 ClipsAI Web Interface Demo running at http://localhost:{PORT}")
        print("🌐 Opening browser...")
        
        # Try to open browser after a short delay
        def open_browser():
            time.sleep(1)
            try:
                webbrowser.open(f"http://localhost:{PORT}")
            except:
                pass
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n👋 Demo server stopped.")

if __name__ == "__main__":
    start_server()