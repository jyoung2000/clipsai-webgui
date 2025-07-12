# ClipsAI Web GUI - PowerShell Launcher
# This script provides a more Windows-native experience

param(
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Install,
    [switch]$Uninstall
)

# Set execution policy for current session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Configuration
$AppName = "ClipsAI Web GUI"
$ContainerName = "clipsai-webgui"
$ImageName = "jyoung2000/clipsai-webgui:latest"
$Port = "5555"
$WebUrl = "http://localhost:$Port"
$DataDir = "$env:USERPROFILE\ClipsAI"

# Colors for output
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

# Functions
function Write-Banner {
    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║                  🎬 ClipsAI Web GUI                      ║" -ForegroundColor Cyan
    Write-Host "  ║        AI-Powered Video Transcription & Processing       ║" -ForegroundColor Cyan
    Write-Host "  ╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Test-DockerInstalled {
    try {
        $null = docker --version 2>$null
        return $true
    }
    catch {
        return $false
    }
}

function Test-DockerRunning {
    try {
        $null = docker info 2>$null
        return $true
    }
    catch {
        return $false
    }
}

function Install-Application {
    Write-Banner
    Write-Host "🔧 Installing ClipsAI Web GUI..." -ForegroundColor Yellow
    
    # Check Docker
    if (-not (Test-DockerInstalled)) {
        Write-Host "❌ Docker Desktop is not installed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "📥 Please install Docker Desktop for Windows:" -ForegroundColor White
        Write-Host "   https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "After installation:" -ForegroundColor White
        Write-Host "1. Start Docker Desktop" -ForegroundColor White
        Write-Host "2. Wait for Docker to start completely" -ForegroundColor White
        Write-Host "3. Run this script again" -ForegroundColor White
        return $false
    }
    
    if (-not (Test-DockerRunning)) {
        Write-Host "❌ Docker Desktop is not running!" -ForegroundColor Red
        Write-Host "🚀 Please start Docker Desktop and try again." -ForegroundColor Yellow
        return $false
    }
    
    # Create data directories
    Write-Host "📁 Creating data directories..." -ForegroundColor White
    @("config", "data", "uploads", "logs") | ForEach-Object {
        $dir = Join-Path $DataDir $_
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    # Pull image
    Write-Host "📦 Downloading ClipsAI Web GUI image..." -ForegroundColor White
    docker pull $ImageName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Installation completed successfully!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Installation failed!" -ForegroundColor Red
        return $false
    }
}

function Start-Application {
    Write-Banner
    Write-Host "🚀 Starting ClipsAI Web GUI..." -ForegroundColor Yellow
    
    # Stop existing container
    docker stop $ContainerName 2>$null | Out-Null
    docker rm $ContainerName 2>$null | Out-Null
    
    # Start new container
    $cmd = @(
        "run", "-d",
        "--name", $ContainerName,
        "--restart", "unless-stopped",
        "-p", "$Port`:$Port",
        "-v", "$DataDir\config:/config",
        "-v", "$DataDir\data:/data", 
        "-v", "$DataDir\uploads:/app/uploads",
        "-v", "$DataDir\logs:/app/logs",
        $ImageName
    )
    
    docker @cmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "📊 Waiting for application to start..." -ForegroundColor White
        Start-Sleep -Seconds 5
        
        # Test health
        for ($i = 1; $i -le 30; $i++) {
            try {
                $response = Invoke-RestMethod -Uri "$WebUrl/api/health" -TimeoutSec 2 -ErrorAction Stop
                Write-Host "✅ ClipsAI Web GUI is ready!" -ForegroundColor Green
                Write-Host ""
                Write-Host "  ╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
                Write-Host "  ║                   🎉 SUCCESS!                            ║" -ForegroundColor Green
                Write-Host "  ║                                                           ║" -ForegroundColor Green
                Write-Host "  ║   ClipsAI Web GUI is now running!                        ║" -ForegroundColor Green
                Write-Host "  ║                                                           ║" -ForegroundColor Green
                Write-Host "  ║   🌐 Web Interface: $WebUrl                ║" -ForegroundColor Green
                Write-Host "  ║   📁 Your Files: $DataDir              ║" -ForegroundColor Green
                Write-Host "  ╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
                
                # Open browser
                Write-Host "🌐 Opening web interface..." -ForegroundColor White
                Start-Process $WebUrl
                return $true
            }
            catch {
                Start-Sleep -Seconds 1
            }
        }
        
        Write-Host "⚠️ Application started but may still be initializing..." -ForegroundColor Yellow
        Write-Host "🌐 Try opening: $WebUrl" -ForegroundColor Cyan
        return $true
    } else {
        Write-Host "❌ Failed to start ClipsAI Web GUI!" -ForegroundColor Red
        return $false
    }
}

