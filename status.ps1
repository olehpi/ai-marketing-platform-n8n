Write-Host ""
Write-Host "========== DOCKER ==========" -ForegroundColor Cyan

docker ps

Write-Host ""
Write-Host "========== OLLAMA ==========" -ForegroundColor Cyan

Get-Process ollama -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========== NGROK ===========" -ForegroundColor Cyan

Get-Process ngrok -ErrorAction SilentlyContinue