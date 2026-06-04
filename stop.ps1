Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "      STOPPING AI PLATFORM" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Whisper
docker compose -f whisper-compose.yml down

# n8n + postgres
docker compose down

# ngrok
Get-Process ngrok -ErrorAction SilentlyContinue |
    Stop-Process -Force

# Ollama
Get-Process ollama -ErrorAction SilentlyContinue |
    Stop-Process -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "       PLATFORM STOPPED" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red