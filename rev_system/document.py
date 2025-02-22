import json
import os
import uuid
from datetime import datetime

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
        """문서 내용을 업데이트합니다."""
        self.contributors.add(username)
        
        # 변경 사항 계산
        changes = []
        
        # 이전 내용이 없으면 전체를 추가로 처리
        if not self.content:
            changes.append({
                f"+0|0|{len(content)}": content
            })
        # 새 내용이 없으면 전체를 삭제로 처리
        elif not content:
            changes.append({
                f"-0|0|{len(self.content)}": self.content
            })
        # 내용이 다르면 변경 사항 계산
        elif self.content != content:
            # 전체 내용이 변경된 것으로 처리
            changes.append({
                f"=0|0|{len(content)}": content
            })
        
        # 변경 사항이 없으면 빈 리스트 사용
        if not changes:
            changes = [{"=0|0|0": ""}]
        
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
        """문서 인덱스를 로드합니다."""
        if os.path.exists(self.index_path):
            with open(self.index_path, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            self.index = {
                "last_updated": datetime.now().isoformat(),
                "documents": {},
                "namespaces": {
                    "main": {
                        "path": "/pages/main",
                        "description": "메인 네임스페이스"
                    }
                }
            }
    
    def save_index(self):
        """문서 인덱스를 저장합니다."""
        self.index["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def create_document(self, title: str, content: str, username: str, ip_address: str, namespace: str = "main") -> Document:
        """새 문서를 생성합니다."""
        doc = Document(title, namespace)
        revision_data = doc.add_content(content, username, ip_address)
        
        # 문서 저장
        namespace_path = os.path.join(self.pages_path, namespace)
        os.makedirs(namespace_path, exist_ok=True)
        
        doc_path = os.path.join(namespace_path, f"{title}.opwi")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc.to_opwi())
        
        # 인덱스 업데이트
        self.index["documents"][doc.doc_id] = {
            "title": title,
            "path": f"/pages/{namespace}/{title}.opwi",
            "namespace": namespace,
            "created_at": doc.created_at,
            "last_modified": revision_data["timestamp"],
            "revision_count": 1,
            "contributors": list(doc.contributors)
        }
        self.save_index()
        
        return doc
    
    def update_document(self, doc_id: str, content: str, username: str, ip_address: str) -> bool:
        """기존 문서를 수정합니다."""
        if doc_id not in self.index["documents"]:
            return False
            
        doc_info = self.index["documents"][doc_id]
        doc_path = os.path.join(self.base_path, doc_info["path"].lstrip("/"))
        
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
        """문서를 가져옵니다."""
        if doc_id not in self.index["documents"]:
            return None
            
        doc_info = self.index["documents"][doc_id]
        doc_path = os.path.join(self.base_path, doc_info["path"].lstrip("/"))
        
        with open(doc_path, "r", encoding="utf-8") as f:
            return Document.from_opwi(f.read())
    
    def get_document_by_path(self, path: str) -> Document:
        """경로로 문서를 가져옵니다."""
        for doc_id, info in self.index["documents"].items():
            if info["path"] == path:
                return self.get_document(doc_id)
        return None 