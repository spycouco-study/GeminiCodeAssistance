import colorsys
import json
import os
from PIL import Image, ImageDraw, ImageFont # ImageDraw, ImageFont 추가

# 1. 입력 JSON 데이터 (새로운 형식에 맞게 변경)
json_str = '''{
    "assets": {
        "images": [
            { "name": "player", "path": "assets/player.png", "width": 48, "height": 48 },
            { "name": "tile_grass", "path": "assets/tile_grass.png", "width": 64, "height": 64 },
            { "name": "tile_wall", "path": "assets/tile_wall.png", "width": 64, "height": 64 },
            { "name": "item_plastic_bottle", "path": "assets/item_plastic_bottle.png", "width": 32, "height": 32 },
            { "name": "item_newspaper", "path": "assets/item_newspaper.png", "width": 32, "height": 32 },
            { "name": "item_can", "path": "assets/item_can.png", "width": 32, "height": 32 },
            { "name": "monster_player_robot_1", "path": "assets/monster_player_robot_1.png", "width": 40, "height": 40 },
            { "name": "monster_wild_rusty_robot", "path": "assets/monster_wild_rusty_robot.png", "width": 40, "height": 40 },
            { "name": "monster_wild_trash_drone", "path": "assets/monster_wild_trash_drone.png", "width": 40, "height": 40 }
        ],
        "sounds": [
            { "name": "bgm_main", "path": "assets/bgm_main.mp3", "volume": 0.5, "loop": true },
            { "name": "sfx_collect", "path": "assets/sfx_collect.mp3", "volume": 1.0, "loop": false },
            { "name": "sfx_combine", "path": "assets/sfx_combine.mp3", "volume": 1.0, "loop": false },
            { "name": "sfx_hit", "path": "assets/sfx_hit.mp3", "volume": 0.7, "loop": false },
            { "name": "sfx_levelup", "path": "assets/sfx_levelup.mp3", "volume": 1.0, "loop": false },
            { "name": "sfx_defeat", "path": "assets/sfx_defeat.mp3", "volume": 1.0, "loop": false }
        ]
    }
}'''

# TARGET_DIR은 이제 경로 전체를 처리하므로, 저장할 파일의 디렉토리를 TARGET_DIR로 설정합니다.
# 이 예시에서는 TARGET_DIR을 'assets' 폴더의 상위 폴더(현재 스크립트가 실행되는 곳)로 가정하고
# 파일 경로(item['path'])를 사용하여 assets 폴더 내에 파일을 생성하도록 코드를 변경했습니다.
TARGET_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트 디렉토리

# 폰트 설정 (시스템에 존재하는 폰트 경로를 사용하거나, .ttf 파일을 직접 지정)
try:
    font = ImageFont.load_default()
except IOError:
    print("⚠️ 경고: 지정된 폰트 파일을 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    font = ImageFont.load_default()

# 텍스트 색상 (배경색과 대비되도록 검정색 또는 흰색)
TEXT_COLOR_LIGHT_BG = (0, 0, 0)   
TEXT_COLOR_DARK_BG = (255, 255, 255)


def generate_unique_rgb_color(index, total_items):
    """
    HSV 기반으로 고유한 RGB 색상을 생성합니다.
    (이 함수는 변경하지 않았습니다.)
    """
    if total_items == 0:
        return (255, 255, 255) 

    hue = index / total_items
    saturation = 1.0
    value = 1.0

    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return (int(r * 255), int(g * 255), int(b * 255))


def get_luminance(rgb_color):
    """RGB 색상의 밝기(휘도)를 계산하여 텍스트 색상을 결정하는 데 사용합니다."""
    r, g, b = rgb_color
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return luminance


def check_and_create_images_with_text(data, base_directory):
    """
    새로운 JSON 형식에 맞춰 이미지 파일을 생성합니다.
    """
    # 새로운 데이터 형식: data['assets']['images']
    images_to_process = data.get('assets', {}).get('images', [])
    
    # 사운드 파일의 경로에서 디렉토리만 추출하여 미리 생성합니다.
    if images_to_process:
        # 첫 번째 항목의 경로에서 디렉토리 경로(예: 'assets')를 추출하여 생성합니다.
        # 모든 파일이 'assets/'와 같은 동일한 디렉토리에 있다고 가정합니다.
        first_path = images_to_process[0].get('path', '')
        # os.path.dirname('assets/player.png') => 'assets'
        target_directory = os.path.join(base_directory, os.path.dirname(first_path)) 
    else:
        print("⚠️ 경고: 처리할 이미지 항목이 없습니다.")
        return

    # 타겟 디렉토리가 없으면 생성 (예: assets/)
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        print(f"📁 디렉토리 생성: {target_directory}")


    total_items = len(images_to_process)

    for index, item in enumerate(images_to_process):
        # 새로운 키: 'name', 'path', 'width', 'height'
        name = item.get('name')
        file_path_full = item.get('path')
        width = item.get('width')
        height = item.get('height')

        # 'path'에서 순수한 파일 이름(예: 'player.png')만 추출하여 저장에 사용합니다.
        file_name = os.path.basename(file_path_full) 
        
        if not (name and file_path_full and width and height):
            print(f"⚠️ 경고: 파일 정보가 불완전합니다. 스킵: {item}")
            continue

        # 이미지에 그릴 텍스트는 'name' 필드를 사용합니다.
        text_to_draw = name

        # 최종 저장 경로 (예: TARGET_DIR/assets/player.png)
        final_save_path = os.path.join(target_directory, file_name)


        if os.path.exists(final_save_path):
            print(f"👍 파일이 이미 존재합니다: {final_save_path}")
        else:
            color = generate_unique_rgb_color(index, total_items)

            try:
                img = Image.new('RGB', (width, height), color)
                draw = ImageDraw.Draw(img) 

                luminance = get_luminance(color)
                text_color = TEXT_COLOR_DARK_BG if luminance < 0.5 else TEXT_COLOR_LIGHT_BG

                try:
                    # 텍스트 크기 계산 (Pillow 최신 버전 호환)
                    bbox = draw.textbbox((0,0), text_to_draw, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except AttributeError:
                    # 이전 버전 대체
                    text_width, text_height = font.getsize(text_to_draw)

                # 텍스트를 이미지 중앙에 배치
                x = (width - text_width) / 2
                y = (height - text_height) / 2

                draw.text((x, y), text_to_draw, font=font, fill=text_color)

                img.save(final_save_path)
                print(f"✨ 파일 생성: {final_save_path} ({width}x{height}, 고유 색상: {color}, 텍스트 추가됨)")
            except Exception as e:
                print(f"❌ 이미지 생성 중 오류 발생: {final_save_path} - {e}")








# # 함수 실행 (이제 이 함수를 호출)
# print("--- 텍스트 포함 이미지 파일 검사 및 생성 시작 ---")
# # TARGET_DIR은 스크립트가 실행되는 베이스 디렉토리를 의미합니다.
# json_data = json.loads(json_str)
# check_and_create_images_with_text(json_data, TARGET_DIR)
# print("--- 텍스트 포함 이미지 파일 검사 및 생성 완료 ---")