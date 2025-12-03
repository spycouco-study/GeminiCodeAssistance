import os
import json
import random
from pathlib import Path
from typing import Dict, Any, List

# --- 설정 변수 ---
# 1. 실제 'root/' 폴더의 경로로 변경하세요.
ROOT_DIR = r"C:\Users\spyco\Desktop\final_project\VerySimpleTypeScriptProject_AtoZ_Game\public"
# -----------------

def batch_add_likes_to_metadata(root_dir: str):
    """
    root_dir 바로 아래의 모든 하위 폴더를 순회하며
    game_metadata.json 파일에 'likes' 항목을 추가합니다.
    """
    print(f"📁 작업 대상 루트 디렉토리: {root_dir}")
    print("----------------------------------------")
    
    root_path = Path(root_dir)
    processed_count = 0
    
    # root_dir 내의 모든 항목을 순회합니다.
    for folder_path in root_path.iterdir():
        # 디렉토리인 경우에만 작업 수행
        if folder_path.is_dir():
            folder_name = folder_path.name
            metadata_file_path = folder_path / "game_metadata.json"
            
            print(f"\n--- ⚙️ {folder_name} 작업 시작 ---")

            if metadata_file_path.exists():
                try:
                    # 1. JSON 파일 읽기
                    with open(metadata_file_path, 'r', encoding='utf-8') as f:
                        data: Dict[str, Any] = json.load(f)
                    
                    # 2. 'plays' 값 확인 및 'likes' 값 생성
                    plays_value = data.get('plays')
                    
                    if isinstance(plays_value, int) and plays_value >= 0:
                        # plays 값보다 작거나 같은 0 이상의 난수 생성
                        likes_value = random.randint(0, plays_value)
                        
                        # 3. 'likes' 항목 추가/수정 (키값은 영어로)
                        data['likes'] = likes_value
                        
                        # 4. JSON 파일에 수정된 데이터 쓰기
                        with open(metadata_file_path, 'w', encoding='utf-8') as outfile:
                            json.dump(data, outfile, ensure_ascii=False, indent=4)
                        
                        print(f"   ✅ 'likes' 항목 추가 및 저장 완료: plays={plays_value}, likes={likes_value}")
                        processed_count += 1
                        
                    else:
                        print(f"   ⚠️ 'plays' 항목이 없거나 유효한 정수 값이 아닙니다. 수정 건너뜀.")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ 오류: {metadata_file_path.name} 파일이 유효한 JSON 형식이 아닙니다. 건너뜀.")
                except Exception as e:
                    print(f"   ❌ 오류: 파일 처리 중 예외 발생: {e}")
            else:
                print(f"   ⚠️ 경고: {metadata_file_path.name} 파일을 찾을 수 없습니다. 건너뜀.")
                
            print(f"--- 🏁 {folder_name} 작업 완료 ---")
        
    print(f"\n========================================")
    print(f"✨ 최종: 총 {processed_count}개의 game_metadata.json 파일 수정 완료.")
    print("========================================")


if __name__ == "__main__":
    # 안전 점검
    if not os.path.isdir(ROOT_DIR):
        print(f"🔥 오류: root 디렉토리 '{ROOT_DIR}'를 찾을 수 없습니다. 경로를 확인해주세요.")
    else:
        batch_add_likes_to_metadata(ROOT_DIR)