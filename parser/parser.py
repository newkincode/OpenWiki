import re

def parseline(text: str):
    # 🔹 1️⃣ [[redirect:...]] 처리
    redirect_pattern = r"\[\[redirect:(.+?)\]\]"
    find_redirect = re.search(redirect_pattern, text)

    if find_redirect:
        rep = f'<meta http-equiv="refresh" content="0;url=/doc/{find_redirect.group(1)}">'  # URL 변환
        text = re.sub(redirect_pattern, rep, text)  # 변환된 텍스트 반환

    # 🔹 1️⃣ [[...]] 처리
    redirect_pattern = r"\[\[(.+?)\]\]"
    find_redirect = re.search(redirect_pattern, text)

    if find_redirect:
        rep = f'<a class="doclink" href="/doc/{find_redirect.group(1)}">{find_redirect.group(1)}</a>'  # URL 변환
        text = re.sub(redirect_pattern, rep, text)  # 변환된 텍스트 반환

    # 🔹 2️⃣ {template:...} 처리
    template_pattern = r"\{template:(.+?)\}"
    find_template = re.search(template_pattern, text)

    if find_template:
        file_path = find_template.group(1)

        try:
            with open(file_path, "r", encoding="utf-8") as template_file:
                rep = template_file.read()
                text = re.sub(template_pattern, rep, text)  # 변환된 텍스트 반환
        except FileNotFoundError:
            text = re.sub(template_pattern, f"[Error: {file_path} not found]", text)  # 파일이 없을 때 에러 메시지

    return text

def parse(filename:str, text: str, docs_base:str):
    """여러 줄의 위키 문법을 처리하는 함수"""
    lines = text.split("\n")  # 여러 줄로 나누기
    processed_lines = [parseline(line) for line in lines]  # 각 줄을 변환
    docs = "\n".join(processed_lines)  # 변환된 줄을 다시 합치기
    docs_base_temp = docs_base.replace("{{ title }}", filename)
    processed_docs = docs_base_temp.replace("{{ content }}", docs)
    return processed_docs

def parse_frame(text: str):
    """여러 줄의 위키 문법을 처리하는 함수"""
    lines = text.split("\n")  # 여러 줄로 나누기
    processed_lines = [parseline(line) for line in lines]  # 각 줄을 변환
    docs = "\n".join(processed_lines)  # 변환된 줄을 다시 합치기
    return docs