function Stop-Application {
    Write-Host "🛑 Stopping ClipsAI Web GUI..." -ForegroundColor Yellow
    docker stop $ContainerName 2>$null | Out-Null
    docker rm $ContainerName 2>$null | Out-Null
    Write-Host "✅ ClipsAI Web GUI stopped successfully." -ForegroundColor Green
    Write-Host "📁 Your data is saved in: $DataDir" -ForegroundColor White
}

function Get-ApplicationStatus {
    Write-Banner
    Write-Host "📊 ClipsAI Web GUI Status:" -ForegroundColor Yellow
    Write-Host ""
    
    # Docker status
    if (Test-DockerInstalled) {
        Write-Host "✅ Docker Desktop: Installed" -ForegroundColor Green
        if (Test-DockerRunning) {
            Write-Host "✅ Docker Service: Running" -ForegroundColor Green
        } else {
            Write-Host "❌ Docker Service: Not Running" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Docker Desktop: Not Installed" -ForegroundColor Red
    }
    
    # Container status
    $containerStatus = docker ps --filter "name=$ContainerName" --format "{{.Status}}" 2>$null
    if ($containerStatus) {
        Write-Host "✅ ClipsAI Container: Running ($containerStatus)" -ForegroundColor Green
        Write-Host "🌐 Web Interface: $WebUrl" -ForegroundColor Cyan
    } else {
        Write-Host "❌ ClipsAI Container: Not Running" -ForegroundColor Red
    }
    
    # Data directory
    if (Test-Path $DataDir) {
        Write-Host "✅ Data Directory: $DataDir" -ForegroundColor Green
    } else {
        Write-Host "❌ Data Directory: Not Created" -ForegroundColor Red
    }
}

function Show-Menu {
    Write-Banner
    Write-Host "📋 Management Options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] Start ClipsAI Web GUI" -ForegroundColor White
    Write-Host "  [2] Stop ClipsAI Web GUI" -ForegroundColor White  
    Write-Host "  [3] Check Status" -ForegroundColor White
    Write-Host "  [4] Open Web Interface" -ForegroundColor White
    Write-Host "  [5] View Logs" -ForegroundColor White
    Write-Host "  [6] Install/Update" -ForegroundColor White
    Write-Host "  [Q] Quit" -ForegroundColor White
    Write-Host ""
    
    do {
        $choice = Read-Host "Enter your choice"
        
        switch ($choice.ToUpper()) {
            "1" { 
                if (-not (Install-Application)) { break }
                Start-Application 
            }
            "2" { Stop-Application }
            "3" { Get-ApplicationStatus }
            "4" { Start-Process $WebUrl }
            "5" { 
                Write-Host "📊 Recent logs (press Ctrl+C to return):" -ForegroundColor White
                docker logs --tail 50 -f $ContainerName 
            }
            "6" { Install-Application }
            "Q" { 
                Write-Host "👋 Goodbye!" -ForegroundColor Green
                exit 
            }
            default { 
                Write-Host "❌ Invalid choice. Please try again." -ForegroundColor Red 
            }
        }
        
        Write-Host ""
        Write-Host "Press any key to continue..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Show-Menu
    } while ($true)
}

# Main execution
if ($Install) {
    Install-Application
} elseif ($Start) {
    if (-not (Install-Application)) { exit 1 }
    Start-Application
} elseif ($Stop) {
    Stop-Application
} elseif ($Status) {
    Get-ApplicationStatus
} elseif ($Uninstall) {
    Stop-Application
    Write-Host "🗑️ Uninstalling ClipsAI Web GUI..." -ForegroundColor Yellow
    docker rmi $ImageName 2>$null | Out-Null
    Write-Host "✅ ClipsAI Web GUI uninstalled." -ForegroundColor Green
    Write-Host "📁 Data preserved in: $DataDir" -ForegroundColor White
} else {
    Show-Menu
}