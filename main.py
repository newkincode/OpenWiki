import markdown
import os
import shutil
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from parser import parser
from rev_system.document import DocumentManager

# 현재 디렉토리로 이동
print("run on", os.path.dirname(os.path.realpath(__file__)))
os.chdir(os.path.dirname(os.path.realpath(__file__)))

def convert_wiki_docs():
    """위키 문서(.opwi)를 HTML로 변환"""
    print("Converting wiki documents...")
    
    # 템플릿 디렉토리 초기화
    if os.path.exists("./templates/doc"):
        shutil.rmtree("./templates/doc")
    os.makedirs("./templates/doc", exist_ok=True)

    # 기본 템플릿 읽기
    with open("./templates/base.html", "r", encoding="utf-8") as file:
        base_template = file.read()

    # 위키 문서 변환
    for root, _, files in os.walk("./pages"):
        for doc in files:
            if doc.endswith(".opwi"):
                opwi_filepath = os.path.join(root, doc)
                # 네임스페이스를 제외한 상대 경로 계산
                namespace = os.path.basename(os.path.dirname(opwi_filepath))
                html_filename = os.path.splitext(os.path.basename(opwi_filepath))[0] + ".html"

                with open(opwi_filepath, "r", encoding="utf-8") as file:
                    content = file.read()
                    # opwi 파싱 및 HTML 변환
                    html_content = parser.parse_opwi(content)
                    wiki_content = parser.parse(
                        html_filename.replace(".html", ""),
                        html_content,
                        base_template
                    )

                html_output_path = os.path.join("./templates/doc", html_filename)
                os.makedirs(os.path.dirname(html_output_path), exist_ok=True)

                with open(html_output_path, "w", encoding="utf-8") as staticfile:
                    staticfile.write(wiki_content)

                print(f"Converting: {opwi_filepath} -> {html_filename}")

    print("Conversion complete!")

# Flask 애플리케이션 설정
app = Flask(__name__, static_url_path='/static')
doc_manager = DocumentManager()

@app.route('/')
@app.route('/home')
def home():
    return redirect(url_for('doc', docname='대문'))

@app.route('/doc/<path:docname>')
def doc(docname):
    filepath = f"templates/doc/{docname}.html"
    if os.path.exists(filepath):
        return render_template(f"doc/{docname}.html")
    else:
        # 문서가 없으면 생성 페이지로 리다이렉트
        return redirect(url_for('edit_doc', docname=docname))

@app.route('/edit/<path:docname>', methods=['GET', 'POST'])
def edit_doc(docname):
    if request.method == 'POST':
        content = request.form.get('content', '')
        username = request.form.get('username', 'anonymous')
        
        # 문서 ID 찾기
        doc_id = None
        for id, info in doc_manager.index["documents"].items():
            if info["path"] == f"/pages/main/{docname}.opwi":
                doc_id = id
                break
        
        if doc_id:
            # 기존 문서 수정
            doc_manager.update_document(doc_id, content, username, request.remote_addr)
        else:
            # 새 문서 생성
            doc_manager.create_document(docname, content, username, request.remote_addr)
        
        # 문서 변환
        convert_wiki_docs()
        
        return redirect(url_for('doc', docname=docname))
    
    # GET 요청: 편집 폼 표시
    content = ""
    for doc_id, info in doc_manager.index["documents"].items():
        if info["path"] == f"/pages/main/{docname}.opwi":
            doc = doc_manager.get_document(doc_id)
            if doc and doc.content:
                content = doc.content
            break
    
    return render_template("edit.html", docname=docname, content=content)

@app.route('/history/<path:docname>')
def history(docname):
    """문서의 변경 이력을 보여줍니다."""
    # 문서 찾기
    doc = None
    for doc_id, info in doc_manager.index["documents"].items():
        if info["path"] == f"/pages/main/{docname}.opwi":
            doc = doc_manager.get_document(doc_id)
            break
    
    if doc:
        revisions = []
        for rev in doc.revisions:
            revisions.append({
                "username": rev["username"],
                "timestamp": rev["timestamp"],
                "changes": rev["changes"]
            })
        return render_template("history.html", docname=docname, revisions=revisions)
    else:
        return render_template("404.html"), 404

@app.route('/api/docs')
def get_docs():
    """전체 문서 목록을 JSON으로 반환"""
    doc_folder = "./templates/doc"
    docs = [
        os.path.splitext(os.path.relpath(os.path.join(root, file), doc_folder))[0]
        for root, _, files in os.walk(doc_folder)
        for file in files if file.endswith(".html")
    ]
    return jsonify(docs)

@app.route('/search', methods=['GET'])
def search():
    """검색 기능"""
    query = request.args.get("query", "").strip().lower()
    search_results = []

    if query:
        # 문서 제목 검색
        for doc_id, info in doc_manager.index["documents"].items():
            title = info["title"].lower()
            if query in title:
                search_results.append({
                    "id": doc_id,
                    "title": info["title"],
                    "path": os.path.splitext(os.path.basename(info["path"]))[0],
                    "match_type": "title",
                    "relevance": 1 if query == title else 0.8
                })

        # 문서 내용 검색
        for doc_id, info in doc_manager.index["documents"].items():
            if any(result["id"] == doc_id for result in search_results):
                continue

            doc_path = os.path.join(doc_manager.base_path, info["path"].lstrip("/"))
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    if query in content:
                        search_results.append({
                            "id": doc_id,
                            "title": info["title"],
                            "path": os.path.splitext(os.path.basename(info["path"]))[0],
                            "match_type": "content",
                            "relevance": 0.6
                        })
            except:
                continue

        # 태그 검색
        for doc_id, info in doc_manager.index["documents"].items():
            if any(result["id"] == doc_id for result in search_results):
                continue

            doc_path = os.path.join(doc_manager.base_path, info["path"].lstrip("/"))
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("META:"):
                            meta = json.loads(line[5:])
                            if any(query in tag.lower() for tag in meta.get("tags", [])):
                                search_results.append({
                                    "id": doc_id,
                                    "title": info["title"],
                                    "path": os.path.splitext(os.path.basename(info["path"]))[0],
                                    "match_type": "tag",
                                    "relevance": 0.7
                                })
                            break
            except:
                continue

        # 검색 결과 정렬 (관련도 순)
        search_results.sort(key=lambda x: (-x["relevance"], x["title"]))

    return render_template("search.html", query=query, results=search_results)

@app.route('/create', methods=['GET', 'POST'])
def create_doc():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        username = request.form.get('username', 'anonymous')
        
        if not title:
            return "문서 제목을 입력해주세요.", 400
        
        # 이미 존재하는 문서인지 확인
        for doc_id, info in doc_manager.index["documents"].items():
            if info["path"] == f"/pages/main/{title}.opwi":
                return "이미 존재하는 문서입니다.", 400
        
        # 새 문서 생성
        doc_manager.create_document(title, content, username, request.remote_addr)
        
        # 문서 변환
        convert_wiki_docs()
        
        return redirect(url_for('doc', docname=title))
    
    return render_template("create.html")

if __name__ == "__main__":
    # 서버 시작 전 문서 변환
    convert_wiki_docs()
    
    # Flask 서버 시작
    print("Starting Flask server...")
    app.run(debug=True)
