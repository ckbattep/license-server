# test_integration.ps1
# Запускать из: C:\IT\CitoLaw\license-server

$ErrorActionPreference = "Continue"

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║         🔐 License Server — Integration Test v1.0          ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# 📊 Шкала прогресса (0/3 → 3/3)
function Show-Progress {
    param(
        [int]$Current,
        [int]$Total = 3,
        [string]$Label,
        [string]$Status = "⏳"
    )
    $percent = [math]::Round(($Current / $Total) * 100)
    $barLength = 30
    $filled = [math]::Round($percent / (100 / $barLength))
    $empty = $barLength - $filled

    Write-Host "[$Status] $Label" -ForegroundColor Yellow -NoNewline
    Write-Host " | " -NoNewline
    Write-Host ("█" * $filled) -ForegroundColor Green -NoNewline
    Write-Host ("░" * $empty) -NoNewline
    Write-Host " $percent% ($Current/$Total)" -ForegroundColor Cyan
}

# =========================
# 🧪 ЭТАП 1: Генерация лицензии и подпись
# =========================
Write-Host "`n[1] 📄 Генерация лицензии и подпись`n" -ForegroundColor Cyan

Show-Progress -Current 1 -Label "Создание license.json"

python app/tests/test_integration.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Тест провален!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n✅ Лицензия создана и подписана" -ForegroundColor Green

Show-Progress -Current 2 -Label "Подпись license.json"

# =========================
# 🧪 ЭТАП 2: Верификация подписи
# =========================
Write-Host "`n[2] 🔍 Верификация подписи`n" -ForegroundColor Cyan

Show-Progress -Current 3 -Label "verify_signature()"

python app/tests/test_integration.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Тест провален!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n✅ Подпись верифицирована" -ForegroundColor Green

# =========================
# 🎉 Финал
# =========================
Write-Host @"
╔════════════════════════════════════════════════════════════╗
║         ✅ Интеграционный тест пройден!                    ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

Write-Host "`n[ℹ️] Файлы:" -ForegroundColor Cyan
Write-Host "  • app/licenses/lic_2026-03-21-001.json" -ForegroundColor Yellow
Write-Host "  • app/licenses/lic_2026-03-21-001.sig" -ForegroundColor Yellow

Write-Host "`n[ℹ️] Следующий шаг: API-тест (POST /api/verify)" -ForegroundColor Cyan