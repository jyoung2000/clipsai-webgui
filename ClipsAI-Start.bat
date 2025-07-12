@echo off
title ClipsAI Web GUI - AI Video Processing
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                  🎬 ClipsAI Web GUI                      ║
echo  ║        AI-Powered Video Transcription & Processing       ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not installed!
    echo.
    echo 📥 Please install Docker Desktop for Windows:
    echo    https://www.docker.com/products/docker-desktop
    echo.
    echo After installation:
    echo 1. Start Docker Desktop
    echo 2. Wait for Docker to start completely
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

REM Check if Docker is running
echo 🔍 Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running!
    echo.
    echo 🚀 Please start Docker Desktop first:
    echo 1. Look for Docker icon in system tray
    echo 2. Right-click and select "Start Docker Desktop"
    echo 3. Wait for Docker to start (may take 1-2 minutes)
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running!
echo.

REM Stop existing container if running
echo 🧹 Cleaning up previous instances...
docker stop clipsai-webgui >nul 2>&1
docker rm clipsai-webgui >nul 2>&1

REM Pull latest image
echo 📦 Downloading latest ClipsAI Web GUI...
echo    (This may take a few minutes on first run)
docker pull jyoung2000/clipsai-webgui:latest
if %errorlevel% neq 0 (
    echo ❌ Failed to download ClipsAI Web GUI image!
    echo    Please check your internet connection.
    pause
    exit /b 1
)

REM Create data directories
if not exist "%USERPROFILE%\ClipsAI\config" mkdir "%USERPROFILE%\ClipsAI\config"
if not exist "%USERPROFILE%\ClipsAI\data" mkdir "%USERPROFILE%\ClipsAI\data"
if not exist "%USERPROFILE%\ClipsAI\uploads" mkdir "%USERPROFILE%\ClipsAI\uploads"
if not exist "%USERPROFILE%\ClipsAI\logs" mkdir "%USERPROFILE%\ClipsAI\logs"

REM Start container
echo 🚀 Starting ClipsAI Web GUI...
docker run -d ^
    --name clipsai-webgui ^
    --restart unless-stopped ^
    -p 5555:5555 ^
    -v "%USERPROFILE%\ClipsAI\config:/config" ^
    -v "%USERPROFILE%\ClipsAI\data:/data" ^
    -v "%USERPROFILE%\ClipsAI\uploads:/app/uploads" ^
    -v "%USERPROFILE%\ClipsAI\logs:/app/logs" ^
    jyoung2000/clipsai-webgui:latest

if %errorlevel% neq 0 (
    echo ❌ Failed to start ClipsAI Web GUI!
    echo    Please check Docker logs for details.
    pause
    exit /b 1
)

REM Wait for container to start
echo 📊 Waiting for ClipsAI Web GUI to initialize...
timeout /t 5 /nobreak >nul

REM Check if container is healthy
echo 🔍 Checking application health...
for /l %%i in (1,1,30) do (
    curl -s http://localhost:5555/api/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ ClipsAI Web GUI is ready!
        goto :healthy
    )
    timeout /t 1 /nobreak >nul
)

echo ⚠️  ClipsAI Web GUI may still be starting...
:healthy

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                   🎉 SUCCESS!                            ║
echo  ║                                                           ║
echo  ║   ClipsAI Web GUI is now running on your computer!       ║
echo  ║                                                           ║
echo  ║   🌐 Web Interface: http://localhost:5555                ║
echo  ║   📁 Your Files: %USERPROFILE%\ClipsAI\              ║
echo  ║                                                           ║
echo  ║   Features Available:                                     ║
echo  ║   • 🎬 Video Upload (Drag & Drop)                       ║
echo  ║   • 🎤 AI Transcription                                 ║
echo  ║   • 👥 Speaker Diarization                              ║
echo  ║   • 🔍 Smart Clip Finding                               ║
echo  ║   • ✂️  Video Trimming & Resizing                       ║
echo  ║   • ⬇️  Download Processed Videos                        ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

REM Open browser
echo 🌐 Opening web interface...
timeout /t 2 /nobreak >nul
start http://localhost:5555

echo.
echo 📋 Management Options:
echo    [V] View container logs
echo    [S] Stop ClipsAI Web GUI  
echo    [R] Restart ClipsAI Web GUI
echo    [O] Open web interface again
echo    [Q] Quit (leave running in background)
echo.

:menu
set /p choice="Enter your choice: "

if /i "%choice%"=="V" (
    echo.
    echo 📊 Recent logs (press Ctrl+C to return to menu):
    docker logs --tail 50 -f clipsai-webgui
    goto :menu
)

if /i "%choice%"=="S" (
    echo 🛑 Stopping ClipsAI Web GUI...
    docker stop clipsai-webgui
    docker rm clipsai-webgui
    echo ✅ ClipsAI Web GUI stopped successfully.
    echo    Your data is saved in: %USERPROFILE%\ClipsAI\
    pause
    exit /b 0
)

if /i "%choice%"=="R" (
    echo 🔄 Restarting ClipsAI Web GUI...
    docker restart clipsai-webgui
    timeout /t 3 /nobreak >nul
    echo ✅ ClipsAI Web GUI restarted!
    start http://localhost:5555
    goto :menu
)

if /i "%choice%"=="O" (
    start http://localhost:5555
    echo 🌐 Web interface opened in your browser!
    goto :menu
)

if /i "%choice%"=="Q" (
    echo 📱 ClipsAI Web GUI will continue running in the background.
    echo    Access it anytime at: http://localhost:5555
    echo    Run this script again to manage the application.
    echo.
    echo 💡 To stop it later, run this script and choose [S]top.
    pause
    exit /b 0
)

echo ❌ Invalid choice. Please try again.
goto :menu