import colorsys
import json
import os
from PIL import Image, ImageDraw, ImageFont # ImageDraw, ImageFont 추가

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

# ... (json_data는 이전과 동일) ...
TARGET_DIR = 'assets'

# 폰트 설정 (시스템에 존재하는 폰트 경로를 사용하거나, .ttf 파일을 직접 지정)
# 예시: Arial 폰트, 크기 12
# Windows: "arial.ttf" 또는 "C:/Windows/Fonts/arial.ttf"
# macOS: "/System/Library/Fonts/Arial.ttf"
# Linux: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" 등
# 없으면 기본 폰트를 사용하거나, 예외 처리 필요
try:
    # 적절한 폰트 경로를 지정하세요. (없으면 주석 처리하여 DefaultFont 사용)
    # font = ImageFont.truetype("arial.ttf", 12)
    # 아래는 Pillow가 제공하는 기본 폰트를 사용하거나,
    # 폰트 파일이 없을 경우 오류를 피하기 위한 예시입니다.
    # 보통 Pillow는 자체 내장 기본 폰트를 가지고 있습니다.
    font = ImageFont.load_default()
except IOError:
    print("⚠️ 경고: 지정된 폰트 파일을 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    font = ImageFont.load_default()

# 텍스트 색상 (배경색과 대비되도록 검정색 또는 흰색)
TEXT_COLOR_LIGHT_BG = (0, 0, 0)   # 밝은 배경에 검정 글씨
TEXT_COLOR_DARK_BG = (255, 255, 255) # 어두운 배경에 흰 글씨


def generate_unique_rgb_color(index, total_items):
    # ... (이전과 동일) ...
    if total_items == 0:
        return (255, 255, 255) # 항목이 없으면 흰색 반환

    hue = index / total_items
    saturation = 1.0
    value = 1.0

    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return (int(r * 255), int(g * 255), int(b * 255))


def get_luminance(rgb_color):
    """RGB 색상의 밝기(휘도)를 계산하여 텍스트 색상을 결정하는 데 사용합니다."""
    r, g, b = rgb_color
    # ITU-R BT.709 표준에 따른 휘도 계산 공식
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return luminance


def check_and_create_images_with_text(data, target_directory):
    """
    HSV 기반 색상 생성 및 파일명 텍스트를 이미지에 그려 넣는 함수.
    """
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    images_to_process = data.get('images', [])
    total_items = len(images_to_process)

    for index, item in enumerate(images_to_process):
        file_name = item.get('file_name')
        resolution = item.get('resolution', {})
        width = resolution.get('width')
        height = resolution.get('height')

        if not (file_name and width and height):
            print(f"⚠️ 경고: 파일 이름 또는 해상도 정보가 불완전합니다. 스킵: {item}")
            continue

        # 파일명에서 확장자를 제거하고 순수한 이름만 추출
        base_name = os.path.splitext(file_name)[0]
        
        # 'base_name'을 사용하여 이미지에 그립니다.
        text_to_draw = base_name

        file_path = os.path.join(target_directory, file_name)

        if os.path.exists(file_path):
            print(f"👍 파일이 이미 존재합니다: {file_name}")
        else:
            color = generate_unique_rgb_color(index, total_items)

            try:
                img = Image.new('RGB', (width, height), color)
                draw = ImageDraw.Draw(img) # 이미지를 그릴 Draw 객체 생성

                # 배경색의 밝기에 따라 텍스트 색상 결정 (대비되게)
                luminance = get_luminance(color)
                text_color = TEXT_COLOR_DARK_BG if luminance < 0.5 else TEXT_COLOR_LIGHT_BG

                # 텍스트 크기 계산 (폰트에 따라 다름)
                # getbbox는 텍스트의 (left, top, right, bottom)을 반환
                # font.getsize는 이제 Deprecated 되었으므로 getbbox를 사용합니다.
                try:
                    bbox = draw.textbbox((0,0), text_to_draw, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except AttributeError:
                    # Pillow 버전이 오래되어 textbbox를 지원하지 않을 경우 대체
                    # 이 방법은 정확하지 않을 수 있습니다.
                    text_width, text_height = font.getsize(text_to_draw)


                # 텍스트를 이미지 중앙에 배치
                x = (width - text_width) / 2
                y = (height - text_height) / 2

                # 텍스트 그리기
                draw.text((x, y), text_to_draw, font=font, fill=text_color)

                img.save(file_path)
                print(f"✨ 파일 생성: {file_name} ({width}x{height}, 고유 색상: {color}, 텍스트 추가됨)")
            except Exception as e:
                print(f"❌ 이미지 생성 중 오류 발생: {file_name} - {e}")

# 함수 실행 (이제 이 함수를 호출)
print("--- 텍스트 포함 이미지 파일 검사 및 생성 시작 ---")
check_and_create_images_with_text(json_data, TARGET_DIR)
print("--- 텍스트 포함 이미지 파일 검사 및 생성 완료 ---")