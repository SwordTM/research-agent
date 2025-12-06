# Research Agent Development Environment Starter
# This script starts both the MCP server and Next.js development server

Write-Host "[*] Starting Research Agent Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Get the script directory (project root)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonDir = Join-Path $ProjectRoot "python"
$WebDir = Join-Path $ProjectRoot "research-agent-web"
$VenvPath = Join-Path $PythonDir "venv\Scripts\Activate.ps1"

# Check if Python virtual environment exists
if (-not (Test-Path $VenvPath)) {
    Write-Host "[ERROR] Virtual environment not found at: $VenvPath" -ForegroundColor Red
    Write-Host "Please create it first:" -ForegroundColor Yellow
    Write-Host "  cd python" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
$EnvFile = Join-Path $PythonDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "[WARNING] .env file not found at: $EnvFile" -ForegroundColor Yellow
    Write-Host "Please create it with your GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
}

# Check if node_modules exists
$NodeModules = Join-Path $WebDir "node_modules"
if (-not (Test-Path $NodeModules)) {
    Write-Host "[WARNING] node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    Push-Location $WebDir
    npm install
    Pop-Location
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Function to cleanup on exit
function Cleanup {
    Write-Host ""
    Write-Host "[*] Shutting down development environment..." -ForegroundColor Yellow
    
    # Kill MCP server if running
    if ($null -ne $McpProcess -and !$McpProcess.HasExited) {
        Write-Host "  Stopping MCP server..." -ForegroundColor Gray
        Stop-Process -Id $McpProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    # Kill Next.js server if running
    if ($null -ne $NextProcess -and !$NextProcess.HasExited) {
        Write-Host "  Stopping Next.js server..." -ForegroundColor Gray
        Stop-Process -Id $NextProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "[OK] Development environment stopped" -ForegroundColor Green
    exit
}

# Register cleanup on Ctrl+C
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Cleanup }
$null = Register-EngineEvent -SourceIdentifier ConsoleControl.CtrlC -Action { Cleanup }

try {
    # Start MCP Server
    Write-Host "[MCP] Starting MCP Server..." -ForegroundColor Cyan
    $McpProcess = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoExit", "-Command", "cd '$PythonDir'; & '$VenvPath'; python agent\mcp_server.py" `
        -PassThru `
        -WindowStyle Normal
    
    Write-Host "  [OK] MCP Server started (PID: $($McpProcess.Id))" -ForegroundColor Green
    Write-Host ""
    
    # Wait a moment for MCP server to initialize
    Start-Sleep -Seconds 2
    
    # Start Next.js Dev Server
    Write-Host "[WEB] Starting Next.js Development Server..." -ForegroundColor Cyan
    $NextProcess = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoExit", "-Command", "cd '$WebDir'; npm run dev" `
        -PassThru `
        -WindowStyle Normal
    
    Write-Host "  [OK] Next.js server started (PID: $($NextProcess.Id))" -ForegroundColor Green
    Write-Host ""
    
    # Display status
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  Development Environment Running!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  MCP Server:        Running (PID: $($McpProcess.Id))" -ForegroundColor White
    Write-Host "  Next.js Server:    http://localhost:3000" -ForegroundColor White
    Write-Host ""
    Write-Host "  Project Root:      $ProjectRoot" -ForegroundColor Gray
    Write-Host "  Python Dir:        $PythonDir" -ForegroundColor Gray
    Write-Host "  Web Dir:           $WebDir" -ForegroundColor Gray
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "TIPS:" -ForegroundColor Yellow
    Write-Host "  - Open http://localhost:3000 in your browser" -ForegroundColor White
    Write-Host "  - Check the MCP server window for Python logs" -ForegroundColor White
    Write-Host "  - Check the Next.js window for web server logs" -ForegroundColor White
    Write-Host "  - Press Ctrl+C here to stop both servers" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all servers..." -ForegroundColor Yellow
    
    # Wait for user to press Ctrl+C
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Check if processes are still running
        if ($McpProcess.HasExited) {
            Write-Host "[WARNING] MCP Server has stopped unexpectedly" -ForegroundColor Red
            break
        }
        if ($NextProcess.HasExited) {
            Write-Host "[WARNING] Next.js Server has stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
    
} catch {
    Write-Host "[ERROR] $_" -ForegroundColor Red
} finally {
    Cleanup
}
