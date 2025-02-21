import markdown
import os
from parser import parser

print("run on", os.path.dirname(os.path.realpath(__file__)))
os.chdir(os.path.dirname(os.path.realpath(__file__)))

print("create static files...")
import shutil

path = "./templates/doc"

# 디렉토리가 이미 존재하면 삭제
if os.path.exists(path):
    shutil.rmtree(path)

# 디렉토리 생성
os.makedirs(path, exist_ok=True)
os.makedirs("./doc", exist_ok=True)

print("doc folder")

docs_base = ""

with open(f"./frame/docs_base.md", "r", encoding="utf-8") as file:
    docs_base = file.read()

# 하위 폴더까지 포함하여 .md 파일 변환
for root, _, files in os.walk("./doc"):
    for docs in files:
        if docs.endswith(".md"):  # .md 파일만 변환
            md_filepath = os.path.join(root, docs)  # 원본 .md 파일 경로
            relative_path = os.path.relpath(md_filepath, "./doc")  # "./doc" 기준 상대 경로
            html_filename = os.path.splitext(relative_path)[0] + ".html"  # 확장자 변경

            with open(md_filepath, "r", encoding="utf-8") as file:
                content = file.read()  # 파일 읽기
                html_content = markdown.markdown(content)  # Markdown → HTML 변환
                wiki_content = parser.parse(relative_path.replace(".md", "").replace("\\", "/"),html_content, docs_base)
                
                

            html_output_path = os.path.join("./templates/doc", html_filename)  # 저장 경로
            os.makedirs(os.path.dirname(html_output_path), exist_ok=True)  # 하위 디렉토리 생성

            with open(html_output_path, "w", encoding="utf-8") as staticfile:
                staticfile.write(wiki_content)  # 변환된 HTML 저장

            print(f"\rprocessing: {relative_path} -> {html_filename}", end="", flush=True)  # 이전 줄 덮어쓰기

print("frame folder", end="", flush=True)

os.makedirs("./templates/frame", exist_ok=True)
os.makedirs("./frame", exist_ok=True)

doc_list = os.listdir("./frame")  # ./doc 폴더의 파일 리스트 가져오기

for docs in doc_list:
    with open(f"./frame/{docs}", "r", encoding="utf-8") as file:
        content = file.read()  # 파일 읽기
        html_content = markdown.markdown(content)  # Markdown → HTML 변환
        wiki_content = parser.parse_frame(html_content)
        
          

    # 확장자 변경: example.md → example.html
    html_filename = docs.rsplit(".", 1)[0] + ".html"

    with open(f"./templates/frame/{html_filename}", "w", encoding="utf-8") as staticfile:
        staticfile.write(wiki_content)  # 변환된 HTML 저장

    print(f"\rprocessing: {docs} -> {html_filename}", end="", flush=True)  # 이전 줄 덮어쓰기

print("\ndone!")  # 모든 파일 변환 완료 후 줄 바꿈

print("flask server openning...")

from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template("frame/index.html")

@app.route('/doc/<path:docname>')
def doc(docname):
    filepath = f"templates/doc/{docname}.html"

    if os.path.exists(filepath):
        return render_template(f"./doc/{docname}.html", title=docname, content=content)
    else:
        return render_template("frame/404.html"), 404

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
    """서버에서 검색 결과 필터링 후 반환"""
    query = request.args.get("query", "").strip().lower()
    doc_folder = "./templates/doc"
    search_results = []

    # 전체 문서 목록 가져오기
    all_docs = [
        os.path.splitext(os.path.relpath(os.path.join(root, file), doc_folder))[0].replace("\\", "/")
        for root, _, files in os.walk(doc_folder)
        for file in files if file.endswith(".html")
    ]

    # 검색어 필터링 (부분 일치)
    if query:
        search_results = [doc for doc in all_docs if query in doc.lower()]

    return render_template("frame/search.html", query=query, results=search_results)

if __name__ == "__main__":
    app.run(debug=True)
