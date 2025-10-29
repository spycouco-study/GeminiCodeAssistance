# import os
# from typing import Dict, List, Union
# from dotenv import load_dotenv
# from supabase import create_client, Client      # PostgreSQL(DB)



# load_dotenv() 



# # PostgreDB 사용 연결
# supabase_url = os.getenv("SUPABASE_URL")
# supabase_key = os.getenv("SUPABASE_ANON_KEY")
# supabase_client: Client = create_client(supabase_url, supabase_key)
# table_name = "history"



# # 사용자 정보를 가져오는 함수
# async def get_user_info(user_id):
#     response = supabase_client.table("users").select("*").eq("user_id", user_id).execute()
#     if response.data:
#         return response.data
#     return None



# # DB로부터 이전 질문 읽기
# async def get_requests_async(userid, prompt):    
#     #response = supabase.table("prompt_tbl").select("id, response").gte("id", id).limit(30).execute()
#     response = supabase_client.table(table_name) \
#     .select("id, prompt, created_at, response") \
#     .eq("userid", userid) \
#     .order("created_at", desc=True) \
#     .limit(3) \
#     .execute()

#     response.data.reverse()

#     questions = ""

#     if response and response.data:
#         data = response.data
#         for row in data:
#             if not row["prompt"].startswith( "http" ):
#                 formatted_time = row['created_at'][5:16]  # YYYY-MM-DD HH:MM -> MM-DD HH:MM
#                 questions += f"{row['prompt']}{row['response']}\n"
#                 #questions += f"{row['id']}, {row['prompt']}({formatted_time})\n"

#         return questions
        


# def get_requests(prompt):
#     #response = supabase.table("prompt_tbl").select("id, response").gte("id", id).limit(30).execute()
#     response = supabase_client.table(table_name).select("id, prompt, created_at, response").order("created_at", desc=True).limit(3).execute()
#     questions = ""

#     if response and response.data:
#         data = response.data
#         for row in data:
#             if not row["prompt"].startswith( "http" ):
#                 formatted_time = row['created_at'][5:16]  # YYYY-MM-DD HH:MM -> MM-DD HH:MM
#                 questions += f"{row['id']}, {row['prompt']}({formatted_time})\n"

#         return questions
    


# def get_session_history(session_id: int) -> List[Dict[str, Union[str, bool]]]:
#     """
#     Supabase에서 특정 session_id와 일치하는 레코드의 채팅 기록을 불러옵니다.

#     Args:
#         session_id: 조회할 세션 ID (int).

#     Returns:
#         List[Dict[str, Union[str, bool]]]: 
#             message(str), recipeList(str), fromUser(bool) 키를 가진 딕셔너리 리스트.
#             조회 실패 시 빈 리스트를 반환합니다.
#     """
#     try:
#         response = (
#             supabase_client.table(table_name)       
#             #.select('message, recipeList, fromUser')
#             .select('message, fromUser, recipeList, additional_info')
#             .eq('chat_id', session_id) 
#             .execute()
#         )
        
#         # 실제 데이터 추출
#         data: List[Dict[str, Union[str, bool]]] = response.data
#         print(f"불러온 레코드 수: {len(data)}")
        
#         return data
        
#     except Exception as e:
#         print(f"데이터 조회 중 오류 발생: {e}")
#         # 오류 발생 시, 함수 계약(Contract)에 따라 빈 리스트를 반환하여 안정성을 높입니다.
#         return [] 



# # Supabase에서 불러온 데이터의 타입
# RawHistoryType = List[Dict[str, Union[str, bool]]]

# def format_chat_history(raw_data: RawHistoryType) -> List[str]:
#     """
#     Supabase에서 불러온 채팅 기록을 '나: ' 또는 'ChatGPT: ' 형식으로 변환합니다.
#     """
#     formatted_messages = []
    
#     for record in raw_data:
#         # fromUser 값에 따라 접두사 결정        
#         from_user = record.get('fromUser', False) # 안전을 위해 기본값 False 설정
#         if from_user is True:
#             prefix = "나: "
#             message = record.get('message', '')
#         else:
#             prefix = "ChatGPT: "
#             message = record.get('recipeList', "")
#             if message == "":
#                 message = record.get('message', '')
#             else:
#                 message = message + "를 추천했습니다."
#                 additional_info = record.get('additional_info', '')
#                 if additional_info != "":
#                     message = message + additional_info
                    
#         # 접두사와 메시지를 결합하여 리스트에 추가
#         formatted_messages.append(prefix + message)
        
#     return formatted_messages



# def save_to_databasee(data_to_insert):
#     try:
#       response = supabase_client.table(table_name).insert(data_to_insert).execute()

#     except Exception as e:
#       error_message = str(e)
#       print( error_message )  
