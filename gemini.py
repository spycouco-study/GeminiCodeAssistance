from pathlib import Path
import re
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv



load_dotenv() 



# OpenAI API 클라이언트 초기화
# OPENAI_API_KEY 불러와서 GPT 모델 호출에 사용
gemini_api_key = os.getenv('GEMINI_API_KEY')
model_name = "gemini-2.5-flash"






def remove_comments_from_file(file_path):
    """
    파이썬 코드 파일에서 주석(단일 라인 및 멀티 라인)을 제거하고
    결과 코드를 문자열로 반환합니다.
    """
    
    if not os.path.exists(file_path):
        return f"오류: 파일 경로를 찾을 수 없습니다: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        code_string = f.read()

    # 1. 단일 라인 주석 제거
    # 문자열 리터럴 내부의 #는 건드리지 않고, 코드 라인의 끝에 있는 #부터 줄 끝까지 제거
    # 이 정규식은 문자열 리터럴('...' 또는 "...") 내부의 #를 무시하는 데 중점을 둡니다.
    # 하지만 모든 엣지 케이스를 완벽히 처리하지는 못할 수 있습니다.
    # 가장 일반적인 경우: # 주석 
    code_string = re.sub(r'(?<![\'"])\#.*', '', code_string)


    # 2. 멀티 라인 주석/독스트링 제거 (""" 또는 ''')
    # 이 정규식은 """ 또는 ''' 으로 감싸진 모든 내용을 제거합니다.
    # 단, 함수나 클래스의 독스트링도 모두 제거되므로 주의해야 합니다.
    code_string = re.sub(r'("""[\s\S]*?""")|(\'\'\'[\s\S]*?\'\'\')', '', code_string)
    
    # 3. 빈 줄 정리 (주석 제거 후 남은 빈 줄들을 정리)
    # 여러 줄의 공백을 한 줄의 공백으로 바꾸고, 맨 앞뒤의 공백 제거
    code_string = re.sub(r'\n\s*\n', '\n', code_string).strip()

    return code_string





def split_gemini_response_code(response_text):
    """
    Gemini 응답 텍스트에서 코드 블록과 코드 외 텍스트를 분리하여 반환합니다.

    Args:
        response_text (str): Gemini 모델로부터 받은 전체 응답 텍스트.

    Returns:
        tuple: (code_content, non_code_text) 형태의 튜플을 반환합니다.
               코드가 없으면 (None, non_code_text)를 반환합니다.
    """
    
    # 1. 정규 표현식 패턴 정의 (DOTALL 플래그 사용)
    pattern = r'(<<<code_start>>>.*?<<<code_end>>>)'
    
    # 2. 텍스트에서 코드 블록을 찾아 분리합니다.
    # re.split()을 사용하면 패턴에 해당하는 부분과 패턴에 해당하지 않는 나머지 부분을 모두 리스트로 반환합니다.
    # 괄호()를 사용하여 패턴 자체도 결과 리스트에 포함되게 합니다.
    parts = re.split(pattern, response_text, flags=re.DOTALL)
    
    # 초기화
    code_content = None
    non_code_parts = []
    
    # 3. 리스트 순회하며 코드와 텍스트 분리
    for part in parts:
        if part.strip().startswith('<<<code_start>>>') and part.strip().endswith('<<<code_end>>>'):
            # 코드 블록에서 구분자를 제거하고 내용을 추출
            # .strip()은 앞뒤 공백을 제거하여 코드를 깔끔하게 합니다.
            code_content = part.replace('<<<code_start>>>', '').replace('<<<code_end>>>', '').strip()
        else:
            # 코드 블록이 아닌 텍스트는 리스트에 추가
            non_code_parts.append(part.strip())
            
    # 4. 코드 외 텍스트 합치고 정리
    # 빈 문자열을 제거하고, 여러 개의 빈 줄을 하나의 줄로 압축합니다.
    non_code_text = '\n'.join([p for p in non_code_parts if p])
    non_code_text = re.sub(r'\n\s*\n', '\n', non_code_text).strip()

    return code_content, non_code_text





# 환경 변수에서 API 키를 자동으로 가져옵니다.
# 만약 환경 변수 설정을 건너뛰고 싶다면, 
# client = genai.Client(api_key="YOUR_API_KEY") 와 같이 직접 전달할 수도 있습니다.
try:
    gemini_client = genai.Client(api_key=gemini_api_key)
except Exception as e:
    # 환경 변수가 설정되지 않은 경우를 처리
    print(f"클라이언트 초기화 오류: {e}")
    print("환경 변수 GEMINI_API_KEY가 설정되었는지 확인해 주세요.")
    exit()

# 💡 config 객체를 생성하여 응답 형식을 JSON으로 지정합니다.
config = types.GenerateContentConfig(
    response_mime_type="application/json"
)



CODE_PATH = Path(__file__).parent / "playground" / "playground.py"
CODE_PATH_NOCOMMENT = Path(__file__).parent / "playground" / "playground_nocomment.py"



while True:
    query = input("안녕하세요. 무엇을 도와드릴까요?\n(exit를 입력하면 종료됩니다.)\n")

    if query == 'exit':
        break

    code = remove_comments_from_file(CODE_PATH)

    # 모델에게 전달할 프롬프트(요청)입니다.
    #prompt = "사용자가 스페이스바를 누를때 마다 A 부터 Z까지 콘솔에 출력되는 파이썬 코드 작성해줘."
    prompt = f"{query} 이 것은 아래의 코드에 대한 수정요청이에요. 어떤 수정사항이 있었는지 간단히 설명도 해주세요. 응답 텍스트에서 코드부분을 명확히 알 수 있도록 반드시 수정된 코드의 시작부분에 '<<<code_start>>>'를, 끝부분에는 '<<<code_end>>>'를 적어주세요.\n\n{code}"

    # 모델 호출 및 응답 생성
    print(f"모델 호출 중: {model_name}...")
    try:
        response = gemini_client.models.generate_content(
            model=model_name,
            #config = config,
            contents=prompt
        )

        code_content, non_code_text = split_gemini_response_code(response.text)

        if code_content != None:
            with open(CODE_PATH, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            with open(CODE_PATH_NOCOMMENT, 'w', encoding='utf-8') as f:
                f.write(remove_comments_from_file(CODE_PATH))
        else:
            code_content = ""

        # 응답 결과 출력
        print("\n--- Gemini 응답 결과 ---")
        print(code_content)
        print(non_code_text)
        print("-----------------------\n")

    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")

print("프로그램이 종료되었습니다.")



