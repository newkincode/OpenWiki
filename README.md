# OpenWiki

OpenWiki는 Python과 Flask를 기반으로 한 위키 엔진입니다.

## 주요 기능

- 마크다운 문법 지원
- 문서 변경 이력 관리
- 문서 간 링크 (`[[문서명]]`)
- 문서 검색 (제목, 내용, 태그)
- 사용자별 기여 추적
- 네임스페이스 지원

## 프로젝트 구조

```
OpenWiki/
├── main.py                 # Flask 애플리케이션 메인 파일
├── parser/                 # 문서 파싱 관련 모듈
│   ├── __init__.py
│   └── parser.py          # OPWI 파일 파서
├── rev_system/            # 문서 관리 시스템
│   ├── __init__.py
│   └── document.py        # Document 및 DocumentManager 클래스
├── static/                # 정적 파일
│   ├── css/
│   │   └── style.css     # 스타일시트
│   └── js/
│       └── search.js     # 검색 기능 스크립트
├── templates/             # HTML 템플릿
│   ├── base.html         # 기본 템플릿
│   ├── edit.html         # 문서 편집 페이지
│   ├── create.html       # 문서 생성 페이지
│   ├── history.html      # 변경 이력 페이지
│   ├── search.html       # 검색 결과 페이지
│   └── 404.html          # 404 오류 페이지
├── pages/                # 위키 문서 저장소
│   └── main/            # 메인 네임스페이스
│       └── *.opwi       # 위키 문서 파일들
└── index/               # 문서 인덱스
    └── document_index.json  # 문서 메타데이터 인덱스
```

## OPWI 파일 구조

OpenWiki는 `.opwi` 확장자를 가진 특별한 파일 형식을 사용합니다:

```
DOC:[UUID]                # 문서 고유 ID (UUID v4)
META:[JSON 메타데이터]     # 문서 메타데이터 (제목, 생성일, 태그 등)
REVUSER:[사용자]:[IP]     # 수정한 사용자 정보
REVBLOCK:START           # 변경사항 블록 시작
CHANGES:[변경내용 JSON]   # 변경 내용 (추가/삭제/수정)
REVBLOCK:END            # 변경사항 블록 끝
```

### 변경사항 형식

변경사항은 다음과 같은 형식으로 기록됩니다:
- `+줄번호|시작|끝:내용` : 내용 추가
- `-줄번호|시작|끝:내용` : 내용 삭제
- `=줄번호|시작|끝:내용` : 내용 수정

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/FamilyMink5/OpenWiki.git
cd OpenWiki
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. 서버 실행:
```bash
python main.py
```

## 사용 방법

1. 문서 생성:
   - "새 문서" 버튼 클릭
   - 제목과 내용 입력
   - 마크다운 문법 사용 가능

2. 문서 편집:
   - 문서 페이지에서 "편집" 버튼 클릭
   - 내용 수정 후 저장

3. 문서 링크:
   - `[[문서명]]` 형식으로 다른 문서 링크
   - 존재하지 않는 문서 링크 시 자동으로 생성 페이지로 이동

4. 문서 검색:
   - 상단 검색창에서 검색어 입력
   - 제목, 내용, 태그 기반 검색 지원

5. 변경 이력:
   - 문서 페이지에서 "역사" 버튼 클릭
   - 모든 변경사항과 기여자 확인 가능

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 