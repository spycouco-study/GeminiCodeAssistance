import json
import os
import shutil

# 1. 입력 JSON 데이터
json_str = '''{
    "game": {
        "boardWidth": 6,
        "boardHeight": 12,
        "hiddenRows": 2,
        "cellSize": 40,
        "puyoColors": ["red", "green", "blue", "yellow", "purple"],
        "gravitySpeed": 1.5,
        "fallAcceleration": 10,
        "resolutionFallSpeed": 20.0,
        "minMatchCount": 4,
        "chainBonusMultiplier": 2,
        "scorePerPuyo": 10,
        "titleScreenText": "PUYO PUYO CLONE",
        "startPromptText": "Press SPACE to Start",
        "gameOverText": "GAME OVER!",
        "gameOverPromptText": "Press SPACE to Restart",
        "nextPuyoPreviewCount": 3,
        "uiPanelWidthCells": 4
    },
    "keys": {
        "moveLeft": "ArrowLeft",
        "moveRight": "ArrowRight",
        "moveDown": "ArrowDown",
        "rotateLeft": "KeyZ",
        "rotateRight": "KeyX",
        "startGame": "Space",
        "hardDrop": "KeyC"
    },
    "assets": {
        "images": [
            { "name": "background", "path": "assets/background.png", "width": 480, "height": 720 },
            { "name": "puyo_red", "path": "assets/puyo_red.png", "width": 40, "height": 40 },
            { "name": "puyo_green", "path": "assets/puyo_green.png", "width": 40, "height": 40 },
            { "name": "puyo_blue", "path": "assets/puyo_blue.png", "width": 40, "height": 40 },
            { "name": "puyo_yellow", "path": "assets/puyo_yellow.png", "width": 40, "height": 40 },
            { "name": "puyo_purple", "path": "assets/puyo_purple.png", "width": 40, "height": 40 }
        ],
        "sounds": [
            { "name": "bgm", "path": "assets/bgm.mp3", "volume": 0.3, "loop": true },
            { "name": "match_sfx", "path": "assets/match_sfx.mp3", "volume": 0.7, "loop": false },
            { "name": "chain_sfx", "path": "assets/chain_sfx.mp3", "volume": 0.8, "loop": false }
        ]
    }
}'''

# 2. 설정 변수
DUMMY_DIR = 'dummy_data/dummy_sound'   # 더미 사운드 파일이 있는 폴더
#TARGET_DIR = 'assets' # 사운드 파일이 복사될 타겟 폴더
TARGET_DIR = os.path.dirname(os.path.abspath(__file__)) # 현재 스크립트 디렉토리
DUMMY_BGM = os.path.join(DUMMY_DIR, 'bgm.mp3') # 더미 BGM 파일 경로
DUMMY_SFX = os.path.join(DUMMY_DIR, 'sfx.mp3') # 더미 SFX 파일 경로


def prepare_dummy_files():
    """테스트를 위해 더미 파일과 디렉토리를 생성합니다."""
    # 더미 폴더 및 타겟 폴더 생성
    os.makedirs(DUMMY_DIR, exist_ok=True)
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # 더미 BGM 파일 생성 (빈 파일)
    with open(DUMMY_BGM, 'w') as f:
        f.write('This is dummy BGM content.')
    print(f"✅ 더미 BGM 파일 생성: {DUMMY_BGM}")
        
    # 더미 SFX 파일 생성 (빈 파일)
    with open(DUMMY_SFX, 'w') as f:
        f.write('This is dummy SFX content.')
    print(f"✅ 더미 SFX 파일 생성: {DUMMY_SFX}")


def copy_and_rename_sound_files(data, base_directory):
    """
    새로운 JSON 형식에 맞춰 이미지 파일을 생성합니다.
    """
    # 새로운 데이터 형식: data['assets']['images']
    sounds_to_process = data.get('assets', {}).get('sounds', [])
    
    # 사운드 파일의 경로에서 디렉토리만 추출하여 미리 생성합니다.
    if sounds_to_process:
        # 첫 번째 항목의 경로에서 디렉토리 경로(예: 'assets')를 추출하여 생성합니다.
        # 모든 파일이 'assets/'와 같은 동일한 디렉토리에 있다고 가정합니다.
        first_path = sounds_to_process[0].get('path', '')
        # os.path.dirname('assets/player.png') => 'assets'
        target_directory = os.path.join(base_directory, os.path.dirname(first_path)) 
    else:
        print("⚠️ 경고: 처리할 이미지 항목이 없습니다.")
        return

    # 타겟 디렉토리가 없으면 생성 (예: assets/)
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        print(f"📁 디렉토리 생성: {target_directory}")


    # 더미 파일 존재 여부 확인
    if not os.path.exists(DUMMY_BGM) or not os.path.exists(DUMMY_SFX):
        print("❌ 오류: 더미 사운드 파일 (bgm.mp3 또는 sfx.mp3)이 dummy_sound 폴더에 없습니다. 작업을 중단합니다.")
        return

    print(f"\n--- 사운드 파일 복사 및 이름 변경 시작 (타겟 경로: {target_directory}) ---")

    for item in sounds_to_process:
        target_file_name = os.path.basename(item.get('path'))
        duration = item.get('duration_seconds')

        if not target_file_name:
            print("⚠️ 경고: 파일 이름 정보가 누락되어 스킵합니다.")
            continue

        # 1. 사용할 더미 파일 경로 결정 (파일 선택 로직)
        source_dummy_path = None
        selection_reason = ""
        
        # 조건 1: duration_seconds가 30.0 이상인 경우 (BGM)
        if isinstance(duration, (int, float)) and duration >= 30.0:
            source_dummy_path = DUMMY_BGM
            selection_reason = "조건 1 (Duration >= 30.0s)"
        
        # 조건 2: duration_seconds 조건에 해당하지 않으면서 파일 이름에 'bgm'이 포함된 경우 (BGM)
        elif 'bgm' in target_file_name.lower():
             source_dummy_path = DUMMY_BGM
             selection_reason = "조건 2 (파일명에 'bgm' 포함)"
        
        # 조건 3: 그 외 모든 경우 (SFX)
        else:
            source_dummy_path = DUMMY_SFX
            selection_reason = "조건 3 (SFX 기본값)"

        # 2. 타겟 경로 설정
        target_path = os.path.join(target_directory, target_file_name)
        
        # 3. 파일 복사 및 이름 변경
        try:
            if os.path.exists(target_path):
                print(f"   (SKIP) 파일이 이미 존재합니다: {target_file_name}")
            else:
                shutil.copy2(source_dummy_path, target_path)
                print(f"   ✅ 복사 완료: '{os.path.basename(source_dummy_path)}' -> '{target_file_name}' ({selection_reason})")
        except Exception as e:
            print(f"   ❌ 복사 중 오류 발생: {target_file_name} - {e}")

    print("--- 사운드 파일 복사 및 이름 변경 완료 ---")

# 1. 더미 파일 및 폴더 준비 (실제 mp3 파일이 없으므로 테스트를 위해 빈 파일 생성)
#prepare_dummy_files()

# # 2. 함수 실행
# json_data = json.loads(json_str)
# copy_and_rename_sound_files(json_data, TARGET_DIR)