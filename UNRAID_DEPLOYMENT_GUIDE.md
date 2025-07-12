# 🐳 **ClipsAI Web GUI - Unraid 7.1.3 Deployment Guide**

## 📦 **Complete Docker Container Setup for Unraid**

This guide provides everything needed to deploy the ClipsAI Web GUI as a Docker container on Unraid 7.1.3 with proper permissions and user management.

---

## 🎯 **What's Included**

### **📁 Container Files:**
- `Dockerfile.unraid` - Optimized Dockerfile for Unraid 7.1.3
- `entrypoint.sh` - Proper user/permission handling script
- `server.unraid.py` - Container-optimized web server
- `requirements.unraid.txt` - Minimal dependencies for container
- `docker-compose.unraid.yml` - Docker Compose configuration
- `unraid-template.xml` - Unraid Community Applications template

### **🔧 Key Features:**
- ✅ **Proper PUID/PGID handling** (nobody:users by default)
- ✅ **Unraid 7.1.3 compatibility** with proper permissions
- ✅ **Health checks** for container monitoring
- ✅ **Volume mounting** for persistent data
- ✅ **Resource limits** and security options
- ✅ **Comprehensive logging** for troubleshooting

---

## 🚀 **Quick Deployment Options**

### **Option 1: Using Docker Compose (Recommended)**

1. **Copy files to Unraid:**
```bash
# Copy files to your Unraid shares
cp Dockerfile.unraid /mnt/user/docker/clipsai/
cp entrypoint.sh /mnt/user/docker/clipsai/
cp server.unraid.py /mnt/user/docker/clipsai/
cp requirements.unraid.txt /mnt/user/docker/clipsai/
cp docker-compose.unraid.yml /mnt/user/docker/clipsai/docker-compose.yml
```

2. **Build and run:**
```bash
cd /mnt/user/docker/clipsai/
docker-compose up -d
```

### **Option 2: Using Unraid Template**

1. **Add template to Community Applications:**
   - Copy `unraid-template.xml` content
   - Add to your CA template repository

2. **Install via Unraid WebUI:**
   - Go to Apps tab
   - Search for "ClipsAI"
   - Click Install and configure paths

### **Option 3: Manual Docker Command**

```bash
docker run -d \
  --name=clipsai-webgui \
  --restart=unless-stopped \
  -e PUID=99 \
  -e PGID=100 \
  -e UMASK=022 \
  -e TZ=America/New_York \
  -p 8501:8501 \
  -v /mnt/user/appdata/clipsai:/config \
  -v /mnt/user/data/clipsai:/data \
  -v /mnt/user/appdata/clipsai/uploads:/app/uploads \
  --security-opt no-new-privileges:true \
  clipsai/webgui:latest
```

---

## 📋 **Container Configuration**

### **🌍 Environment Variables:**
```bash
PUID=99                    # User ID (default: nobody)
PGID=100                   # Group ID (default: users)  
UMASK=022                  # Permission mask
TZ=America/New_York        # Your timezone
```

### **📁 Volume Mappings:**
```bash
/config       -> /mnt/user/appdata/clipsai          # Config storage
/data         -> /mnt/user/data/clipsai             # User videos  
/app/uploads  -> /mnt/user/appdata/clipsai/uploads  # Temp uploads
/app/logs     -> /mnt/user/appdata/clipsai/logs     # Logs (optional)
```

### **🌐 Port Mapping:**
```bash
8501:8501     # Web interface port
```

---

## 🔧 **Building the Container**

### **1. Prepare Build Environment:**
```bash
# Create build directory
mkdir -p /mnt/user/docker/clipsai
cd /mnt/user/docker/clipsai

# Copy all necessary files
cp /path/to/Dockerfile.unraid ./Dockerfile
cp /path/to/entrypoint.sh ./
cp /path/to/server.unraid.py ./final_working_server.py
cp /path/to/requirements.unraid.txt ./requirements.txt
```

### **2. Build the Image:**
```bash
docker build -t clipsai/webgui:latest -f Dockerfile .
```

### **3. Test the Build:**
```bash
docker run --rm -p 8501:8501 \
  -e PUID=99 -e PGID=100 \
  clipsai/webgui:latest
```

---

## 📊 **Unraid-Specific Features**

### **🔐 Permission Management:**
The container automatically handles Unraid permissions:
- **PUID/PGID**: Maps to your Unraid user/group
- **UMASK**: Controls default file permissions
- **File ownership**: Automatically corrected on startup

### **📈 Health Monitoring:**
```bash
# Check container health
docker exec clipsai-webgui curl -f http://localhost:8501/api/health

# View detailed status
docker exec clipsai-webgui curl -s http://localhost:8501/api/status | jq
```

### **📝 Logging:**
```bash
# Container logs
docker logs clipsai-webgui

# Application logs
docker exec clipsai-webgui tail -f /app/logs/clipsai.log

# Upload logs
docker exec clipsai-webgui tail -f /app/logs/uploads.log
```

