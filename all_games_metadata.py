import json
import uuid
import os
from typing import Optional, Dict, Any, List
from base_dir import ALL_GAMES_METADATA



def _load_metadata(file_path: str) -> List[Dict[str, Any]]:
    """JSON 파일을 읽어 메타데이터 리스트를 반환합니다. 파일이 없으면 빈 리스트를 반환합니다."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 메타데이터 파일 읽기 오류: {e}. 빈 리스트로 초기화합니다.")
            return []
    return []

def _save_metadata(file_path: str, data: List[Dict[str, Any]]):
    """메타데이터 리스트를 JSON 파일에 저장합니다."""
    try:
        with open(file_path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)
        print(f"✅ 메타데이터 파일에 저장 완료: {file_path}")
    except Exception as e:
        print(f"❌ 최종 파일 저장 중 오류 발생: {e}")




def upsert_metadata(new_entry: Dict[str, Any]) -> str:    
    # 1. 파일에서 기존 메타데이터 불러오기
    all_metadata = _load_metadata(ALL_GAMES_METADATA())
    
    # 2. 입력 데이터에서 ID 추출 및 처리
    entry_id = new_entry.get('id')
    
    # ID가 없는 경우, 새로 ID를 생성하고 추가 처리로 전환
    if not entry_id:
        entry_id = str(uuid.uuid4())
        new_entry['id'] = entry_id
        
    # 3. ID를 기준으로 기존 항목 검색
    found_index = -1
    for i, item in enumerate(all_metadata):
        if item.get('id') == entry_id:
            found_index = i
            break
            
    # 4. 로직 분기 및 처리
    if found_index != -1:
        # --- UPDATE/REPLACE 로직 ---
        # 기존 항목을 새 항목으로 완전히 교체합니다.
        all_metadata[found_index] = new_entry
        action = "업데이트/교체"
        print(f"🔄 ID '{entry_id}' 항목을 성공적으로 교체했습니다.")
    else:
        # --- INSERT/ADD 로직 ---
        # 리스트의 끝에 새 항목을 추가합니다.
        all_metadata.append(new_entry)
        action = "추가"
        print(f"➕ ID '{entry_id}' 항목을 새로운 데이터로 추가했습니다.")
        
    # 5. 파일에 다시 저장
    _save_metadata(ALL_GAMES_METADATA(), all_metadata)
    
    return entry_id




def add_existing_metadata(new_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    구성된 JSON 데이터를 받아서 파일을 읽고 바로 추가한 후 저장합니다.
    (ID 생성이나 필드 유효성 검사는 수행하지 않습니다.)
    """
    
    # 1. 파일에서 기존 메타데이터 불러오기
    all_metadata = _load_metadata(ALL_GAMES_METADATA())
    
    # 2. 리스트에 새로운 데이터 추가 (입력받은 데이터를 그대로 사용)
    all_metadata.append(new_entry)
    
    # 3. 파일에 다시 저장
    _save_metadata(ALL_GAMES_METADATA(), all_metadata)
    
    # ID가 존재하는지 확인하고 출력
    entry_id = new_entry.get('id', 'ID_MISSING')
    entry_title = new_entry.get('game_title', 'TITLE_MISSING')
    
    print(f"➕ JSON 데이터 추가 완료: ID={entry_id}, Title={entry_title}")
    return new_entry



def add_new_game_metadata(game_title: str, author: str = "unknown", category: str = "etc", description: str = "새로 추가된 재미있는 게임") -> Dict[str, Any]:
    """
    새로운 게임 메타데이터를 생성하고, 파일에 추가하여 저장합니다.
    """
    
    # 1. 파일에서 기존 메타데이터 불러오기
    all_metadata = _load_metadata(ALL_GAMES_METADATA())
    
    # 2. 새로운 메타데이터 객체 생성
    new_entry = {
        "id": str(uuid.uuid4()),  # 새로운 고유 ID 생성
        "game_title": game_title,
        "author": author,
        "category": category,
        "thumbnail": f"/static/{game_title}/assets/thumbnail.png", 
        "plays": 0,
        "description": description,
        "likes":0
    }
    
    # 3. 리스트에 추가
    all_metadata.append(new_entry)
    
    # 4. 파일에 다시 저장
    _save_metadata(ALL_GAMES_METADATA(), all_metadata)
    
    print(f"➕ 새 요소 추가 완료: ID={new_entry['id']}, Title={game_title}")
    return new_entry


def find_metadata_by_id(target_id: str) -> Optional[Dict[str, Any]]:
    """
    파일을 읽어 ID를 사용하여 요소를 검색하고 반환합니다.
    """
    # 1. 파일에서 기존 메타데이터 불러오기
    all_metadata = _load_metadata(ALL_GAMES_METADATA())
    
    # 2. 리스트에서 검색
    found_item = next((item for item in all_metadata if item.get('id') == target_id), None)
    
    if found_item:
        print(f"🔎 요소 검색 성공: ID={target_id}, Title={found_item['game_title']}")
    else:
        print(f"⚠️ 요소 검색 실패: ID={target_id}에 해당하는 요소를 찾을 수 없습니다.")
        
    return found_item


