import json
import os
import shutil
from base_dir import ASSETS_PATH, PROJECT_ROOT
from classes import SoundSelecterProcessor
from model_info_gemini import gemini_client, model_name
from remove_code_fences_safe import remove_code_fences_safe



REQUIRED_EXTENSION = ".mp3"
SOURCE_DIR = PROJECT_ROOT / "dummy_data/sound_sources"




ssp = SoundSelecterProcessor()

def generate_sound(game_name, file_name, description, isBackgroundMusic, duration_seconds):
    return

def generate_sounds(game_name, sound_asset_info):
    DESTINATION_DIR = ASSETS_PATH(game_name)

    prompt = ssp.get_final_prompt(sound_asset_info)

    print(f"AI 모델이 사운드를 선택 중 입니다: {model_name}...")
    response = gemini_client.models.generate_content(
        model=model_name,
        #config = config,
        contents=prompt
    )
    
    match_result = json.loads(remove_code_fences_safe(response.text))    

    for snd in match_result.get('match_result', []):
        # 1. 원본 파일 경로 생성: match_item에 확장자 추가
        # 원본 파일명에 이미 확장자가 포함되어 있을 경우를 대비해 os.path.splitext로 분리 후 다시 합칩니다.
        base_match_item, _ = os.path.splitext(snd['match_item'])
        source_file_name = base_match_item + REQUIRED_EXTENSION
        
        # 원본 파일의 전체 경로 (SOURCE_DIR 내부의 파일이라고 가정)
        source_file_path = os.path.join(SOURCE_DIR, source_file_name)
        
        # 2. 목적지 파일 경로 생성: file_name에 확장자 추가
        base_file_name, _ = os.path.splitext(snd['file_name'])
        destination_file_name = base_file_name + REQUIRED_EXTENSION
        
        # 목적지 파일의 전체 경로
        destination_file_path = os.path.join(DESTINATION_DIR, destination_file_name)
        
        try:
            # 3. 파일 복사 및 이름 변경
            shutil.copyfile(source_file_path, destination_file_path)
            print(f"✅ 복사 완료: '{source_file_path}' -> '{destination_file_path}'")
            
        except FileNotFoundError:
            print(f"❌ 오류: 원본 파일을 찾을 수 없습니다. 경로: {source_file_path}")
        except Exception as e:
            print(f"❌ 오류: 파일 복사 중 예외 발생: {e}")


# json_str = json_str = """
# {
#     "images": [
#         {
#             "file_name": "title_background.png",
#             "description": "A dark, futuristic city skyline at night with neon lights and a prominent glowing 'NEO-SERPENT' title in the center. The style should be cyberpunk/sci-fi, with a sense of technology and mystery.",
#             "isBackgroundImage": true,
#             "width": 800,
#             "height": 600
#         },
#         {
#             "file_name": "instructions_background.png",
#             "description": "A subtle, glowing circuit board pattern or holographic grid on a dark background. It should convey information and technology, with a slightly translucent effect allowing text to be readable.",
#             "isBackgroundImage": true,
#             "width": 800,
#             "height": 600
#         },
#         {
#             "file_name": "game_background.png",
#             "description": "A deep space background with distant stars, nebulae, or a minimal glowing grid overlay, suggesting a digital arena or a starfield. It should be dark but with subtle cosmic elements.",
#             "isBackgroundImage": true,
#             "width": 800,
#             "height": 600
#         },
#         {
#             "file_name": "game_over_background.png",
#             "description": "A glitchy, red-tinged screen with broken digital patterns and error symbols, conveying a sense of system failure or data corruption. The background should feel like a critical error message.",
#             "isBackgroundImage": true,
#             "width": 800,
#             "height": 600
#         },
#         {
#             "file_name": "snake_head.png",
#             "description": "The head of a sci-fi 'Neo-Serpent'. It should be sleek, metallic, with glowing blue or green eyes/sensors, and a distinct, aggressive design. The background should be a plain color like green for easy removal.",
#             "isBackgroundImage": false,
#             "width": 64,
#             "height": 64
#         },
#         {
#             "file_name": "snake_body.png",
#             "description": "A segment of the sci-fi 'Neo-Serpent' body. It should be segmented, metallic, possibly with integrated glowing lines or energy conduits, consistent with the head design. The background should be a plain color like green for easy removal.",
#             "isBackgroundImage": false,
#             "width": 64,
#             "height": 64
#         },
#         {
#             "file_name": "snake_tail.png",
#             "description": "The tail end of the sci-fi 'Neo-Serpent'. It should taper off, perhaps with a small thruster or a distinct end cap, matching the overall sleek, metallic, glowing design. The background should be a plain color like green for easy removal.",
#             "isBackgroundImage": false,
#             "width": 64,
#             "height": 64
#         },
#         {
#             "file_name": "food_item.png",
#             "description": "A glowing, crystalline energy cube or a floating data module. It should emit a soft, pulsing light, perhaps blue or purple, to make it distinct and appealing. The background should be a plain color like green for easy removal.",
#             "isBackgroundImage": false,
#             "width": 64,
#             "height": 64
#         }
#     ],
#     "sounds": [
#         {
#             "file_name": "bgm_sci_fi.mp3",
#             "description": "An atmospheric, synth-heavy background music track with a driving but not overly distracting beat. It should evoke a sense of futuristic exploration or suspense, suitable for a sci-fi game.",
#             "isBackgroundMusic": true,
#             "duration_seconds": 120
#         },
#         {
#             "file_name": "sfx_eat.mp3",
#             "description": "A short, satisfying futuristic 'chime' or 'power-up' sound effect, indicating the snake has consumed the energy cube.",
#             "isBackgroundMusic": false,
#             "duration_seconds": 0.5
#         },
#         {
#             "file_name": "sfx_game_over.mp3",
#             "description": "A dramatic, slightly glitchy or descending sci-fi sound effect, signifying a game over, perhaps with a low hum or a digital 'flatline'.",
#             "isBackgroundMusic": false,
#             "duration_seconds": 2.0
#         },
#         {
#             "file_name": "sfx_menu_select.mp3",
#             "description": "A crisp, high-tech 'beep' or 'click' sound effect suitable for menu navigation or selection in a futuristic interface.",
#             "isBackgroundMusic": false,
#             "duration_seconds": 0.2
#         }
#     ]
# }
# """
# json_data = json.loads(json_str)
# aaa = json_data.get('sounds', [])
# generate_sounds("sy_scifi_snake", aaa)