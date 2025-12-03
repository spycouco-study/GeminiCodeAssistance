# Gemini API 초기화
import os
from google import genai
from google.genai import types


gemini_api_key = os.getenv('GEMINI_API_KEY')
model_name = "gemini-2.5-flash"
#model_name = "gemini-3-pro-preview"

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