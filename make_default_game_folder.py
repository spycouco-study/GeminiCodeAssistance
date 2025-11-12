import os
import shutil
from pathlib import Path
import sys

def create_project_structure(target_path: str):
    """
    주어진 경로에 기본 파일들을 복사하고 'assets' 폴더를 생성합니다.

    Args:
        target_path (str): 파일을 복사하고 구조를 만들 대상 경로입니다.
    """
    
    # 1. 소스 파일 및 폴더의 기준 경로 설정
    # 이 스크립트가 실행되는 디렉토리 기준으로 'dummy_data/default_files' 경로를 설정합니다.
    # sys.argv[0]를 사용하여 스크립트의 경로를 기준으로 설정하는 것이 안전하지만, 
    # 간단하게 현재 작업 디렉토리를 기준으로 설정하겠습니다.
    
    # 주의: 실제 환경에서는 BASE_DIR을 프로젝트 루트로 정확히 지정해야 합니다.
    BASE_DIR = Path(__file__).resolve().parent if '__file__' in locals() else Path(os.getcwd())
    
    # 소스 디렉토리 경로
    SOURCE_DIR = BASE_DIR / "dummy_data" / "default_files" 
    
    # 대상 디렉토리 경로 (사용자 입력)
    DEST_DIR = Path(target_path)
    
    # 복사할 파일 목록
    FILES_TO_COPY = ["index.html", "style.css", "favicon.png"]
    
    try:
        # 2. 대상 경로가 존재하는지 확인하고 없으면 생성
        # exist_ok=True: 이미 경로가 존재해도 오류가 발생하지 않음
        DEST_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ 대상 디렉토리 준비 완료: {DEST_DIR}")

        # 3. 기본 파일 복사
        for filename in FILES_TO_COPY:
            source_file = SOURCE_DIR / filename
            dest_file = DEST_DIR / filename
            
            if source_file.exists():
                # shutil.copy2는 파일 데이터와 메타데이터(수정 시간 등)를 모두 복사합니다.
                shutil.copy2(source_file, dest_file)
                print(f"   -> 파일 복사 완료: {filename}")
            else:
                print(f"⚠️ 경고: 소스 파일이 존재하지 않습니다: {source_file}")

        # 4. 'assets' 폴더 생성
        assets_dir = DEST_DIR / "assets"
        assets_dir.mkdir(exist_ok=True)
        print(f"   -> 폴더 생성 완료: {assets_dir.name}/")

        print("\n✨ 프로젝트 구조 생성이 성공적으로 완료되었습니다.")

    except FileNotFoundError:
        print(f"\n❌ 오류: 소스 디렉토리 ({SOURCE_DIR})를 찾을 수 없습니다. 경로를 확인해주세요.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")

# # --- 실행 부분 ---
# if __name__ == "__main__":
    
#     while True:
#         # 사용자로부터 대상 경로 입력받기
#         target_path = input("파일을 복사할 경로를 입력하세요 (예: my_new_project): ").strip()
        
#         if target_path:
#             # 입력받은 경로로 구조 생성 함수 호출
#             create_project_structure(target_path)
#             break
#         else:
#             print("경로를 반드시 입력해야 합니다. 다시 시도해 주세요.")