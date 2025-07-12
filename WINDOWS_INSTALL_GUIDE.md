# 🪟 ClipsAI Web GUI - Windows Installation Guide

## 🎯 **One-Click Windows Installation**

Transform your ClipsAI Web GUI into a Windows application with Docker Desktop!

---

## 📋 **Requirements**

- **Windows 10/11** (64-bit)
- **4GB RAM** minimum (8GB recommended)
- **Internet connection** for downloads
- **Administrator privileges** for Docker installation

---

## 🚀 **Quick Start (3 Steps)**

### **Step 1: Install Docker Desktop**
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Run installer as Administrator
3. Restart computer when prompted
4. Start Docker Desktop (wait for it to fully load)

### **Step 2: Download ClipsAI Package**
1. Download the release ZIP from GitHub
2. Extract to desired folder (e.g., `C:\ClipsAI\`)
3. You should see `ClipsAI-Start.bat` file

### **Step 3: Launch Application**
1. **Double-click `ClipsAI-Start.bat`**
2. Wait for download and startup (1-2 minutes first time)
3. Browser opens automatically to the web interface
4. Start using ClipsAI Web GUI!

---

## 🎬 **Using ClipsAI Web GUI**

### **🌐 Web Interface**
- **URL:** http://localhost:5555
- **Modern dark theme** with professional styling
- **Responsive design** works on any screen size

### **🔧 Core Features**
1. **🎬 Video Upload**
   - Drag & drop any video file
   - Or click "Choose Video File" button
   - Supports: MP4, MOV, AVI, MKV

2. **🔑 Hugging Face Token**
   - Enter your HF token for AI features
   - **Visual validation** with red/green circles
   - Real-time verification with model access check

3. **🎤 AI Transcription**
   - Powered by WhisperX
   - Speaker diarization with Pyannote
   - High accuracy transcription

4. **🔍 Smart Clip Finding**
   - AI-powered clip detection
   - Automatic topic identification
   - Confidence scoring

5. **✂️ Video Processing**
   - Trim videos to specific segments
   - Resize for different aspect ratios
   - Optimize for social media

6. **⬇️ Download Results**
   - Download processed videos
   - Multiple format options
   - Batch processing support

---

## 📁 **File Storage**

Your files are stored in: `%USERPROFILE%\ClipsAI\`

```
📁 C:\Users\[YourName]\ClipsAI\
├── 📁 config\     # Application settings
├── 📁 data\       # Your video files
├── 📁 uploads\    # Temporary uploads
└── 📁 logs\       # Application logs
```

---

## ⚙️ **Management Options**

The `ClipsAI-Start.bat` script provides these options:

- **[V]** View container logs (for troubleshooting)
- **[S]** Stop ClipsAI Web GUI completely
- **[R]** Restart the application
- **[O]** Open web interface again
- **[Q]** Leave running in background

---

## 🔧 **Troubleshooting**

### **❌ "Docker is not installed"**
- Install Docker Desktop from official website
- Restart computer after installation
- Make sure Docker Desktop is running

### **❌ "Docker is not running"**
- Look for Docker whale icon in system tray
- Right-click → "Start Docker Desktop"
- Wait 1-2 minutes for full startup

### **❌ "Failed to download image"**
- Check internet connection
- Disable antivirus temporarily
- Try running as Administrator

### **❌ "Application not responding"**
- Wait longer (first startup takes time)
- Check container logs with [V] option
- Restart with [R] option

### **❌ "Port 5555 already in use"**
- Stop other applications using port 5555
- Or restart computer to free the port

---

## 🔒 **Security Notes**

- **Safe & Secure:** All processing happens locally
- **No data sent to cloud** (except HF token validation)
- **Isolated environment** via Docker container
- **Your videos never leave your computer**

---

## 🆙 **Updates**

To update to the latest version:
1. Run `ClipsAI-Start.bat`
2. The script automatically downloads the latest version
3. No manual updates needed!

---

## 🎯 **Professional Features**

### **✅ Production Ready**
- Automatic health checks
- Error recovery mechanisms
- Professional logging
- Resource management

### **✅ User Friendly**
- One-click startup
- Automatic browser opening
- Visual status indicators
- Comprehensive help system

### **✅ Enterprise Grade**
- Docker containerization
- Scalable architecture
- API-first design
- Comprehensive documentation

---

## 🏆 **Why This Approach?**

### **🔥 Advantages:**
- **No complex setup** - Just install Docker once
- **Always up-to-date** - Pulls latest version automatically
- **Consistent environment** - Works the same on every Windows PC
- **Easy uninstall** - Just delete the folder
- **Professional grade** - Same quality as enterprise software

### **💾 vs. Traditional EXE:**
- **Smaller download** (script vs. 200MB+ executable)
- **Better security** (isolated container environment)
- **Automatic updates** (no manual downloads)
- **Cross-platform ready** (same container works everywhere)

---

## 🎉 **Ready to Use!**

Your ClipsAI Web GUI is now a **professional Windows application** with:

✅ **One-click startup**  
✅ **Professional interface**  
✅ **Automatic updates**  
✅ **Local processing**  
✅ **Enterprise security**  

**🌐 Just double-click `ClipsAI-Start.bat` and start processing videos!**

---

*🎬 Transform your videos with AI-powered ClipsAI Web GUI on Windows!*