import json
import os
import uuid
from datetime import datetime
import difflib

class Document:
    def __init__(self, title: str, namespace: str = "main"):
        self.doc_id = str(uuid.uuid4())
        self.title = title
        self.namespace = namespace
        self.created_at = datetime.now().isoformat()
        self.tags = []
        self.category = ""
        self.content = ""
        self.contributors = set()
        self.revisions = []
    
    def add_content(self, content: str, username: str, ip_address: str):
        """문서에 내용을 추가합니다."""
        self.contributors.add(username)
        
        # 마크다운 문서로 저장
        self.content = content
        
        changes = [{
            f"+0|0|{len(content)}": content
        }]
        
        revision = {
            "doc_id": self.doc_id,
            "username": username,
            "ip_address": ip_address,
            "timestamp": datetime.now().isoformat(),
            "changes": changes
        }
        self.revisions.append(revision)
        
        return revision
    
    def update_content(self, content: str, username: str, ip_address: str):
        """문서 내용을 업데이트하며 변경 사항을 정확하게 감지"""
        self.contributors.add(username)
        
        # 변경 사항 계산
        changes = self.diff_lines(self.content, content)

        # 변경 사항이 없으면 저장하지 않음
        if not changes:
            return {"message": "NO_CHANGE"}

        revision = {
            "doc_id": self.doc_id,
            "username": username,
            "ip_address": ip_address,
            "timestamp": datetime.now().isoformat(),
            "changes": changes
        }
        self.revisions.append(revision)

        # 내용 업데이트
        self.content = content
        
        return revision

    def diff_lines(self, old_text: str, new_text: str):
        """기존 텍스트와 새 텍스트의 변경 사항을 감지하여 리스트 반환"""
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        differ = difflib.Differ()
        diff_result = list(differ.compare(old_lines, new_lines))
        
        changes = []
        for i, line in enumerate(diff_result):
            if line.startswith("+ "):  # 추가된 줄
                changes.append({f"+{i}|{len(line[2:])}": line[2:]})
            elif line.startswith("- "):  # 삭제된 줄
                changes.append({f"-{i}|{len(line[2:])}": line[2:]})
            elif line.startswith("? "):  # 수정된 줄 (추가 & 삭제가 모두 포함될 경우)
                continue

        return changes
    
    def to_opwi(self) -> str:
        """문서를 OPWI 형식으로 변환합니다."""
        meta = {
            "title": self.title,
            "created_at": self.created_at,
            "tags": self.tags,
            "category": self.category,
            "namespace": self.namespace
        }
        
        content = [
            f"DOC:{self.doc_id}",
            f"META:{json.dumps(meta, ensure_ascii=False)}"
        ]
        
        # 모든 리비전 추가
        for revision in self.revisions:
            content.extend([
                f"REVUSER:{revision['username']}:{revision['ip_address']}",
                "REVBLOCK:START",
                f"CHANGES:{json.dumps(revision['changes'], ensure_ascii=False)}",
                "REVBLOCK:END"
            ])
        
        return "\n".join(content)
    
    @classmethod
    def from_opwi(cls, content: str) -> 'Document':
        """OPWI 형식에서 문서를 로드합니다."""
        lines = content.split('\n')
        doc = None
        meta = {}
        current_block = None
        current_revision = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('DOC:'):
                doc = cls("", "")  # 임시 제목과 네임스페이스
                doc.doc_id = line[4:]
            elif line.startswith('META:'):
                try:
                    meta = json.loads(line[5:])
                    if doc:
                        doc.title = meta.get("title", "")
                        doc.namespace = meta.get("namespace", "main")
                        doc.created_at = meta.get("created_at", "")
                        doc.tags = meta.get("tags", [])
                        doc.category = meta.get("category", "")
                except json.JSONDecodeError:
                    print(f"Warning: Invalid META JSON format")
            elif line.startswith('REVUSER:'):
                parts = line[8:].split(':')
                if len(parts) == 2:
                    current_revision = {
                        "username": parts[0],
                        "ip_address": parts[1],
                        "doc_id": doc.doc_id if doc else None,
                        "timestamp": None,
                        "changes": None
                    }
            elif line.startswith('REVBLOCK:START'):
                current_block = []
            elif line.startswith('REVBLOCK:END'):
                if current_block and current_revision:
                    try:
                        changes = json.loads(''.join(current_block))
                        if isinstance(changes, list) and len(changes) > 0:
                            current_revision["changes"] = changes
                            if doc:
                                doc.revisions.append(current_revision)
                                doc.contributors.add(current_revision["username"])
                                # 마지막 변경 내용을 현재 내용으로 설정
                                for change in changes:
                                    if isinstance(change, dict):
                                        for op, text in change.items():
                                            if op.startswith('+') or op.startswith('='):
                                                doc.content = text
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid CHANGES JSON format")
                current_block = None
                current_revision = None
            elif line.startswith('CHANGES:'):
                if current_block is not None:
                    current_block.append(line[8:])
            elif current_block is not None:
                current_block.append(line)
        
        return doc

