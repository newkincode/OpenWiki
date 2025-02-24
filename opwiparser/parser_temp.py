code = {
    "redirect": "redirect",
    "colon": ":",
    "left_square_brackets": "[",
    "right_square_brackets": "]",
    "left_square_brackets2": "[[",
    "right_square_brackets2": "]]",
}

def parse(fileline: str):
    backtoken = ""
    parse_index = 0
    parse_end_code = []
    
    for i in range(len(fileline)):
        # 리다이렉트 감지 부분
        if fileline[i] == code["left_square_brackets"] and backtoken == "":  # 첫 대괄호
            backtoken = fileline[i]
        elif fileline[i] == code["left_square_brackets"] and backtoken == code["left_square_brackets"]:  # 대괄호 2번 연속
            parse_end_code.append(code["left_square_brackets2"])  # 파싱된 코드 리스트에 저장
            backtoken = ""
        elif len(parse_end_code) > 0 and parse_end_code[-1] == code["left_square_brackets2"]:  # 마지막으로 [[이 파싱되었다면
            backtoken = fileline[i]  # 오타 수정 (== → =)
            if parse_index < len(code["redirect"]) and fileline[i] == code["redirect"][parse_index]:  # redirect 감지
                parse_index += 1
                if parse_index == len(code["redirect"]):  # redirect 완성
                    parse_end_code.append(code["redirect"])
                    parse_index = 0
            else:
                parse_index = 0
        
        elif len(parse_end_code) > 0 and parse_end_code[-1] == code["redirect"]:  # redirect 이후라면
            backtoken = fileline[i]  # 오타 수정 (== → =)
            if parse_index < len(code["colon"]) and fileline[i] == code["colon"][parse_index]:  # : 감지
                parse_index += 1
                if parse_index == len(code["colon"]):  # : 완성
                    parse_end_code.append(code["colon"])
                    parse_index = 0
            else:
                parse_index = 0
        
        elif (
            len(parse_end_code) >= 3
            and parse_end_code[-3] == code["left_square_brackets2"]
            and parse_end_code[-2] == code["redirect"]
            and parse_end_code[-1] == code["colon"]
        ):  # [[redirect: 이후
            end_redirect = fileline.find(code["right_square_brackets2"], i)  # ]] 찾기
            
            if end_redirect == -1:  # 닫는 대괄호 없음 → 일반 문자 취급
                temp1 = parse_end_code[-3] + parse_end_code[-2] + parse_end_code[-1]  # [[redirect: 합치기
                parse_end_code = parse_end_code[:-3]  # 마지막 3개 삭제
                parse_end_code.append(temp1)  # 합친 문자열 저장
            else:  # ]] 닫음
                parse_end_code.append(fileline[i:end_redirect])  # dd 저장
                parse_end_code.append(code["right_square_brackets2"])
    
    return parse_end_code

print(parse("[[redirect:./오픈위키:대문]] ㅇㅇㅇ"))
