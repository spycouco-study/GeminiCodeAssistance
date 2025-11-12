import json
from pathlib import Path
import re
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from realtime import List

from classes import AnswerTemplateProcessor, ClientError, MakePromptTemplateProcessor, ModifyPromptTemplateProcessor, QuestionTemplateProcessor
from make_default_game_folder import create_project_structure
from make_dummy_image_asset_copy_2 import check_and_create_images_with_text
from make_dummy_sound_asset import copy_and_rename_sound_files
from tools.debug_print import debug_print
from tsc import check_typescript_compile_error
#from supabase import format_chat_history, get_session_history

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="Gemini Code Assistant API")

# ⚠️ CORS 설정: 클라이언트 브라우저가 요청을 보내도록 허용
# 개발 환경(예: http://localhost:5500)에서 실행되는 클라이언트 허용
origins = [
    "http://localhost",
    "http://localhost:8080",
    # 게임이 실행되는 클라이언트 주소를 추가해야 합니다.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)







# 환경 변수 로드
load_dotenv()

# Gemini API 초기화
gemini_api_key = os.getenv('GEMINI_API_KEY')
model_name = "gemini-2.5-flash"

# 요청 모델 정의
class CodeRequest(BaseModel):
    message: str
    game_name: str

# 서버 상태 체크를 위한 헬스체크 엔드포인트
@app.get("/")
async def root():
    return {"status": "healthy", "message": "Gemini Code Assistant API is running"}






def remove_comments_from_file(file_path):
    """
    파이썬 코드 파일에서 주석(단일 라인 및 멀티 라인)을 제거하고
    결과 코드를 문자열로 반환합니다.
    """
    
    if not os.path.exists(file_path):
        return ""#f"오류: 파일 경로를 찾을 수 없습니다: {file_path}"
    
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
            code_content = remove_code_fences_safe(code_content)
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




#CODE_PATH = Path(__file__).parent / "playground" / "playground.py"
#CODE_PATH_NOCOMMENT = Path(__file__).parent / "playground" / "playground_nocomment.py"

# 1. 게임 이름 정의 (수정 필요 없음)
GAME_NAME = "test"

# 2. 공통 기본 디렉토리 정의
# 'C:\Users\UserK\Desktop\final project\ts_game\GameMakeTest\GameFolder\public'
BASE_PUBLIC_DIR = Path(r"C:\Users\UserK\Desktop\final project\ts_game\GameMakeTest\GameFolder\public")

# 3. Old Version 디렉토리 정의
# 'C:\Users\UserK\Desktop\final project\ts_game\GameMakeTest\OldVersion'
BASE_OLD_DIR = Path(r"C:\Users\UserK\Desktop\final project\ts_game\GameMakeTest\OldVersion")

# # --- 최종 경로 정의 ---

# # 현재 버전 경로 (BASE_PUBLIC_DIR / GAME_NAME)
# GAME_DIR = BASE_PUBLIC_DIR / GAME_NAME
# CODE_PATH = BASE_PUBLIC_DIR / GAME_NAME / "game.ts"
# DATA_PATH = BASE_PUBLIC_DIR / GAME_NAME / "data.json"
# SPEC_PATH = BASE_PUBLIC_DIR / GAME_NAME / "spec.md"
# ASSETS_PATH = BASE_PUBLIC_DIR / GAME_NAME / "assets"

# # 이전 버전 경로 (BASE_OLD_DIR / GAME_NAME)
# OLD_GAME_DIR = BASE_OLD_DIR / GAME_NAME
# OLD_CODE = BASE_OLD_DIR / GAME_NAME / "(old)game.ts"
# OLD_DATA = BASE_OLD_DIR / GAME_NAME / "(old)data.json"
CODE_PATH_NOCOMMENT = ""#ePath(r"C:\Users\UserK\Desktop\final project\ts_game\GameFolder\src\bear block game(nocomment).ts")








def GAME_DIR(game_name:str):
    return BASE_PUBLIC_DIR / game_name

def CODE_PATH(game_name:str):
    return BASE_PUBLIC_DIR / game_name / "game.ts"

def DATA_PATH(game_name:str):
    return BASE_PUBLIC_DIR / game_name / "data.json"

def SPEC_PATH(game_name:str):
    return BASE_PUBLIC_DIR / game_name / "spec.md"

# def ASSETS_PATH(game_name:str):
#     return BASE_PUBLIC_DIR / game_name / "assets"



# 이전 버전 경로 (BASE_OLD_DIR / GAME_NAME)
def OLD_GAME_DIR(game_name:str):
    return BASE_OLD_DIR / game_name

def OLD_CODE(game_name:str):
    return BASE_OLD_DIR / game_name / "(old)game.ts"

def OLD_DATA(game_name:str):
    return BASE_OLD_DIR / game_name / "(old)data.json"









@app.post("/category")
async def category(request: CodeRequest):
    prompt = f"[사용자쿼리: {request.message}]\n" + """
    이 앱은 사용자의 자연어 입력을 받아 게임을 만드는 앱입니다.
    당신은 사용자쿼리가 아래의 카테고리 중 어디에 속하는지 분류해야 합니다.
        1: 게임을 수정해 달라는 요청.
        2: 게임과 관련된 질문.
        3: 기타.
        4: 부적절/비윤리적/서비스 범위초과
    아래와 같은 json 형식으로 답변해 주세요.
    {
        "category": int,
        "dscription: str,
        "response": str
    }
    """

    response = gemini_client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    reply_content = json.loads(remove_code_fences_safe(response.text))
    cat = reply_content['category']
    debug_print(cat)

    result_text = ""
    if cat == 1:
        code_content, result_text = modify_code(request)
    elif cat == 2:
        result_text = describe_code(request)
    elif cat == 3:
        result_text = ""
    elif cat == 4:
        result_text = "제가 도와드릴 수 없는 요청이에요."

    return {
        "status": "success",
        "reply": result_text
    }



def describe_code(request: CodeRequest):
    code = remove_comments_from_file(CODE_PATH(request.game_name))
    
    if code == "":
        return "분석할 코드가 없습니다."
    else:
        prompt = request.message + """ 이 것은 아래의 코드에 대한 질문입니다.
        답변은 반드시 다음과 같은 json 형식으로 해주세요: {response:str}""" + "\n\n<TypeScript code>\n" + code

    # 모델 호출 및 응답 생성
    print(f"AI 모델이 작업 중 입니다: {model_name}...")
    response = gemini_client.models.generate_content(
        model=model_name,
        #config = config,
        contents=prompt
    )

    reply_content = json.loads(remove_code_fences_safe(response.text))
    print(reply_content)

    return reply_content['response']

makePTP = MakePromptTemplateProcessor()
modifyPTP = ModifyPromptTemplateProcessor()


# path = Path(r"C:\Users\UserK\Desktop\test.txt")
# if os.path.exists(path):
#     with open(path, 'r', encoding='utf-8') as f:
#         text = f.read()


# try:
#     text2 = remove_code_fences_safe(text)    
#     path2 = Path(r"C:\Users\UserK\Desktop\test2.txt")
#     with open(path2, 'w', encoding='utf-8') as f:
#             f.write(text2)

#     responseJson = json.loads(text2)
# except Exception as e:
#     print(e)

def parse_ai_response(response_text):
    result = {}
    
    # 1. 코드 블록 추출
    code_start = response_text.find("###CODE_START###") + len("###CODE_START###")
    code_end = response_text.find("###CODE_END###")
    result['game_code'] = response_text[code_start:code_end].strip()

    # 2. 데이터 블록 추출 (JSON 문자열)
    data_start = response_text.find("###DATA_START###") + len("###DATA_START###")
    data_end = response_text.find("###DATA_END###")
    json_string = response_text[data_start:data_end].strip()
    result['game_data'] = json_string
    
    # 3. 필요 Asset 리스트 (JSON 문자열)
    asset_start = response_text.find("###ASSET_LIST_START###") + len("###ASSET_LIST_START###")
    asset_end = response_text.find("###ASSET_LIST_END###")
    json_asset_string = response_text[asset_start:asset_end].strip()
    result['asset_list'] = json_asset_string

    # 4. 설명 블록 추출
    desc_start = response_text.find("###DESCRIPTION_START###") + len("###DESCRIPTION_START###")
    desc_end = response_text.find("###DESCRIPTION_END###")
    result['description'] = response_text[desc_start:desc_end].strip()

    # 필요하다면 여기서 result['game_data']에 대해 json.loads()를 별도로 실행
    # game_data 블록은 순수한 JSON 텍스트이므로 이스케이프 문제가 훨씬 적습니다.
    # ...

    return result




def parse_ai_response2(response_text):
    result = {}
    
    # 1. 설명 블록 추출
    code_start = response_text.find("###COMMENT_START###") + len("###COMMENT_START###")
    code_end = response_text.find("###COMMENT_END###")
    result['comment'] = response_text[code_start:code_end].strip()

    # 2. 자연어 사양서 블록 추
    code_start = response_text.find("###SPECIFICATION_START###") + len("###SPECIFICATION_START###")
    code_end = response_text.find("###SPECIFICATION_END###")
    result['specification'] = response_text[code_start:code_end].strip()

    # 필요하다면 여기서 result['game_data']에 대해 json.loads()를 별도로 실행
    # game_data 블록은 순수한 JSON 텍스트이므로 이스케이프 문제가 훨씬 적습니다.
    # ...

    return result




#check_typescript_compile_error(CODE_PATH)

def validate_json(json_str):
    try:
        json.loads(json_str)
        return ""
    except json.JSONDecodeError as e:
        return f"{e.msg} (line {e.lineno}, col {e.colno})"
    


def modify_code(request, game_name):
    """코드 처리 엔드포인트"""
    #original_code = remove_comments_from_file(CODE_PATH)

    if not os.path.exists(GAME_DIR(game_name)):
        create_project_structure(GAME_DIR(game_name))

    if os.path.exists(CODE_PATH(game_name)):
        with open(CODE_PATH(game_name), 'r', encoding='utf-8') as f:
            original_code = f.read()
    else:
        original_code = ""

    if os.path.exists(DATA_PATH(game_name)):
        with open(DATA_PATH(game_name), 'r', encoding='utf-8') as f:
            original_data = f.read()
    else:
        original_data = ""
    


    if original_code == "":
        prompt = makePTP.get_final_prompt(request)
    else:
        prompt = modifyPTP.get_final_prompt(request, original_code, original_data)

    # 💡 config 객체를 생성하여 응답 형식을 JSON으로 지정합니다.
    # config = types.GenerateContentConfig(
    #     response_mime_type="application/json"
    # )
    
    # 모델 호출 및 응답 생성
    print(f"AI 모델이 작업 중 입니다: {model_name}...")
    response = gemini_client.models.generate_content(
        model=model_name,
        #config = config,
        contents=prompt
    )

    #responseData = json.loads(remove_code_fences_safe(response.text))
    responseData = parse_ai_response(response.text)

    game_code = remove_code_fences_safe(responseData['game_code'])
    game_data = remove_code_fences_safe(responseData['game_data'])
    #asset_list = remove_code_fences_safe(responseData['asset_list'])
    # asset_list = json.loads(asset_list)
    # print(asset_list)
    # check_and_create_images(asset_list, ASSETS_PATH)
    
    error = validate_json(game_data)

    json_data = json.loads(game_data)
    print(json_data.get('assets', {}))

    check_and_create_images_with_text(json_data, GAME_DIR(game_name))
    copy_and_rename_sound_files(json_data, GAME_DIR(game_name))
    description = remove_code_fences_safe(responseData['description'])
    #split_gemini_response_code(response.text)

    if game_code is not None:
        # 이전 버전 백업
        if original_code != "":
            directory_path = os.path.dirname(OLD_CODE(game_name)) 
            if directory_path:
                os.makedirs(directory_path, exist_ok=True)

            with open(OLD_CODE(game_name), 'w', encoding='utf-8') as f:
                f.write(original_code)

        if original_data != "":            
            directory_path = os.path.dirname(OLD_DATA(game_name)) 
            if directory_path:
                os.makedirs(directory_path, exist_ok=True)

            with open(OLD_DATA(game_name), 'w', encoding='utf-8') as f:
                f.write(original_data)



        # 새 코드 저장          
        directory_path = os.path.dirname(CODE_PATH(game_name)) 
        if directory_path:
            os.makedirs(directory_path, exist_ok=True)

        with open(CODE_PATH(game_name), 'w', encoding='utf-8') as f:  
            f.write(game_code)
              
        directory_path = os.path.dirname(DATA_PATH(game_name)) 
        if directory_path:
            os.makedirs(directory_path, exist_ok=True)

        with open(DATA_PATH(game_name), 'w', encoding='utf-8') as f:  
            f.write(game_data)



        # 주석 제거된 버전 저장
        if CODE_PATH_NOCOMMENT != "":
            with open(CODE_PATH_NOCOMMENT, 'w', encoding='utf-8') as f:
                f.write(remove_comments_from_file(CODE_PATH_NOCOMMENT))

        if error == "":
            error = check_typescript_compile_error(CODE_PATH(game_name))
        else:
            error = error + '\n' + check_typescript_compile_error(CODE_PATH(game_name))

    return game_code, game_data, description, error




@app.get("/spec")
async def get_spec(game_name: str):
    if os.path.exists(SPEC_PATH(game_name)):
        with open(SPEC_PATH(game_name), 'r', encoding='utf-8') as f:
            spec = f.read()

    # 최신 사양서(문자열) 반환
    markdown = spec
    # 프런트는 onMarkdownUpdate(specRes.data)를 호출하므로 문자열이면 충분
    return markdown


MAX_ATTEMPTS = 5

@app.post("/process-code")
async def process_code(request: CodeRequest):
    """코드 처리 엔드포인트"""
    try:
        game_code, game_data, description, error = modify_code(request.message, request.game_name)  

        if error != "":
            for i in range(MAX_ATTEMPTS):    
                game_code, game_data, description, error = modify_code(error, request.game_name) 
                
                if error == "":
                    # 에러가 빈 문자열이라면 (에러 해결 성공)
                    print(f"🎉 컴파일 성공! 에러가 해결되었습니다. (총 {i + 1}회 시도)")
                    #final_error = "" # 최종 에러 상태를 성공으로 기록
                    break # 반복문을 즉시 중단하고 빠져나옴
                else:
                    # 에러가 있다면 (에러 해결 실패)
                    print(f"❌ 컴파일 에러 발생: {error}")
                    #final_error = error # 최종 에러 상태를 실패로 기록

        return {
            "status": "success",
            "code": game_code,
            "data": game_data,
            "reply": description
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/client-error")
async def log_client_error(error_data: ClientError):
    """
    클라이언트로부터 전송된 오류 로그를 받아 처리합니다.
    """
    # 🌟 1. 로그 기록 (가장 중요)
    print(f"[{error_data.time}] 💥 CLIENT ERROR ({error_data.type})")
    print(f"  Version: {error_data.game_version}")
    print(f"  Message: {error_data.message}")
    
    if error_data.stack:
        print(f"  Stack Trace:\n{error_data.stack[:200]}...") # 스택은 너무 길 수 있으므로 일부만 출력
    
    # 🌟 2. 실제 데이터베이스나 파일에 저장
    # 예: log_to_database(error_data)
    # 예: log_to_file(error_data)

    # 클라이언트에게 성공적으로 받았음을 응답합니다.
    return {"status": "success", "message": "Error logged successfully"}



qtp = QuestionTemplateProcessor()

@app.post("/question")
async def process_code(request: CodeRequest):
    try:        
        history = ""#format_chat_history(get_session_history(0))
        specification = ""
        prompt = qtp.get_final_prompt(history, request.message, specification)

        print(f"AI 모델이 작업 중 입니다: {model_name}...")
        response = gemini_client.models.generate_content(
            model=model_name,
            #config = config,
            contents=prompt
        )

        return {
            "reply": remove_code_fences_safe(response.text)
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


class QuestionAnswer(BaseModel):
    question: str
    answer: str

class AdditionalRequest(BaseModel):
    request: str

class ChatData(BaseModel):
    mainQuestions: List[QuestionAnswer]
    additionalRequests: List[AdditionalRequest]
    



def format_json_to_string(data):
    """
    주어진 JSON 데이터를 '질문x: ...\n답변x: ...\n추가요청x: ...' 형식의 문자열로 변환합니다.
    """
    output_lines = []
    
    # 1. mainQuestions 처리 (질문과 답변)
    for i, item in enumerate(data.get('mainQuestions', [])):
        question_num = i + 1
        
        # 'question' 키는 항상 존재한다고 가정
        question = item.get('question', '질문 없음')
        
        # 'answer' 키가 있으면 사용하고, 없으면 빈 문자열 또는 특정 문구를 사용
        # 원본 JSON에는 첫 번째 질문에 'answer' 키가 없으므로, 코드 실행을 위해 'answer': '없음'을 임시로 추가했습니다.
        answer = item.get('answer', '미입력')
        
        output_lines.append(f"질문{question_num}: {question}")
        output_lines.append(f"답변{question_num}: {answer}")
        output_lines.append("") # 줄바꿈 추가
        
    # 질문/답변 섹션과 추가 요청 섹션을 시각적으로 구분
    if output_lines and data.get('additionalRequests'):
        output_lines.append("") # 줄바꿈 추가
        
    # 2. additionalRequests 처리 (추가 요청)
    for i, item in enumerate(data.get('additionalRequests', [])):
        request_num = i + 1
        # 'request' 키는 항상 존재한다고 가정
        request = item.get('request', '요청 내용 없음')
        
        output_lines.append(f"추가요청{request_num}: {request}")
        output_lines.append("") # 줄바꿈 추가
        
    # 모든 라인을 줄바꿈 문자('\n')로 연결하여 최종 문자열 생성
    return "\n".join(output_lines)


atp = AnswerTemplateProcessor()
    


from typing import Any, Dict

# 기존 submitData의 구조에 맞춰 payload 필드를 정의합니다.
# payload 내용이 복잡하거나 명확하지 않다면 Dict[str, Any]로 설정할 수 있습니다.
# class SubmitPayload(BaseModel):
#     # submitData의 원래 필드들을 여기에 정의합니다.
#     # 예시:
#     # prompt: str
#     # answer: str
#     # group_index: int
#     # 정확한 구조를 모를 경우 Dict[str, Any]로 처리
#     __root__: Dict[str, Any]

# 💡 상위 계층 구조를 정의하는 메인 모델
class WrappedSubmitData(BaseModel):
    game_name: str
    payload: str

@app.post("/qna")
async def process_chat_data(data: WrappedSubmitData):   #      game_name: str, data: str = Body(...)):
    # Pydantic 모델을 통해 깔끔하게 데이터 접근
    game_name = data.game_name
    chat_data = json.loads(data.payload)

    print(chat_data)

    result = format_json_to_string(chat_data)

    print(result)

    old_spec = ""
    if os.path.exists(SPEC_PATH(game_name)):
        with open(SPEC_PATH(game_name), 'r', encoding='utf-8') as f:
            old_spec = f.read()

    prompt = atp.get_final_prompt(old_spec, result)

    print(f"AI 모델이 작업 중 입니다: {model_name}...")
    response = gemini_client.models.generate_content(
            model=model_name,
            #config = config,
            contents=prompt
        )

    print(response.text)

    parse = parse_ai_response2(response.text)
    spec = parse['specification']

    directory_path = os.path.dirname(SPEC_PATH(game_name)) 
    if directory_path:
        os.makedirs(directory_path, exist_ok=True)

    with open(SPEC_PATH(game_name), 'w', encoding='utf-8') as f:
        f.write(spec)

    history = ""#format_chat_history(get_session_history(0))
    prompt = qtp.get_final_prompt(history, "", spec)

    print(f"AI 모델이 작업 중 입니다: {model_name}...")
    response = gemini_client.models.generate_content(
        model=model_name,
        #config = config,
        contents=prompt
    )

    return {
                "status": "success",
                "message": "답변이 성공적으로 처리되었습니다.",                
                "reply": remove_code_fences_safe(response.text)
            }



@app.post("/answer")
async def process_code(request: CodeRequest):
    try:        
        history = ""
        specification = ""
        prompt = atp.get_final_prompt(specification)

        return {
            "reply": prompt
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))



# /revert 엔드포인트 추가
@app.post("/revert")
async def revert_code(game_name):
    """코드를 이전 버전으로 되돌리는 엔드포인트"""
    try:
        if os.path.exists(OLD_CODE(game_name)):
            with open(OLD_CODE(game_name), 'r', encoding='utf-8') as f:
                old_code = f.read()
            
            with open(CODE_PATH(game_name), 'w', encoding='utf-8') as f:
                f.write(old_code)
            
            if os.path.exists(OLD_DATA(game_name)):
                with open(OLD_DATA(game_name), 'r', encoding='utf-8') as f:
                    old_code = f.read()
                
                with open(DATA_PATH(game_name), 'w', encoding='utf-8') as f:
                    f.write(old_code)

            return {"status": "success", "reply": "코드를 이전 버전으로 되돌렸습니다."}
        else:
            return {"status": "success", "reply": "되돌릴 코드가 없습니다."}
            #raise HTTPException(status_code=404, detail="되돌릴 코드가 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 서버 실행 방법 1: uvicorn 명령어로 직접 실행 (권장)
# uvicorn gemini:app --reload --port 8000

# 서버 실행 방법 2: Python 스크립트로 직접 실행
if __name__ == "__main__":
    import uvicorn
    print("서버를 시작합니다... http://localhost:8000")
    uvicorn.run(
        "gemini:app",
        host="0.0.0.0",
        port=8000,
        reload=True,      # 코드 변경 감지
        log_level="debug",  # 디버그 로그 활성화
        workers=1        # 디버깅을 위해 단일 워커 사용
    )


