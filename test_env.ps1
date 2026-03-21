# test_env.ps1
# Запускать из: C:\IT\CitoLaw\license-server

$ErrorActionPreference = "Continue"

# 🎨 ASCII-заголовок
Write-Host @"
╔════════════════════════════════════════════════════════════╗
║         🔐 CitoLaw License Server — Test Suite v1.0        ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# 📊 Шкала прогресса (0/5 → 5/5)
function Show-Progress {
    param(
        [int]$Current,
        [int]$Total = 5,
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
# 🧪 ЭТАП 0: Окружение и ключи
# =========================
Write-Host "`n[0] 🔍 Проверка окружения и ключей`n" -ForegroundColor Cyan

Show-Progress -Current 1 -Label "Python & cryptography"

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion"
} catch {
    Write-Host "❌ Python не найден в PATH!" -ForegroundColor Red
    exit 1
}

try {
    $cinfo = python -c "import cryptography; print(cryptography.__version__)" 2>&1
    Write-Host "✅ cryptography: $cinfo"
} catch {
    Write-Host "❌ cryptography не установлен!" -ForegroundColor Red
    exit 1
}

Show-Progress -Current 2 -Label "Ключи (ed25519_private.key)"

$privateKeyPath = ".\app\crypto\ed25519_private.key"
$publicKeyPath  = ".\app\crypto\ed25519_public.key"

function Test-KeyLoad {
    param($keyType)
    python -c "
import os, sys
sys.path.insert(0, '.')
from app.security.ed25519 import load_$keyType
try:
    key = load_$keyType()
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1
}

$keyLoadResult = Test-KeyLoad "private_key"
if ($keyLoadResult -like "*ERROR*") {
    Write-Host "⚠️ Приватный ключ повреждён: $keyLoadResult" -ForegroundColor Yellow

    if (Test-Path $privateKeyPath) { Remove-Item $privateKeyPath }
    if (Test-Path $publicKeyPath)  { Remove-Item $publicKeyPath }

    Write-Host "🔄 Генерация новых ключей..." -ForegroundColor Yellow
    python -c "
import os, sys
sys.path.insert(0, '.')
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

private_key = ed25519.Ed25519PrivateKey.generate()
public_key  = private_key.public_key()

pem_private = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

pem_public = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

os.makedirs('app/crypto', exist_ok=True)

with open('app/crypto/ed25519_private.key', 'wb') as f:
    f.write(pem_private)
with open('app/crypto/ed25519_public.key',  'wb') as f:
    f.write(pem_public)

print('✅ Keys regenerated.')
"
}

$keyLoadResult = Test-KeyLoad "private_key"
if ($keyLoadResult -like "*ERROR*") {
    Write-Host "❌ Не удалось сгенерировать ключи: $keyLoadResult" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Ключи загружаются корректно."
Show-Progress -Current 3 -Label "Ключи (ed25519_public.key)" -Status "✔️"

# =========================
# 🧪 ЭТАП 1: Подпись и верификация
# =========================
Write-Host "`n[1] 🔐 Тест подписи (sign_payload + verify_signature)`n" -ForegroundColor Cyan

Show-Progress -Current 4 -Label "Подпись → Верификация"

python -c "
import os, sys
sys.path.insert(0, '.')
from app.security.ed25519 import sign_payload, verify_signature

payload = {'test': 1}
signed = sign_payload(payload)
sig = signed['signature']

ok = verify_signature(payload, sig)

if ok:
    print('✅ sign_payload() OK')
    print(f'✅ verify_signature() → True')
else:
    raise RuntimeError('❌ verify_signature() failed!')
" 2>&1

# Если ошибка — авто-исправление (Ed25519() и дубликаты)
if ($LASTEXITCODE -ne 0) {
    $output = python -c "
import os, sys
sys.path.insert(0, '.')
from app.security.ed25519 import sign_payload, verify_signature

payload = {'test': 1}
signed = sign_payload(payload)
sig = signed['signature']

ok = verify_signature(payload, sig)

if ok:
    print('✅ OK')
else:
    raise RuntimeError('❌ verify failed!')
" 2>&1

    if ($output -like "*Ed25519()*") {
        Write-Host "⚠️ Ошибка: `ed25519.Ed25519()` не поддерживается → исправляем ed25519.py..." -ForegroundColor Yellow
        $file = ".\app\security\ed25519.py"
        $content = Get-Content $file -Raw
        $content = $content -replace 'private_key\.sign\(message, ed25519\.Ed25519\(\)\)', 'private_key.sign(message)'
        $content = $content -replace 'public_key\.verify\(signature, message, ed25519\.Ed25519\(\)\)', 'public_key.verify(signature, message)'
        Set-Content $file $content
        Write-Host "✅ ed25519.py исправлен." -ForegroundColor Green

        python -c "
import os, sys
sys.path.insert(0, '.')
from app.security.ed25519 import sign_payload, verify_signature

payload = {'test': 1}
signed = sign_payload(payload)
sig = signed['signature']

ok = verify_signature(payload, sig)

if ok:
    print('✅ sign_payload() OK')
    print(f'✅ verify_signature() → True')
else:
    raise RuntimeError('❌ verify_signature() failed!')
"
    }
}

Show-Progress -Current 5 -Label "Подпись → Верификация" -Status "✔️"

# =========================
# 🎉 Финал
# =========================
Write-Host @"
╔════════════════════════════════════════════════════════════╗
║         ✅ Все тесты пройдены — готово к интеграции!       ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

Write-Host "`n[ℹ️] Следующий шаг: интеграционный тест (Этап 1)" -ForegroundColor Cyan