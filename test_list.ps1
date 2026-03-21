# test_list.ps1
$uri = "http://127.0.0.1:8080/api/list"
$response = Invoke-RestMethod -Uri $uri -Method Get
Write-Host "`n✅ Licenses list:" -ForegroundColor Green
$response | Format-List