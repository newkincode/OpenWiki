from uuid_extensions import uuid7, uuid7str
from rev_system import rev

def newdoc(title, content, user, ip):
    doc_content = {
        "title": title,
        "body": content,
        "author": f"{user}:{ip}"
    }

    docid = uuid7str()
    timest = rev.new_timestamp()
    revid = rev.generate_revision_id(doc_content, timest)

    # 큰따옴표 문제 수정 (f-string에서 중첩된 따옴표 사용)
    doc_text = f"DOC:{docid}\nREVUSER:{doc_content['author']}\nREV:{revid}"

    return doc_text  # 문서 내용을 반환 (파일로 저장할 수도 있음)