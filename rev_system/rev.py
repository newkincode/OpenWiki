import hashlib
import json
from datetime import datetime
import pytz

def generate_revision_id(content: dict, timestamp: str) -> str:
    """문서 내용 + 타임스탬프를 SHA-256으로 변환하여 리비전 ID 생성"""
    content_str = json.dumps(content, sort_keys=True)  # 정렬하여 일관성 유지
    data = f"{content_str} {timestamp}".encode("utf-8")
    sha256_hash = hashlib.sha256(data).hexdigest()
    return sha256_hash  # 앞 7자만 사용 (Git 스타일)

def new_timestamp() -> str:
    utc_timezone = pytz.utc
    timestamp = datetime.now(utc_timezone).isoformat()  # UTC 타임스탬프
    return timestamp

# 테스트 예제
doc_content = {
    "title": "위키 엔진",
    "body": "위키 엔진을 개발하는 중입니다.",
    "author": "user123"
}
