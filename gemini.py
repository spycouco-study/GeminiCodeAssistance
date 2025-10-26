from pathlib import Path
import re
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="Gemini Code Assistant API")

# 환경 변수 로드
load_dotenv()

# Gemini API 초기화
gemini_api_key = os.getenv('GEMINI_API_KEY')
model_name = "gemini-2.5-flash"

# 요청 모델 정의
class CodeRequest(BaseModel):
    message: str

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




#CODE_PATH = Path(__file__).parent / "playground" / "playground.py"
#CODE_PATH_NOCOMMENT = Path(__file__).parent / "playground" / "playground_nocomment.py"

FILE_NAME = "bubble game.ts"
CODE_PATH = Path(r"C:\Users\UserK\Desktop\final project\ts_game\GameMakeTest\GameFolder\src" + "\\" + FILE_NAME)
OLD_VERSION = Path(r"C:\Users\UserK\Desktop\final project\ts_game\GameMakeTest\OldVersion\(old)" + FILE_NAME)
CODE_PATH_NOCOMMENT = ""#ePath(r"C:\Users\UserK\Desktop\final project\ts_game\GameFolder\src\bear block game(nocomment).ts")



@app.post("/process-code")
async def process_code(request: CodeRequest):
    """코드 처리 엔드포인트"""
    try:
        code = remove_comments_from_file(CODE_PATH)
        
        if code == "":
            prompt = f"{request.message} 이 것은 하나의 TypeScript 파일로 구동되는 게임을 만들기 위한 요청입니다. 게임은 'gameCanvas'에 표시되어야 합니다. 게임 코드를 생성하고 간단히 설명도 해주세요. 응답 텍스트에서 코드부분을 명확히 알 수 있도록 반드시 수정된 코드의 시작부분에 '<<<code_start>>>'를, 끝부분에는 '<<<code_end>>>'를 적어주세요."
        else:
            prompt = f"{request.message} 이 것은 아래의 코드에 대한 수정요청이에요. 어떤 수정사항이 있었는지 간단히 설명도 해주세요. 응답 텍스트에서 코드부분을 명확히 알 수 있도록 반드시 수정된 코드의 시작부분에 '<<<code_start>>>'를, 끝부분에는 '<<<code_end>>>'를 적어주세요.\n\n{code}"

        # 💡 config 객체를 생성하여 응답 형식을 JSON으로 지정합니다.
        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )
        
        # 모델 호출 및 응답 생성
        print(f"AI 모델이 작업 중 입니다: {model_name}...")
        response = gemini_client.models.generate_content(
            model=model_name,
            #config = config,
            contents=prompt
        )

        code_content, non_code_text = split_gemini_response_code(response.text)

        if code_content is not None:
            # 이전 버전 백업
            if code != "":
                with open(OLD_VERSION, 'w', encoding='utf-8') as f:
                    f.write(code)

            # 새 코드 저장
            with open(CODE_PATH, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            # 주석 제거된 버전 저장
            if CODE_PATH_NOCOMMENT != "":
                with open(CODE_PATH_NOCOMMENT, 'w', encoding='utf-8') as f:
                    f.write(remove_comments_from_file(CODE_PATH_NOCOMMENT))

            # return {
            #     "status": "success",
            #     "code": code_content,
            #     "explanation": non_code_text
            # }
            return {
                "status": "success",
                "code": code_content,
                "reply": non_code_text
            }
        else:
            raise HTTPException(status_code=400, detail="코드 생성에 실패했습니다.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# /revert 엔드포인트 추가
@app.post("/revert")
async def revert_code():
    """코드를 이전 버전으로 되돌리는 엔드포인트"""
    try:
        if os.path.exists(OLD_VERSION):
            with open(OLD_VERSION, 'r', encoding='utf-8') as f:
                old_code = f.read()
            
            with open(CODE_PATH, 'w', encoding='utf-8') as f:
                f.write(old_code)
            
            return {"status": "success", "message": "코드를 이전 버전으로 되돌렸습니다."}
        else:
            raise HTTPException(status_code=404, detail="되돌릴 코드가 없습니다.")
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


