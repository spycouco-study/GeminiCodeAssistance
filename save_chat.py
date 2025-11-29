import json
from pathlib import Path
from typing import Literal

from realtime import Dict, List, Union

# 'from' 필드에 들어갈 수 있는 값의 타입을 명확히 정의
Sender = Literal["user", "bot"]

def save_chat(file_path: str, sender: Sender, text: str):
    """
    채팅 내용을 지정된 JSON 파일에 새로운 배열 항목으로 추가합니다.

    Args:
        file_path (str): chat.json 파일의 경로.
        sender (Sender): 메시지 발신자 ("user" 또는 "bot").
        text (str): 채팅 내용.
    """
    
    file = Path(file_path)
    
    # 1. 파일이 없으면 초기 JSON 구조 생성 및 저장
    if not file.exists():
        initial_data = {"chat": []}
        try:
            file.parent.mkdir(parents=True, exist_ok=True) # 부모 폴더가 없다면 생성
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=4)
            print(f"💡 {file_path} 파일이 새로 생성되었습니다.")
        except Exception as e:
            print(f"❌ 파일 생성 오류: {e}")
            return

    # 2. 파일에서 기존 JSON 데이터 읽어오기
    try:
        with open(file, 'r', encoding='utf-8') as f:
            # json.load()로 파일 내용을 파이썬 딕셔너리로 읽습니다.
            data = json.load(f)
            
    except json.JSONDecodeError:
        print(f"❌ 오류: {file_path} 파일의 JSON 형식이 올바르지 않아 초기화합니다.")
        data = {"chat": []}
        
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return

    # 3. 새로운 채팅 항목 생성 및 배열에 추가
    new_entry = {
        "from": sender,
        "text": text
    }
    
    # 'chat' 배열이 있는지 확인하고 배열이 아니면 초기화
    if "chat" not in data or not isinstance(data["chat"], list):
         data["chat"] = []
         
    data["chat"].append(new_entry)

    # 4. 수정된 데이터를 파일에 다시 덮어쓰기
    try:
        # 'w' 모드로 파일을 다시 열어 기존 내용을 덮어씁니다.
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        #print(f"✅ 채팅 기록 추가 성공: [{sender}] '{text[:20]}...' -> {file_path}")
        print(f"✅ 채팅 기록 추가 성공: [{sender}] '{text[:20]}...'")
        
    except Exception as e:
        print(f"❌ 파일 쓰기 오류: {e}")



def load_chat(file_path: str) -> Union[Dict[str, List[Dict[str, str]]], None]:
    """
    지정된 경로의 JSON 파일에서 채팅 내용을 불러옵니다.

    Args:
        file_path (str): chat.json 파일의 경로.

    Returns:
        Union[Dict[str, List[Dict[str, str]]], None]: 
        파일 내용이 담긴 딕셔너리 ({"chat": [...]}) 또는 오류 시 None.
    """
    file = Path(file_path)

    # 1. 파일 존재 여부 확인
    if not file.exists():
        print(f"⚠️ 경고: 채팅 파일 '{file_path}'이 존재하지 않습니다. 빈 데이터 반환.")
        return {"chat": []} # 파일이 없으면 빈 채팅 구조 반환
    
    # 2. 파일 읽기 및 JSON 파싱
    try:
        with open(file, 'r', encoding='utf-8') as f:
            # json.load()로 파일 내용을 파이썬 딕셔너리로 읽습니다.
            data = json.load(f)
            
            # 'chat' 키가 없거나 리스트가 아니면 빈 구조 반환 (데이터 무결성 확인)
            if not isinstance(data.get("chat"), list):
                print(f"⚠️ 경고: '{file_path}' 파일의 'chat' 키가 유효하지 않습니다. 빈 구조 반환.")
                return {"chat": []}
                
            return data
            
    except json.JSONDecodeError:
        print(f"❌ 오류: '{file_path}' 파일의 JSON 형식이 올바르지 않습니다.")
        return None
        
    except Exception as e:
        print(f"❌ 파일 읽기 중 알 수 없는 오류가 발생했습니다: {e}")
        return None



# --- 실행 예시 ---
if __name__ == "__main__":
    
    FILE_PATH = "chat_logs/session_1.json"
    
    # 1. 파일이 없는 상태에서 처음 호출
    save_chat(FILE_PATH, "user", "안녕하세요. 채팅 기록을 시작합니다.")
    
    # 2. 두 번째 호출 (새 항목 추가)
    save_chat(FILE_PATH, "bot", "네, 사용자님의 메시지를 기록했습니다.")
    
    # 3. 세 번째 호출
    save_chat(FILE_PATH, "user", "이제 비행기 게임을 만들어줘. 파일이 계속 업데이트 되고 있죠?")
    
    print("\n--- 최종 파일 내용 확인 ---")
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            print(f.read())
    except:
        print("파일 읽기 실패.")