def delete_metadata_by_id(target_id: str) -> bool:
    """
    파일을 읽어 ID를 사용하여 요소를 검색하고 삭제한 후, 파일에 저장합니다.
    """
    # 1. 파일에서 기존 메타데이터 불러오기
    all_metadata = _load_metadata(ALL_GAMES_METADATA())
    
    # 2. 삭제 전 리스트 길이 저장
    initial_length = len(all_metadata)
    
    # 3. ID가 target_id와 같지 않은 요소들만 남기고 리스트를 재구성 (삭제)
    new_metadata = [item for item in all_metadata if item.get('id') != target_id]
    
    # 4. 삭제가 실제로 일어났는지 확인
    if len(new_metadata) < initial_length:
        # 5. 파일에 다시 저장
        _save_metadata(ALL_GAMES_METADATA(), new_metadata)
        print(f"🗑️ 요소 삭제 성공 및 파일 저장 완료: ID={target_id}")
        return True
    else:
        print(f"⚠️ 요소 삭제 실패: ID={target_id}에 해당하는 요소를 찾을 수 없습니다.")
        return False
    



def get_metadata_by_id_list(id_list: List[str]) -> List[Dict[str, Any]]:
    """
    ID 리스트를 받아 해당 ID에 해당하는 모든 메타데이터 항목을 검색하여 리스트로 반환합니다.
    """
    if not id_list:
        print("⚠️ ID 리스트가 비어 있어 빈 결과를 반환합니다.")
        return []

    # 1. 파일에서 전체 메타데이터 불러오기
    all_metadata = _load_metadata(ALL_GAMES_METADATA())
    
    # 2. 검색을 빠르게 하기 위해 ID를 Set 형태로 변환
    target_ids = set(id_list)
    
    # 3. 리스트 컴프리헨션을 사용하여 검색 및 필터링
    # 전체 메타데이터를 순회하며 ID가 target_ids Set에 포함된 항목만 필터링합니다.
    found_items = [
        item for item in all_metadata 
        if item.get('id') in target_ids
    ]
    
    # 검색 결과를 원래 요청된 ID 리스트의 순서대로 정렬해야 하는 경우, 
    # 추가적인 작업이 필요하지만, 여기서는 검색된 항목만 반환합니다.
    
    # 검색 성공/실패 여부 출력 (선택 사항)
    found_count = len(found_items)
    missing_count = len(id_list) - found_count
    
    if missing_count > 0:
        print(f"⚠️ 요청된 {len(id_list)}개 중 {found_count}개만 찾았습니다. {missing_count}개의 ID에 해당하는 항목을 찾을 수 없습니다.")
    else:
        print(f"🔎 요청된 ID {len(id_list)}개 모두에 해당하는 항목을 찾았습니다.")
        
    return found_items



def search_metadata_by_category(target_category: str) -> List[Dict[str, Any]]:
    """
    특정 Category를 사용하여 메타데이터 리스트에서 일치하는 모든 요소를 검색하여 배열로 반환합니다.
    """
    # 1. 파일에서 전체 메타데이터 불러오기
    all_metadata = _load_metadata(ALL_GAMES_METADATA())
    
    # 2. 리스트 컴프리헨션을 사용하여 Category가 일치하는 모든 항목 검색
    # 검색 시 대소문자를 구분하지 않으려면 .lower()를 사용할 수 있습니다.
    # 예: item.get('category', '').lower() == target_category.lower()

    if target_category.lower() == "all":
        return all_metadata
    
    found_items = [
        item for item in all_metadata 
        if item.get('category', '').lower() == target_category.lower()
    ]
    
    found_count = len(found_items)
    if found_count > 0:
        print(f"🔎 Category '{target_category}' 검색 성공: {found_count}개의 항목 반환.")
    else:
        print(f"⚠️ Category '{target_category}'에 해당하는 항목을 찾을 수 없습니다.")
        
    return found_items



def search_metadata_by_author(target_author: str) -> List[Dict[str, Any]]:
    """
    특정 Author(저자)를 사용하여 메타데이터 리스트에서 일치하는 모든 요소를 검색하여 배열로 반환합니다.
    """
    # 1. 파일에서 전체 메타데이터 불러오기
    all_metadata = _load_metadata(ALL_GAMES_METADATA())
    
    # 2. 리스트 컴프리헨션을 사용하여 Author가 일치하는 모든 항목 검색
    # item.get('author')를 사용하여 해당 키가 없더라도 오류를 방지합니다.
    found_items = [
        item for item in all_metadata 
        if item.get('author') == target_author
    ]
    
    found_count = len(found_items)
    if found_count > 0:
        print(f"🔎 Author '{target_author}' 검색 성공: 총 {found_count}개의 항목 반환.")
    else:
        print(f"⚠️ Author '{target_author}'에 해당하는 항목을 찾을 수 없습니다.")
        
    return found_items