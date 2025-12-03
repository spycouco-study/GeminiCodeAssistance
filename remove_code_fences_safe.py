def remove_code_fences_safe(code_string: str) -> str:
    """
    문자열의 맨 처음과 맨 끝에 있는 Markdown 코드 블록(```)을 안전하게 제거합니다.
    시작과 끝 모두 백틱이 명확하게 존재하는지 검사합니다.
    
    Args:
        code_string: 백틱으로 감싸인 코드 문자열.

    Returns:
        백틱이 제거된 순수한 코드 문자열.
    """
    # 1. 문자열 앞뒤의 공백/줄바꿈을 제거합니다.
    stripped_string = code_string.strip()
    
    # 2. 앞쪽 백틱(```) 검사 및 제거
    content_start = 0
    if stripped_string.startswith('```'):
        # 첫 줄바꿈 위치를 찾아 언어 지정(예: typescript) 부분을 건너뜁니다.
        stripped_string = stripped_string.replace('\\n', '\n')
        first_newline_index = stripped_string.find('\n')
        
        if first_newline_index != -1:
            # '\n' 이후부터 코드가 시작됩니다.
            content_start = first_newline_index + 1
        else:
            # 한 줄짜리 코드인 경우, 단순히 '```' 세 글자만 제거합니다.
            content_start = 3
    
    # 앞쪽 백틱을 제거한 문자열
    processed_string = stripped_string[content_start:]
    
    # 3. 뒤쪽 백틱(```) 검사 및 제거 (가장 명확한 검증 부분)
    # 앞쪽을 제거한 문자열의 뒤쪽 공백/줄바꿈을 다시 정리합니다.
    final_string = processed_string.rstrip() 
    
    if final_string.endswith('```'):
        # 백틱 세 개가 명확하게 존재하면, 끝에서 세 글자를 제거합니다.
        final_string = final_string[:-3]
        
    return final_string.strip() # 최종적으로 앞뒤 공백/줄바꿈 다시 정리

