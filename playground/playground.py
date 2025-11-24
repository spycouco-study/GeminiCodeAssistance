import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

# Gemini API 초기화
gemini_api_key = os.getenv('GEMINI_API_KEY')
# API 키 설정
# genai.Client(api_key=os.environ.get("GEMINI_API_KEY")) 와 같이 환경 변수를 사용하는 것을 권장합니다.
client = genai.Client(api_key=gemini_api_key) 

print("접근 가능한 모델 목록:")
# client.models.list()는 모든 모델 목록을 가져옵니다.
for model in client.models.list():
    # 수정된 부분: model.supported_generation_methods -> model.supported_methods
    # 'models/gemini'로 시작하고 'generateContent'를 지원하는 모델만 필터링합니다.
    #if model.name.startswith("models/gemini") and "generateContent" in model.supported_methods:
        # 출력된 모델 이름 (예: models/gemini-2.5-flash)을 코드에 사용하시면 됩니다.
        print(f"- {model.name}")