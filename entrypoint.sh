#!/bin/bash
# Entrypoint script for Unraid 7.1.3 compatibility

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎬 ClipsAI Web GUI - Unraid Container Starting...${NC}"

# Default values for Unraid
PUID=${PUID:-99}
PGID=${PGID:-100}
UMASK=${UMASK:-022}
TZ=${TZ:-UTC}
PORT=${PORT:-5555}

echo -e "${YELLOW}📋 Container Configuration:${NC}"
echo -e "   PUID: ${PUID}"
echo -e "   PGID: ${PGID}"
echo -e "   UMASK: ${UMASK}"
echo -e "   TZ: ${TZ}"
echo -e "   PORT: ${PORT}"

# Set timezone
if [[ -n "$TZ" ]]; then
    echo -e "${BLUE}🌍 Setting timezone to: ${TZ}${NC}"
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
    echo $TZ > /etc/timezone
fi

# Set umask
echo -e "${BLUE}🔒 Setting umask to: ${UMASK}${NC}"
umask $UMASK

# Get current user info
CURRENT_UID=$(id -u nobody)
CURRENT_GID=$(id -g nobody)

echo -e "${YELLOW}👤 Current User Info:${NC}"
echo -e "   Current UID: ${CURRENT_UID}"
echo -e "   Current GID: ${CURRENT_GID}"
echo -e "   Target UID: ${PUID}"
echo -e "   Target GID: ${PGID}"

# Update user/group IDs if needed
if [[ "$CURRENT_UID" != "$PUID" ]] || [[ "$CURRENT_GID" != "$PGID" ]]; then
    echo -e "${BLUE}🔄 Updating user/group IDs...${NC}"
    
    # Update group
    if [[ "$CURRENT_GID" != "$PGID" ]]; then
        groupmod -g $PGID users
        echo -e "   Updated group ID to: ${PGID}"
    fi
    
    # Update user
    if [[ "$CURRENT_UID" != "$PUID" ]]; then
        usermod -u $PUID nobody
        echo -e "   Updated user ID to: ${PUID}"
    fi
    
    # Update file ownership
    echo -e "${BLUE}📁 Updating file ownership...${NC}"
    chown -R nobody:users /app /config /data 2>/dev/null || true
    
    echo -e "${GREEN}✅ User/group IDs updated successfully${NC}"
else
    echo -e "${GREEN}✅ User/group IDs already correct${NC}"
fi

# Ensure proper permissions on key directories
echo -e "${BLUE}🔐 Setting directory permissions...${NC}"
chmod 755 /app /config /data
chmod 755 /app/uploads 2>/dev/null || mkdir -p /app/uploads && chmod 755 /app/uploads
chmod 755 /app/logs 2>/dev/null || mkdir -p /app/logs && chmod 755 /app/logs

# Create config file if it doesn't exist
if [[ ! -f /config/clipsai.conf ]]; then
    echo -e "${BLUE}📝 Creating default config file...${NC}"
    cat > /config/clipsai.conf << 'EOF'
# ClipsAI Web GUI Configuration
# This file is automatically created by the container

# Server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=5555

# Upload settings
MAX_UPLOAD_SIZE=104857600  # 100MB in bytes
ALLOWED_EXTENSIONS=mp4,avi,mov,mkv,flv,wmv

# Paths
UPLOAD_DIR=/app/uploads
LOG_DIR=/app/logs
DATA_DIR=/data

# Default settings
DEFAULT_WHISPER_MODEL=base
DEFAULT_ASPECT_RATIO=9:16
DEFAULT_MIN_DURATION=15

# Created by ClipsAI container
CONTAINER_VERSION=3.0.0
CREATED=$(date)
EOF
    chown nobody:users /config/clipsai.conf
    echo -e "${GREEN}✅ Config file created at /config/clipsai.conf${NC}"
fi

# Create log directory structure
echo -e "${BLUE}📊 Setting up logging...${NC}"
mkdir -p /app/logs
touch /app/logs/clipsai.log
touch /app/logs/uploads.log
touch /app/logs/errors.log
chown -R nobody:users /app/logs

# Display startup information
echo -e "${GREEN}🚀 ClipsAI Web GUI Ready!${NC}"
echo -e "${YELLOW}📋 Container Information:${NC}"
echo -e "   Version: 3.0.0"
echo -e "   Port: ${PORT}"
echo -e "   Upload Directory: /app/uploads"
echo -e "   Config Directory: /config"
echo -e "   Data Directory: /data"
echo -e "   Logs Directory: /app/logs"

echo -e "${BLUE}🌐 Web Interface will be available at:${NC}"
echo -e "   http://your-unraid-ip:${PORT}"

echo -e "${YELLOW}📁 Volume Mounts (configure in Unraid):${NC}"
echo -e "   /config -> Container config storage"
echo -e "   /data -> User data and videos"
echo -e "   /app/uploads -> Temporary upload storage"

# Check if running as root and switch to nobody user
if [[ "$(id -u)" == "0" ]]; then
    echo -e "${BLUE}👤 Switching to nobody user...${NC}"
    exec gosu nobody "$@"
else
    echo -e "${GREEN}✅ Already running as non-root user${NC}"
    exec "$@"
fi