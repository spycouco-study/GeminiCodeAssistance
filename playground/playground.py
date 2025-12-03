import os

# --- 사용자 설정 ---
# 1. 파일 목록을 가져올 대상 폴더 경로
TARGET_DIRECTORY = r"C:\Users\spyco\Desktop\final_project\GeminiCodeAssistance\dummy_data\sound_sources"  # 실제 경로로 변경하세요!
# --------------------

def get_filenames_without_extension_as_comma_separated_string(directory_path):
    """
    지정된 폴더 내의 파일 목록을 가져와 확장자를 제외하고 콤마로 구분된 문자열로 반환합니다.
    """
    
    # 1. 폴더 존재 여부 확인
    if not os.path.isdir(directory_path):
        return f"❌ 오류: 지정된 경로 '{directory_path}'가 존재하지 않거나 폴더가 아닙니다."
    
    # 2. 파일명 저장 리스트 초기화
    names_without_ext = []
    
    try:
        # 3. 폴더 내의 모든 항목을 가져옵니다.
        for item_name in os.listdir(directory_path):
            # 항목의 전체 경로
            full_path = os.path.join(directory_path, item_name)
            
            # 폴더가 아닌 파일만 처리합니다.
            if os.path.isfile(full_path):
                # os.path.splitext(파일명) -> (확장자를 제외한 이름, 확장자) 튜플 반환
                name_only, extension = os.path.splitext(item_name)
                
                # 확장자가 없는 이름만 리스트에 추가합니다.
                names_without_ext.append(name_only)
                
        # 4. 리스트의 항목들을 콤마와 공백으로 구분된 하나의 문자열로 결합합니다.
        result_string = ", ".join(names_without_ext)
        
        return result_string
        
    except PermissionError:
        return f"❌ 오류: 폴더에 접근할 권한이 없습니다: {directory_path}"
    except Exception as e:
        return f"❌ 예상치 못한 오류 발생: {e}"

# 함수 실행 및 결과 출력
result = get_filenames_without_extension_as_comma_separated_string(TARGET_DIRECTORY)

print("--- 처리 결과 ---")
print(result)