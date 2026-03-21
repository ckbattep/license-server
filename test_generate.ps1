# test_generate.ps1
$uri = "http://127.0.0.1:8080/api/generate"
$body = @{
    user     = "CitoLaw"
    product  = "License Server v1.0"
    features = @("api", "web")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json"
Write-Host "`n✅ Generated license:" -ForegroundColor Green
$response | Format-List