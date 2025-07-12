# 🐳 ClipsAI Web GUI Docker Container - Port 5555 ✅

## 🎉 Docker Container Successfully Created!

The ClipsAI Web GUI has been successfully containerized for deployment on port **5555** with proper Unraid 7.1.3 permissions.

---

## 📦 What Was Created

### 1. **Dockerfile** ✅
- Based on Python 3.11-slim for optimal performance
- Includes `gosu` for proper permission handling
- Configures environment variables for PUID/PGID
- Exposes port 5555
- Includes health check endpoint

### 2. **docker-compose.yml** ✅
- Configured for port 5555
- Proper volume mappings for Unraid
- Security options (no-new-privileges)
- Health check configuration
- Resource limits support

### 3. **server_port5555.py** ✅
- Web server configured to run on port 5555
- Environment variable support for PORT
- Health check endpoint at `/api/health`
- Full upload/download functionality
- HF token validation
- All interactive features working

### 4. **entrypoint.sh** ✅
- Updated to support PORT environment variable
- Proper PUID/PGID handling for Unraid
- Creates necessary directories
- Sets correct permissions
- Switches to non-root user (nobody)

### 5. **build_and_run.sh** ✅
- Helper script to build and run the container
- Stops existing containers
- Builds the image
- Runs with proper port mapping

---

## 🚀 How to Deploy

### Option 1: Using Docker Compose
```bash
# Build and start the container
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Using Build Script
```bash
# Make script executable
chmod +x build_and_run.sh

# Build and run
./build_and_run.sh
```

### Option 3: Manual Docker Commands
```bash
# Build the image
docker build -t clipsai/webgui:latest -f Dockerfile .

# Run the container
docker run -d \
  --name clipsai-webgui \
  -p 5555:5555 \
  -e PUID=99 \
  -e PGID=100 \
  -e PORT=5555 \
  -v ./config:/config \
  -v ./data:/data \
  -v ./uploads:/app/uploads \
  -v ./logs:/app/logs \
  clipsai/webgui:latest
```

---

## 🔧 Container Configuration

### Environment Variables:
- `PORT=5555` - Web server port
- `PUID=99` - User ID (nobody on Unraid)
- `PGID=100` - Group ID (users on Unraid)
- `UMASK=022` - File permission mask
- `TZ=America/New_York` - Timezone

### Volume Mappings:
- `/config` - Configuration files
- `/data` - User data and videos
- `/app/uploads` - Temporary uploads
- `/app/logs` - Application logs

### Port Mapping:
- `5555:5555` - Web interface

---

## ✅ Features Verified

1. **Web Interface** - Runs on port 5555
2. **File Upload** - Drag & drop + button upload
3. **HF Token Validation** - Working validation endpoint
4. **Permissions** - Proper PUID/PGID handling
5. **Health Checks** - `/api/health` endpoint
6. **Logging** - Comprehensive logging to files
7. **Security** - Non-root user execution

---

## 🌐 Access the Web GUI

Once the container is running, access the web interface at:

```
http://localhost:5555
```

Or if deploying on Unraid:

```
http://your-unraid-ip:5555
```

---

## 📊 Container Management

### Check Container Status:
```bash
docker ps | grep clipsai-webgui
```

### View Logs:
```bash
docker logs -f clipsai-webgui
```

### Stop Container:
```bash
docker stop clipsai-webgui
```

### Remove Container:
```bash
docker rm clipsai-webgui
```

### Check Health:
```bash
curl http://localhost:5555/api/health
```

---

## 🏆 Summary

✅ **Docker container created** with all requested features  
✅ **Port 5555** configured as requested  
✅ **Unraid permissions** properly handled (PUID/PGID)  
✅ **Web GUI starts** and is fully functional  
✅ **All interactive features** working (upload, validation, etc.)  
✅ **Ready for deployment** on Unraid 7.1.3  

The container is production-ready and can be deployed immediately!

---

*Container created on: July 12, 2025*  
*Status: Production Ready* 🚀