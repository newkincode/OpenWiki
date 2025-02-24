import re
import json
import markdown

def parse_opwi(content: str) -> str:
    """OPWI 파일을 파싱하여 HTML로 변환"""
    lines = content.split('\n')
    doc_id = None
    meta = {}
    current_block = None
    content_blocks = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('DOC:'):
            doc_id = line[4:]
        elif line.startswith('META:'):
            try:
                meta = json.loads(line[5:])
            except json.JSONDecodeError:
                print(f"Warning: Invalid META JSON format in {doc_id}")
        elif line.startswith('REVBLOCK:START'):
            current_block = []
        elif line.startswith('REVBLOCK:END'):
            if current_block:
                try:
                    changes = json.loads(''.join(current_block))
                    if isinstance(changes, list) and len(changes) > 0:
                        for change in changes:
                            if isinstance(change, dict):
                                for op, text in change.items():
                                    if op.startswith('+'):
                                        content_blocks.append(text)
                                    elif op.startswith('='):
                                        content_blocks.pop(-1)
                                        content_blocks.append(text)
                                    elif op.startswith('-'):
                                        content_blocks.pop(-1)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid CHANGES JSON format in {doc_id}")
            current_block = None
        elif line.startswith('CHANGES:'):
            if current_block is not None:
                current_block.append(line[8:])
        elif current_block is not None:
            current_block.append(line)
    
    # 마크다운으로 변환
    content = '\n'.join(content_blocks)
    html_content = markdown.markdown(content)
    
    return html_content

def parseline(text: str) -> str:
    """한 줄의 위키 문법을 처리하는 함수"""
    # [[redirect:...]] 처리
    redirect_pattern = r"\[\[redirect:(.+?)\]\]"
    if match := re.search(redirect_pattern, text):
        rep = f'<meta http-equiv="refresh" content="0;url=/doc/{match.group(1)}">'
        text = re.sub(redirect_pattern, rep, text)

    # [[...]] 처리
    link_pattern = r"\[\[(.+?)\]\]"
    if match := re.search(link_pattern, text):
        rep = f'<a class="doclink" href="/doc/{match.group(1)}">{match.group(1)}</a>'
        text = re.sub(link_pattern, rep, text)

    # {template:...} 처리
    template_pattern = r"\{template:(.+?)\}"
    if match := re.search(template_pattern, text):
        file_path = match.group(1)
        try:
            with open(file_path, "r", encoding="utf-8") as template_file:
                rep = template_file.read()
                text = re.sub(template_pattern, rep, text)
        except FileNotFoundError:
            text = re.sub(template_pattern, f"[Error: {file_path} not found]", text)

    return text

def parse(filename: str, text: str, template: str) -> str:
    """HTML 문서를 기본 템플릿에 적용"""
    # 위키 문법 처리
    lines = text.split('\n')
    processed_lines = [parseline(line) for line in lines]
    content = '\n'.join(processed_lines)
    
    # 템플릿 적용
    result = template.replace("{{ title }}", filename)
    result = result.replace("{{ content }}", content)
    
    return result

def parse_frame(text: str):
    """여러 줄의 위키 문법을 처리하는 함수"""
    lines = text.split("\n")  # 여러 줄로 나누기
    processed_lines = [parseline(line) for line in lines]  # 각 줄을 변환
    docs = "\n".join(processed_lines)  # 변환된 줄을 다시 합치기
    return docs