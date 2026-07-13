$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      AI PLATFORM (INTERACTIVE MODE)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

New-Item -ItemType Directory -Force -Path ".\logs" | Out-Null

# -----------------------------
# Helpers
# -----------------------------

function Ask($msg) {
    do {
        $r = Read-Host "$msg (y/n)"
    } while ($r -ne "y" -and $r -ne "n")
    return $r -eq "y"
}

function Start-Service($name, $cmd) {
    Write-Host "$name started" -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd | Out-Null
}

function Get-NgrokUrl {
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -UseBasicParsing
        return $resp.tunnels[0].public_url
    }
    catch {
        return $null
    }
}

# -----------------------------
# REAL HEALTH CHECK (IMPORTANT)
# -----------------------------

function Assert-N8nReady {

    try {
        $resp = Invoke-WebRequest `
            -Uri "http://localhost:5678/healthz" `
            -UseBasicParsing `
            -TimeoutSec 3

        return ($resp.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

# -----------------------------
# [1/5] Docker check
# -----------------------------

Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow

cmd /c "docker info > .\logs\docker-check.log 2>&1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker is not running or is unavailable" -ForegroundColor Red
    Write-Host "See logs/docker-check.log" -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker is READY" -ForegroundColor Green

# -----------------------------
# [2/5] ngrok
# -----------------------------

Write-Host "[2/5] Starting ngrok..." -ForegroundColor Yellow
Start-Service "ngrok" "ngrok http 5678"

do {
    Start-Sleep 0.2
    try {
        $resp = Invoke-RestMethod "http://127.0.0.1:4040/api/tunnels"
        $ready = $resp.tunnels.Count -gt 0
    } catch {
        $ready = $false
    }
} while (-not $ready)

Write-Host "ngrok is READY" -ForegroundColor Green

# -----------------------------
# [3/5] Ollama
# -----------------------------

Write-Host "[3/5] Starting Ollama..." -ForegroundColor Yellow

$ollama = Ask "Start Ollama model qwen3.5:9b? (n = already running)"

if ($ollama) {
    Start-Service "ollama" "ollama run qwen3.5:9b"
    Start-Sleep 5
    Write-Host "Ollama started." -ForegroundColor Green
    if (-not (Ask "Continue?")) { exit }
} else {
    Write-Host "Skipping Ollama start." -ForegroundColor DarkYellow
}

# -----------------------------
# [4/5] Whisper
# -----------------------------

Write-Host "[4/5] Starting Whisper..." -ForegroundColor Yellow

$whisper = Ask "Start Whisper container?"

if ($whisper) {
    cmd /c "docker compose -f whisper-compose.yml up -d --remove-orphans >> .\logs\whisper.log 2>&1"
    Write-Host "Whisper started." -ForegroundColor Green
} else {
    Write-Host "Skipping Whisper." -ForegroundColor DarkYellow
}

if (-not (Ask "Continue?")) { exit }

# -----------------------------
# [5/5] n8n + Postgres
# -----------------------------

Write-Host "[5/5] Starting n8n + Postgres..." -ForegroundColor Yellow

cmd /c "docker compose up -d >> .\logs\n8n.log 2>&1"

$maxRetries = 100
$delaySec = 15

$spinner = @('|','/','-','\')

$ready = $false

for ($i = 0; $i -lt $maxRetries; $i++) {

    $frame = $spinner[$i % $spinner.Count]

    Write-Host -NoNewline "`r[$frame] Checking n8n /healthz... attempt $($i + 1)/$maxRetries"

    $ready = Assert-N8nReady

    if ($ready) {
        Write-Host "`r[OK] n8n is READY." -ForegroundColor Green
        break
    }

    Start-Sleep -Seconds $delaySec
}

if (-not $ready) {
    Write-Host "`r[✗] n8n failed to start in time.                              " -ForegroundColor Red
    exit 1
}

$url = Get-NgrokUrl
if (-not $url) { $url = "http://localhost:5678" }

Write-Host ""
Write-Host "n8n container is running." -ForegroundColor Green
Write-Host "n8n is still initializing in background (normal behavior)." -ForegroundColor Yellow
Write-Host ""
Write-Host "UI will be available here:" -ForegroundColor Cyan
Write-Host "$url" -ForegroundColor Yellow
Write-Host ""

# ONLY NOW USER DECIDES
if (-not (Ask "n8n is responding: GET /healthz 200 OK. Continue?")) { exit }

# -----------------------------
# DONE
# -----------------------------

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "       PLATFORM READY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "n8n      : $url"
Write-Host "Whisper  : http://localhost:9000/docs"
Write-Host "Postgres : localhost:5432"