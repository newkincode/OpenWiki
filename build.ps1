# PowerShell 실행 정책 변경 (관리자 권한 필요)
Set-ExecutionPolicy Bypass -Scope Process -Force

# 가상환경 폴더 이름
$venvDir = "venv"

# Python 확인
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "[⚠] Python이 설치되어 있지 않습니다. Chocolatey 확인 중..."

    # Chocolatey 확인
    $chocoCheck = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $chocoCheck) {
        Write-Host "[⚠] Chocolatey가 설치되어 있지 않습니다. 설치를 진행합니다..."
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    } else {
        Write-Host "[✅] Chocolatey가 이미 설치되어 있습니다."
    }

    # Chocolatey로 Python 설치
    Write-Host "[🔄] Chocolatey를 이용하여 Python을 설치합니다..."
    choco install python -y
} else {
    Write-Host "[✅] Python이 이미 설치되어 있습니다."
}

# pip 최신 버전 업그레이드
Write-Host "[🔄] pip 최신 버전으로 업그레이드 중..."
python -m pip install --upgrade pip

# 가상환경 생성
if (Test-Path $venvDir) {
    Write-Host "[✅] 가상환경 ($venvDir)이 이미 존재합니다."
} else {
    Write-Host "[🔄] 가상환경 ($venvDir)을 생성합니다..."
    python -m venv $venvDir
}

# 가상환경 활성화
Write-Host "[🔄] 가상환경을 활성화합니다..."
& .\$venvDir\Scripts\Activate.ps1

# requirements.txt 확인 후 패키지 설치
if (Test-Path "requirements.txt") {
    Write-Host "[✅] requirements.txt 파일을 찾았습니다. 패키지를 설치합니다..."
    pip install -r requirements.txt
} else {
    Write-Host "[⚠] requirements.txt 파일이 존재하지 않습니다. 패키지를 설치하지 않습니다."
}

Write-Host "[🎉] 모든 작업이 완료되었습니다!"
Write-Host "[👉] 가상환경을 활성화하려면 '.\$venvDir\Scripts\Activate.ps1'을 실행하세요."
