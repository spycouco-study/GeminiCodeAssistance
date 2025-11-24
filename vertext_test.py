import google.auth
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google.cloud import aiplatform

# --- 1. 환경 설정 ---
# 발급받은 액세스 토큰을 여기에 넣어주세요.
access_token = "YOUR_ACCESS_TOKEN" 

# 프로젝트 ID와 리전을 설정합니다.
PROJECT_ID = " "  # 실제 GCP 프로젝트 ID로 변경하세요
REGION = "us-central1"           # 모델이 배포된 리전으로 변경하세요 (예: us-central1)

# 나노바나나 이미지 생성 모델이 배포된 엔드포인트 ID 또는 모델 이름입니다.
# 실제 Vertex AI 모델 배포 정보에 맞게 변경해야 합니다.
ENDPOINT_ID = "YOUR_ENDPOINT_ID" 
# 또는
# MODEL_NAME = "imagen-3.0-generate-002" 

# --- 2. 액세스 토큰을 Credential 객체로 변환 ---
# google.auth.credentials.Credentials 객체를 사용하여 액세스 토큰을 전달합니다.
# 이 객체를 사용하면 aiplatform.Client 초기화 시 인증이 가능합니다.
class AccessTokenCredentials(Credentials):
    """액세스 토큰을 기반으로 하는 단순 Credential 구현"""
    def __init__(self, token):
        self.token = token
        
    def refresh(self, request: Request):
        # 토큰이 이미 있으므로 갱신 로직은 생략합니다.
        pass

    def get_access_token(self):
        # 토큰, 만료 시간(None), 추가 범위(None)를 반환합니다.
        return self.token, None, None

    @property
    def token_expiry(self):
        # 만료 시간이 없거나 알 수 없음을 나타냅니다.
        return None

# AccessTokenCredentials 인스턴스 생성
credentials = AccessTokenCredentials(access_token)

# --- 3. aiplatform.Client 초기화 ---
# 클라이언트 초기화 시 생성한 credentials 객체를 전달합니다.
client_options = {"api_endpoint": f"{REGION}-aiplatform.googleapis.com"}
aiplatform.init(
    project=PROJECT_ID,
    location=REGION,
    client_options=client_options,
    credentials=credentials # <- 액세스 토큰 기반 Credential 사용
)

# --- 4. 모델 호출 (Prediction) ---
# Prompt(요청) 설정
prompt = "A hyper-realistic image of a nanobanana, glowing blue, floating in space with tiny nebula."

# 이미지 생성 요청을 위한 입력 데이터 구조 (모델에 따라 다를 수 있음)
instances = [
    {"prompt": prompt, "number_of_images": 1}
]

# 예측 요청 실행
try:
    print(f"이미지 생성 모델({ENDPOINT_ID}) 호출 중...")
    
    # 배포된 엔드포인트 호출
    endpoint = aiplatform.Endpoint(endpoint_name=f"projects/{PROJECT_ID}/locations/{REGION}/endpoints/{ENDPOINT_ID}")
    
    # 예측 (predict) 메서드를 사용하여 이미지 생성 요청
    response = endpoint.predict(instances=instances)
    
    # 결과 처리
    print("\n✅ 예측 결과 수신 완료.")
    
    # 이미지 데이터는 일반적으로 base64 인코딩된 문자열 형태로 반환됩니다.
    # 모델 출력 구조에 맞게 `predictions`의 첫 번째 요소를 확인합니다.
    if response.predictions:
        print(f"생성된 이미지 개수: {len(response.predictions)}")
        # 첫 번째 생성된 이미지의 Base64 데이터를 출력합니다.
        print("\n첫 번째 이미지 Base64 데이터 (일부):")
        
        # 모델 응답 구조에 따라 데이터 접근 방식이 다를 수 있습니다.
        # 예: Imagen 모델의 경우 response.predictions[0]['bytesBase64Encoded']
        if 'bytesBase64Encoded' in response.predictions[0]:
            base64_image = response.predictions[0]['bytesBase64Encoded']
            print(base64_image[:50] + "...") # 앞 50자만 출력
            
            # TODO: base64_image를 파일로 저장하거나 웹에 표시하는 추가 작업이 필요합니다.
        else:
             print("모델 응답 구조가 예상과 다릅니다. 실제 모델의 출력 형식을 확인하세요.")
    
except Exception as e:
    print(f"\n❌ API 호출 중 오류 발생: {e}")