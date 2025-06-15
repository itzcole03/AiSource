Write-Host "🎯 Intelligent Port Synchronization Status" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Read backend config
$backendConfig = Get-Content 'backend_config.json' | ConvertFrom-Json
$frontendConfig = Get-Content 'public\backend_config.json' | ConvertFrom-Json

Write-Host "Backend running on port: $($backendConfig.backend_port)" -ForegroundColor Cyan
Write-Host "Frontend config port: $($frontendConfig.backend_port)" -ForegroundColor Cyan

if ($backendConfig.backend_port -eq $frontendConfig.backend_port) {
    Write-Host "✅ Port synchronization: PERFECT" -ForegroundColor Green
} else {
    Write-Host "❌ Port mismatch detected" -ForegroundColor Red
}

# Test endpoints
Write-Host "`nTesting endpoints on port $($backendConfig.backend_port):" -ForegroundColor Yellow

try {
    $lmstudio = Invoke-RestMethod -Uri "http://127.0.0.1:$($backendConfig.backend_port)/providers/lmstudio/models" -TimeoutSec 3
    Write-Host "✅ LM Studio: $($lmstudio.count) models" -ForegroundColor Green
} catch {
    Write-Host "❌ LM Studio: Failed" -ForegroundColor Red
}

try {
    $ollama = Invoke-RestMethod -Uri "http://127.0.0.1:$($backendConfig.backend_port)/providers/ollama/models" -TimeoutSec 3
    $ollamaCount = ($ollama.models | Measure-Object).Count
    Write-Host "✅ Ollama: $ollamaCount models" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama: Failed" -ForegroundColor Red
}

try {
    $status = Invoke-RestMethod -Uri "http://127.0.0.1:$($backendConfig.backend_port)/providers/status" -TimeoutSec 3
    Write-Host "✅ Provider Status: LM Studio ($($status.providers.lmstudio.status)), Ollama ($($status.providers.ollama.status))" -ForegroundColor Green
} catch {
    Write-Host "❌ Provider Status: Failed" -ForegroundColor Red
}

Write-Host "`n🚀 Ready for frontend!" -ForegroundColor Green
Write-Host "Frontend will auto-discover backend on port $($backendConfig.backend_port)" -ForegroundColor Cyan
Write-Host "Please refresh your browser - both LM Studio and Ollama should work!" -ForegroundColor Yellow
