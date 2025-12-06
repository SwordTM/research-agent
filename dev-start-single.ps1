# Research Agent - Single Terminal Development Starter
# This script runs both servers in the same terminal with combined output

Write-Host "[*] Starting Research Agent (Single Terminal Mode)..." -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonDir = Join-Path $ProjectRoot "python"
$WebDir = Join-Path $ProjectRoot "research-agent-web"
$VenvActivate = Join-Path $PythonDir "venv\Scripts\Activate.ps1"

# Validation checks
if (-not (Test-Path $VenvActivate)) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: cd python; python -m venv venv; pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path (Join-Path $PythonDir ".env"))) {
    Write-Host "[WARNING] .env file not found in python directory" -ForegroundColor Yellow
}

# Start MCP Server in background job
Write-Host "[MCP] Starting MCP Server..." -ForegroundColor Cyan
$McpJob = Start-Job -ScriptBlock {
    param($PythonDir, $VenvActivate)
    Set-Location $PythonDir
    & $VenvActivate
    python agent\mcp_server.py
} -ArgumentList $PythonDir, $VenvActivate

Write-Host "  [OK] MCP Server job started (ID: $($McpJob.Id))" -ForegroundColor Green
Start-Sleep -Seconds 2

# Start Next.js in background job
Write-Host "[WEB] Starting Next.js Server..." -ForegroundColor Cyan
$NextJob = Start-Job -ScriptBlock {
    param($WebDir)
    Set-Location $WebDir
    npm run dev
} -ArgumentList $WebDir

Write-Host "  [OK] Next.js job started (ID: $($NextJob.Id))" -ForegroundColor Green
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Both servers are starting..." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Next.js will be available at: http://localhost:3000" -ForegroundColor White
Write-Host "  MCP Server is running in the background" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers..." -ForegroundColor Yellow
Write-Host ""

try {
    # Monitor both jobs and display output
    while ($true) {
        # Get MCP output
        $mcpOutput = Receive-Job -Job $McpJob
        if ($mcpOutput) {
            Write-Host "[MCP] $mcpOutput" -ForegroundColor Blue
        }
        
        # Get Next.js output
        $nextOutput = Receive-Job -Job $NextJob
        if ($nextOutput) {
            Write-Host "[Next.js] $nextOutput" -ForegroundColor Green
        }
        
        # Check if jobs are still running
        if ($McpJob.State -eq 'Failed' -or $McpJob.State -eq 'Stopped') {
            Write-Host "[ERROR] MCP Server stopped: $($McpJob.State)" -ForegroundColor Red
            break
        }
        if ($NextJob.State -eq 'Failed' -or $NextJob.State -eq 'Stopped') {
            Write-Host "[ERROR] Next.js Server stopped: $($NextJob.State)" -ForegroundColor Red
            break
        }
        
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host ""
    Write-Host "[*] Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $McpJob -ErrorAction SilentlyContinue
    Stop-Job -Job $NextJob -ErrorAction SilentlyContinue
    Remove-Job -Job $McpJob -Force -ErrorAction SilentlyContinue
    Remove-Job -Job $NextJob -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Servers stopped" -ForegroundColor Green
}
