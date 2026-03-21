# test_api_key.ps1 — исправленный

$uri = "http://127.0.0.1:8080/api/verify"
$headers = @{
    "X-API-Key"        = "dev-key-123"
    "Content-Type"     = "application/json"  # ← ВАЖНО!
}

# Читаем данные
$payload_json = Get-Content -Raw "app/licenses/lic_2026-03-21-001.json"
$signature = (Get-Content -Raw "app/licenses/lic_2026-03-21-001.sig").Trim()

# Формируем JSON
$body = @{
    payload   = $payload_json | ConvertFrom-Json
    signature = $signature
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -Headers $headers
Write-Host "`n✅ API Response:" -ForegroundColor Green
$response | Format-List