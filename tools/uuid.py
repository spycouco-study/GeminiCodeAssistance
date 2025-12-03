import uuid



def generate_uuid4():
    # UUID4 생성
    unique_id = uuid.uuid4() 

    # 문자열 형태로 사용
    unique_id_str = str(unique_id) 
    return unique_id_str