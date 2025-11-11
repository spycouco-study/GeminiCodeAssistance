import json
import os
from PIL import Image

# 1. 입력 JSON 데이터
json_data = {
    "images": [
        {
            "file_name": "player.png",
            "resolution": {
                "width": 32,
                "height": 32
            }
        },
        {
            "file_name": "player_bullet.png",
            "resolution": {
                "width": 10,
                "height": 20
            }
        },
        {
            "file_name": "enemy1.png",
            "resolution": {
                "width": 32,
                "height": 32
            }
        },
        {
            "file_name": "enemy2.png",
            "resolution": {
                "width": 32,
                "height": 32
            }
        },
        {
            "file_name": "enemy_bullet.png",
            "resolution": {
                "width": 8,
                "height": 16
            }
        },
        {
            "file_name": "background.png",
            "resolution": {
                "width": 480,
                "height": 960
            }
        }
    ],
    "sounds": []
}

# 2. 설정 변수
TARGET_DIR = 'assets'  # 파일 검사 및 생성 대상 폴더
# 단색으로 사용할 고유한 색상 리스트 (RGB 튜플)
# 파일이 6개이므로 6개의 고유한 색상 준비
UNIQUE_COLORS = [
    (255, 0, 0),    # 빨강
    (0, 255, 0),    # 초록
    (0, 0, 255),    # 파랑
    (255, 255, 0),  # 노랑
    (255, 0, 255),  # 마젠타
    (0, 255, 255),  # 시안
    (128, 128, 128) # 회색 (여분의 색상)
]

def check_and_create_images(data, target_directory):
    """
    JSON 데이터를 기반으로 특정 폴더에 파일이 존재하는지 검사하고,
    없을 경우 고유한 단색의 이미지 파일을 생성합니다.
    """
    
    # 대상 폴더가 없으면 생성
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        print(f"✅ 대상 폴더 '{target_directory}'를 생성했습니다.")

    images_to_process = data.get('images', [])
    color_index = 0
    
    # images 리스트를 순회하며 작업 수행
    for item in images_to_process:
        file_name = item.get('file_name')
        resolution = item.get('resolution', {})
        width = resolution.get('width')
        height = resolution.get('height')
        
        if not (file_name and width and height):
            print(f"⚠️ 경고: 파일 이름 또는 해상도 정보가 불완전합니다. 스킵: {item}")
            continue

        file_path = os.path.join(target_directory, file_name)
        
        # 1. 파일 존재 여부 검사
        if os.path.exists(file_path):
            print(f"👍 파일이 이미 존재합니다: {file_name}")
        else:
            # 2. 파일이 없으면 단색 이미지 생성
            
            # 사용할 색상 선택 (고유한 색상 리스트를 순환하여 사용)
            # color_index가 리스트 크기를 넘어서면 다시 0으로 돌아가도록 % 연산 사용
            color = UNIQUE_COLORS[color_index % len(UNIQUE_COLORS)]
            color_index += 1
            
            # PIL 라이브러리를 사용하여 단색 이미지 생성
            try:
                # 'RGB' 모드, (너비, 높이) 크기, (R, G, B) 색상으로 이미지 객체 생성
                img = Image.new('RGB', (width, height), color)
                img.save(file_path)
                print(f"✨ 파일이 없으므로 생성했습니다: {file_name} ({width}x{height}, 색상: {color})")
            except Exception as e:
                print(f"❌ 이미지 생성 중 오류 발생: {file_name} - {e}")
                
# 함수 실행
print("--- 이미지 파일 검사 및 생성 시작 ---")
check_and_create_images(json_data, TARGET_DIR)
print("--- 이미지 파일 검사 및 생성 완료 ---")