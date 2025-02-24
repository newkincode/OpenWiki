import markdown
import os
import shutil
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from opwiparser import parser
from rev_system.document import DocumentManager

# 현재 디렉토리로 이동
print("run on", os.path.dirname(os.path.realpath(__file__)))
os.chdir(os.path.dirname(os.path.realpath(__file__)))

def convert_wiki_docs():
    """위키 문서(.opwi)를 HTML로 변환 (네임스페이스 폴더 유지)"""
    print("Converting wiki documents...")

    templates_path = "./templates/doc"
    
    # 기존 변환된 문서 삭제 후 재생성
    if os.path.exists(templates_path):
        shutil.rmtree(templates_path)
    os.makedirs(templates_path, exist_ok=True)

    # 기본 템플릿 읽기
    with open("./templates/base.html", "r", encoding="utf-8") as file:
        base_template = file.read()

    for root, _, files in os.walk("./pages"):
        for doc in files:
            if doc.endswith(".opwi"):
                opwi_filepath = os.path.join(root, doc)

                # 네임스페이스 유지하면서 변환된 HTML 파일 저장 경로 설정
                relative_path = os.path.relpath(opwi_filepath, "./pages")
                html_filename = os.path.splitext(relative_path)[0] + ".html"
                html_output_path = os.path.join(templates_path, html_filename)

                # 변환된 HTML 파일의 폴더 생성
                os.makedirs(os.path.dirname(html_output_path), exist_ok=True)

                with open(opwi_filepath, "r", encoding="utf-8") as file:
                    content = file.read()
                    # OPWI 파싱 및 HTML 변환
                    html_content = parser.parse_opwi(content)
                    wiki_content = parser.parse(html_filename.replace(".html", ""), html_content, base_template)

                with open(html_output_path, "w", encoding="utf-8") as staticfile:
                    staticfile.write(wiki_content)

                print(f"Converted: {opwi_filepath} -> {html_output_path}")

    print("Conversion complete!")

# Flask 애플리케이션 설정
app = Flask(__name__, static_url_path='/static')
doc_manager = DocumentManager()

@app.route('/')
@app.route('/home')
def home():
    return redirect(url_for('doc', docname='오픈위키/대문'))

@app.route('/doc/<path:docname>')
def doc(docname):
    filepath = f"templates/doc/{docname}.html"
    
    if os.path.exists(filepath):
        return render_template(f"doc/{docname}.html")
    else:
        return redirect(url_for('edit_doc', docname=docname))

@app.route('/edit/<path:docname>', methods=['GET', 'POST'])
def edit_doc(docname):
    if request.method == 'POST':
        content = request.form.get('content', '')
        username = request.form.get('username', 'anonymous')

        doc_id = docname.strip("/")
        if doc_id in doc_manager.index["documents"]:
            doc_manager.update_document(doc_id, content, username, request.remote_addr)
        else:
            doc_manager.create_document(docname, content, username, request.remote_addr)
        
        convert_wiki_docs()
        return redirect(url_for('doc', docname=docname))
    
    content = ""
    doc_id = docname.strip("/")
    if doc_id in doc_manager.index["documents"]:
        doc = doc_manager.get_document(doc_id)
        if doc and doc.content:
            content = doc.content
    
    return render_template("edit.html", docname=docname, content=content)

@app.route('/history/<path:docname>')
def history(docname):
    doc_id = docname.strip("/")
    doc = doc_manager.get_document(doc_id)
    if doc:
        revisions = [{"username": rev["username"], "timestamp": rev["timestamp"], "changes": rev["changes"]} for rev in doc.revisions]
        return render_template("history.html", docname=docname, revisions=revisions)
    else:
        return render_template("404.html"), 404

@app.route('/api/docs')
def get_docs():
    """모든 문서 목록을 JSON으로 반환 (네임스페이스 없이)"""
    doc_folder = "./templates/doc"
    docs = [
        os.path.splitext(file)[0]
        for file in os.listdir(doc_folder)
        if file.endswith(".html")
    ]
    return jsonify(docs)

@app.route('/search', methods=['GET'])
def search():
    """네임스페이스 없이 검색 가능하도록 수정"""
    query = request.args.get("query", "").strip().lower()
    search_results = []

    if query:
        for doc_id, info in doc_manager.index["documents"].items():
            title = info["title"].lower()
            if query in title:
                search_results.append({
                    "id": doc_id,
                    "title": info["title"],
                    "path": info["path"].replace(".opwi", ""),
                    "match_type": "title",
                    "relevance": 1 if query == title else 0.8
                })

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
                            "path": info["path"].replace(".opwi", ""),
                            "match_type": "content",
                            "relevance": 0.6
                        })
            except:
                continue

        search_results.sort(key=lambda x: (-x["relevance"], x["title"]))

    return render_template("search.html", query=query, results=search_results)

if __name__ == "__main__":
    convert_wiki_docs()
    print("Starting Flask server...")
    app.run(debug=True)

def apprun():
    convert_wiki_docs()
    return app