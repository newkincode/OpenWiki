@echo off
setlocal

:: 가상환경 폴더 이름
set VENV_DIR=venv

:: Python이 설치되어 있는지 확인
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [⚠] Python이 설치되어 있지 않습니다. Chocolatey 확인 중...

    :: Chocolatey 확인
    where choco >nul 2>nul
    if %errorlevel% neq 0 (
        echo [⚠] Chocolatey가 설치되어 있지 않습니다. Chocolatey를 설치합니다...
        @powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "Set-ExecutionPolicy Bypass -Scope Process -Force; ^
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; ^
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        if %errorlevel% neq 0 (
            echo [❌] Chocolatey 설치 실패. 수동으로 설치하세요.
            exit /b 1
        )
    ) else (
        echo [✅] Chocolatey가 이미 설치되어 있습니다.
    )

    :: Chocolatey를 사용하여 Python 설치
    echo [🔄] Chocolatey를 이용하여 Python을 설치합니다...
    choco install python -y
    if %errorlevel% neq 0 (
        echo [❌] Python 설치 실패. 수동으로 설치하세요.
        exit /b 1
    )
) else (
    echo [✅] Python이 이미 설치되어 있습니다.
)

:: pip 최신 버전 업그레이드
echo [🔄] pip 최신 버전으로 업그레이드 중...
python -m pip install --upgrade pip

:: 가상환경 생성
if exist %VENV_DIR% (
    echo [✅] 가상환경(%VENV_DIR%)이 이미 존재합니다.
) else (
    echo [🔄] 가상환경(%VENV_DIR%)을 생성합니다...
    python -m venv %VENV_DIR%
)

:: 가상환경 활성화
echo [🔄] 가상환경을 활성화합니다...
call %VENV_DIR%\Scripts\activate

:: requirements.txt 확인 후 패키지 설치
if exist requirements.txt (
    echo [✅] requirements.txt 파일을 찾았습니다. 패키지를 설치합니다...
    pip install -r requirements.txt
) else (
    echo [⚠] requirements.txt 파일이 존재하지 않습니다. 패키지를 설치하지 않습니다.
)

echo [🎉] 모든 작업이 완료되었습니다!
echo [👉] 가상환경을 활성화하려면 'call %VENV_DIR%\Scripts\activate'을 실행하세요.

endlocal
pause
