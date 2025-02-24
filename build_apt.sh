#!/bin/bash

# 원하는 가상환경 폴더 이름
VENV_DIR="venv"

# Python 확인
if command -v python3 &>/dev/null; then
    echo "✅ Python이 이미 설치되어 있습니다."
else
    echo "⚠️ Python이 설치되어 있지 않습니다. apt를 이용하여 설치합니다..."

    # apt 패키지 목록 업데이트 및 Python 설치
    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip
fi

# pip 최신 버전으로 업그레이드
echo "pip를 최신 버전으로 업그레이드합니다..."
python3 -m pip install --upgrade pip

# 가상환경 생성
if [ -d "$VENV_DIR" ]; then
    echo "가상환경($VENV_DIR)이 이미 존재합니다."
else
    echo "가상환경($VENV_DIR)을 생성합니다..."
    python3 -m venv $VENV_DIR
fi

# 가상환경 활성화
echo "가상환경을 활성화합니다..."
source $VENV_DIR/bin/activate

# requirements.txt 파일 확인 후 패키지 설치
if [ -f "requirements.txt" ]; then
    echo "requirements.txt 파일을 찾았습니다. 패키지를 설치합니다..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt 파일이 존재하지 않습니다. 패키지를 설치하지 않습니다."
fi

echo "설치가 완료되었습니다!"
echo "가상환경을 활성화하려면 'source $VENV_DIR/bin/activate'를 실행하세요."