class DocumentManager:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.index_path = os.path.join(base_path, "index", "document_index.json")
        self.pages_path = os.path.join(base_path, "pages")
        self.load_index()

    def load_index(self):
        """문서 인덱스를 로드하고, 하위 폴더까지 자동으로 검색"""
        if os.path.exists(self.index_path):
            with open(self.index_path, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            self.index = {
                "last_updated": datetime.now().isoformat(),
                "documents": {},
                "namespaces": {}
            }
        
        # 모든 문서를 재귀적으로 탐색하여 인덱스 업데이트
        self.index["documents"] = {}
        for root, _, files in os.walk(self.pages_path):
            namespace = os.path.relpath(root, self.pages_path).replace("\\", "/")  # 네임스페이스 경로 저장
            if namespace not in self.index["namespaces"]:
                self.index["namespaces"][namespace] = {"path": f"/pages/{namespace}", "description": "자동 추가된 네임스페이스"}

            for file in files:
                if file.endswith(".opwi"):
                    doc_path = os.path.join(root, file)
                    doc_relative_path = os.path.relpath(doc_path, self.pages_path).replace("\\", "/")  # 상대 경로 사용
                    doc_id = os.path.splitext(doc_relative_path)[0]  # `.opwi` 확장자 제거

                    self.index["documents"][doc_id] = {
                        "title": os.path.splitext(file)[0],
                        "path": doc_relative_path,
                        "namespace": namespace,
                        "created_at": datetime.now().isoformat(),
                        "last_modified": datetime.now().isoformat(),
                        "revision_count": 1,
                        "contributors": []
                    }

        self.save_index()

    def save_index(self):
        """문서 인덱스를 저장"""
        self.index["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def create_document(self, title: str, content: str, username: str, ip_address: str, namespace: str = "") -> Document:
        """하위 폴더까지 지원하는 문서 생성"""
        doc = Document(title, namespace)
        revision_data = doc.add_content(content, username, ip_address)

        # 문서 저장 경로 설정 (네임스페이스 유지)
        doc_path = os.path.join(self.pages_path, namespace, f"{title}.opwi") if namespace else os.path.join(self.pages_path, f"{title}.opwi")
        os.makedirs(os.path.dirname(doc_path), exist_ok=True)

        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc.to_opwi())

        # 인덱스 업데이트
        doc_id = os.path.join(namespace, title).replace("\\", "/").strip("/")
        self.index["documents"][doc_id] = {
            "title": title,
            "path": os.path.relpath(doc_path, self.pages_path).replace("\\", "/"),
            "namespace": namespace,
            "created_at": doc.created_at,
            "last_modified": revision_data["timestamp"],
            "revision_count": 1,
            "contributors": list(doc.contributors)
        }
        self.save_index()

        return doc

    def update_document(self, doc_id: str, content: str, username: str, ip_address: str) -> bool:
        """기존 문서를 수정 (하위 폴더 지원)"""
        if doc_id not in self.index["documents"]:
            return False

        doc_info = self.index["documents"][doc_id]
        doc_path = os.path.join(self.pages_path, doc_info["path"])

        if not os.path.exists(doc_path):
            return False  # 파일이 존재하지 않으면 실패
        
        # 기존 문서 읽기
        with open(doc_path, "r", encoding="utf-8") as f:
            doc = Document.from_opwi(f.read())

        # 새 리비전 추가
        revision_data = doc.update_content(content, username, ip_address)

        # 문서 저장
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc.to_opwi())

        # 인덱스 업데이트
        doc_info["last_modified"] = revision_data["timestamp"]
        doc_info["revision_count"] = len(doc.revisions)
        doc_info["contributors"] = list(doc.contributors)
        self.save_index()

        return True

    def get_document(self, doc_id: str) -> Document:
        """하위 폴더 포함 문서를 가져오기"""
        if doc_id not in self.index["documents"]:
            return None
        
        doc_info = self.index["documents"][doc_id]
        doc_path = os.path.join(self.pages_path, doc_info["path"])

        if not os.path.exists(doc_path):
            return None

        with open(doc_path, "r", encoding="utf-8") as f:
            return Document.from_opwi(f.read())

    def get_document_by_path(self, path: str) -> Document:
        """경로를 기반으로 문서를 가져오기 (하위 폴더까지 검색)"""
        normalized_path = os.path.relpath(path, self.pages_path).replace("\\", "/")
        for doc_id, info in self.index["documents"].items():
            if info["path"] == normalized_path:
                return self.get_document(doc_id)
        return None
