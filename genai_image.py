import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# # ⚠️ API 키가 환경 변수 'GEMINI_API_KEY'에 설정되어 있어야 합니다.
# try:
#     client = genai.Client()
# except Exception as e:
#     print(f"클라이언트 초기화 오류: {e}")
#     # 실제 사용 시: 여기서 프로그램 종료 또는 적절한 예외 처리

# 환경 변수 로드
load_dotenv()

# Gemini API 초기화
gemini_api_key = os.getenv('GEMINI_API_KEY')
model_name = 'gemini-2.5-flash-image'

try:
    gemini_client = genai.Client(api_key=gemini_api_key)
except Exception as e:
    # 환경 변수가 설정되지 않은 경우를 처리
    print(f"클라이언트 초기화 오류: {e}")
    print("환경 변수 GEMINI_API_KEY가 설정되었는지 확인해 주세요.")
    exit()



def nano_banana_style_image_editing(reference_image_path: str, editing_prompt: str, output_filename: str):
    """
    Gemini 모델을 사용하여 참고 이미지를 기반으로 이미지를 편집하고 저장합니다.
    """
    if not os.path.exists(reference_image_path):
        print(f"❌ 오류: 참고 이미지 파일 '{reference_image_path}'를 찾을 수 없습니다.")
        return
        
    print(f"--- '{reference_image_path}' 기반 이미지 편집 중 ---")
    
    try:
        # 1. 이미지 파일 로드
        ref_img = Image.open(reference_image_path)
        
        # 2. 이미지와 텍스트 요청을 contents 리스트로 구성
        contents = [
            editing_prompt,  # 사용자가 원하는 변경 사항
            ref_img          # 참고 이미지
        ]
        
        # 3. 모델 호출 (이미지 편집에 특화된 모델 사용)
        # 중요: response_modalities를 설정하여 모델이 텍스트가 아닌 이미지를 반환하도록 지시
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash-image',  # 'nano banana'와 관련된 이미지 편집 모델
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                number_of_images=1,
                mime_type="image/png",
                image_config=types.ImageConfig(
                    aspect_ratio="1:1"
                    # style="VIBRANT" 등 추가적인 이미지 스타일 옵션 사용 가능
                )
            )
        )
        
        # 4. 생성된 이미지 데이터를 파일로 저장
        if response.images:
            image_bytes = response.images[0].image.image_bytes
            with open(output_filename, "wb") as f:
                f.write(image_bytes)
            print(f"✅ 이미지 편집 완료 및 '{output_filename}'에 저장됨.")
        else:
            print("❌ 이미지 생성 결과가 없습니다. (모델이 텍스트를 반환했을 수 있습니다.)")

    except Exception as e:
        print(f"❌ 예기치 않은 오류 발생: {e}")


# --- 사용 예시 ---

# 1. 참고 이미지 파일 경로 (이 파일을 현재 디렉토리에 미리 준비해야 합니다)
REFERENCE_IMAGE = "reference_photo.png" 

# 2. 참고 이미지에 적용할 편집 요청
EDIT_REQUEST = "캐릭터가 정면을 보고 점프하는 장면의 애니메이션을 만들기 위한 스프라이트 시트 이미지 16컷을 그려줘."

# 3. 최종 출력 파일 이름
OUTPUT_IMAGE = "result.png"

# ----------------------------------------------------------

nano_banana_style_image_editing(
    reference_image_path=REFERENCE_IMAGE,
    editing_prompt=EDIT_REQUEST,
    output_filename=OUTPUT_IMAGE
)