---

## 🛠️ **Unraid Template Configuration**

When installing via Unraid WebUI, configure these settings:

### **🔧 Basic Settings:**
- **Container Name:** ClipsAI-WebGUI
- **Repository:** clipsai/webgui:latest
- **Network Type:** Bridge
- **Console Shell Command:** Bash

### **📁 Path Mappings:**
| Container Path | Host Path | Access Mode | Description |
|----------------|-----------|-------------|-------------|
| `/config` | `/mnt/user/appdata/clipsai` | Read/Write | Config storage |
| `/data` | `/mnt/user/data/clipsai` | Read/Write | User videos |
| `/app/uploads` | `/mnt/user/appdata/clipsai/uploads` | Read/Write | Temp uploads |
| `/app/logs` | `/mnt/user/appdata/clipsai/logs` | Read/Write | Logs |

### **🌐 Port Configuration:**
| Container Port | Host Port | Connection Type |
|----------------|-----------|-----------------|
| 8501 | 8501 | TCP |

### **🔧 Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 99 | User ID for permissions |
| `PGID` | 100 | Group ID for permissions |
| `UMASK` | 022 | File permission mask |
| `TZ` | America/New_York | Container timezone |

---

## 🐛 **Troubleshooting**

### **📁 Permission Issues:**
```bash
# Check container user
docker exec clipsai-webgui id

# Fix permissions manually
docker exec clipsai-webgui chown -R nobody:users /app /config /data

# Check upload directory
docker exec clipsai-webgui ls -la /app/uploads
```

### **🌐 Connection Issues:**
```bash
# Test web interface
curl -I http://your-unraid-ip:8501

# Check port binding
docker port clipsai-webgui

# View container logs
docker logs --tail 50 clipsai-webgui
```

### **💾 Storage Issues:**
```bash
# Check disk space
docker exec clipsai-webgui df -h

# Check mount points
docker exec clipsai-webgui mount | grep /app
```

### **🔍 Debug Mode:**
```bash
# Run with debug logging
docker run --rm -it \
  -e PUID=99 -e PGID=100 \
  -p 8501:8501 \
  -v /mnt/user/appdata/clipsai:/config \
  clipsai/webgui:latest bash
```

---

## 📈 **Performance Optimization**

### **💾 Resource Limits:**
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G        # Adjust based on your system
      cpus: '1.0'       # Adjust based on CPU cores
    reservations:
      memory: 512M
      cpus: '0.5'
```

### **🚀 Performance Tips:**
- **Use SSD cache** for upload directory
- **Limit upload size** to prevent disk filling
- **Regular cleanup** of temp files
- **Monitor container resources** via Unraid dashboard

---

## 🔒 **Security Considerations**

### **🛡️ Container Security:**
- ✅ **Non-root user** (nobody:users)
- ✅ **No new privileges** security option
- ✅ **Read-only root filesystem** (optional)
- ✅ **Resource limits** to prevent abuse

### **🌐 Network Security:**
- **Reverse proxy** recommended for external access
- **SSL termination** at proxy level
- **Firewall rules** for port 8501
- **VPN access** for remote usage

---

## 📚 **Additional Resources**

### **📖 Documentation:**
- [Unraid Docker Guide](https://docs.unraid.net/unraid-os/manual/docker-management/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Container Security](https://docs.docker.com/engine/security/)

### **🔗 Links:**
- **Web Interface:** http://your-unraid-ip:8501
- **Health Check:** http://your-unraid-ip:8501/api/health
- **Status API:** http://your-unraid-ip:8501/api/status

---

## 🎉 **Success Verification**

### **✅ Container Health:**
1. Container shows as "Started" in Unraid Docker tab
2. Health check returns HTTP 200
3. Web interface loads at http://your-unraid-ip:8501
4. Upload functionality works
5. Token validation works

### **✅ File Operations:**
1. Files upload successfully
2. Proper permissions on created files
3. Downloads work correctly
4. Logs are being written

### **✅ Integration:**
1. Unraid dashboard shows container stats
2. Volume mounts working correctly
3. Environment variables applied
4. Resource limits respected

---

## 🏆 **Deployment Complete!**

Your ClipsAI Web GUI is now ready for production use on Unraid 7.1.3 with:

✅ **Proper permissions** (PUID/PGID handling)  
✅ **Persistent storage** (volume mounts)  
✅ **Health monitoring** (health checks)  
✅ **Security hardening** (non-root, no-new-privileges)  
✅ **Unraid integration** (template support)  
✅ **Production logging** (comprehensive logs)  

**🌐 Access your ClipsAI Web GUI at: http://your-unraid-ip:8501**

---

*🐳 Container optimized for Unraid 7.1.3*  
*📅 Deployment Guide created: July 12, 2025*  
*🎯 Status: Production Ready*