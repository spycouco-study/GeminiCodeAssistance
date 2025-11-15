
import os
from pathlib import Path
import threading
from typing import Any, List, Optional, Tuple

from pydantic import BaseModel

class CodePromptTemplateProcessor:
    PROMPT_PATH = Path(__file__).parent / "playground" / "playground.py"
    ROLE = "당신은 정해진 의사코드 로직을 바탕으로 사용자 쿼리가 어떤 카테고리에 속하는지 판별하는 분류기 입니다."
    PREV_TALK_REF = '[이전 대화: "'
    USER_QUERY_REF = '[사용자 쿼리: "'    
    


    def __init__(self):
        self._template_cache: Optional[str] = None # 템플릿 내용을 캐시할 변수
        self.IS_PROMPT_MODIFICATION_MODE = os.getenv('IS_PROMPT_MODIFICATION_MODE') == "True"



    def _load_template(self) -> str:
        if self._template_cache is None or self.IS_PROMPT_MODIFICATION_MODE:
            if not os.path.exists(self.PROMPT_PATH):
                raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {self.PROMPT_PATH}")

            with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
                self._template_cache = f.read()
                
        return self._template_cache

    def get_final_prompt(self, history: List[Any], user_query: str) -> str:
        template = self._load_template()
        prompt_text = template
        
        # 1. 이전 대화(history) 삽입 로직
        find_end = template.find(self.PREV_TALK_REF)
        
        if find_end != -1: # 플레이스홀더를 찾은 경우에만 처리
            insert_point = find_end + len(self.PREV_TALK_REF)
            
            if len(history) > 0:
                history_str = str(history) # history를 문자열로 변환
                prompt_text = prompt_text[:insert_point] + history_str + prompt_text[insert_point:]

        find_end = prompt_text.find(self.USER_QUERY_REF)
        
        if find_end != -1: # 플레이스홀더를 찾은 경우에만 처리
            insert_point = find_end + len(self.USER_QUERY_REF)
            
            before = prompt_text[:insert_point]
            after = prompt_text[insert_point:] # 뒷부분: 따옴표 이후 전부
            prompt_text = before + user_query + after
        
        return self.ROLE, prompt_text




class MakePromptTemplateProcessor:
    PROMPT_PATH = Path(__file__).parent / "prompts" / "make.md"
    


    def __init__(self):
        self._lock = threading.Lock()
        self._template_cache: Optional[str] = None # 템플릿 내용을 캐시할 변수
        self.IS_PROMPT_MODIFICATION_MODE = os.getenv('IS_PROMPT_MODIFICATION_MODE') == "True"



    def _load_template(self) -> str:
        with self._lock:
            if self._template_cache is None or self.IS_PROMPT_MODIFICATION_MODE:
                if not os.path.exists(self.PROMPT_PATH):
                    raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {self.PROMPT_PATH}")

                with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
                    self._template_cache = f.read()
                
        return self._template_cache

    def get_final_prompt(self, user_query, user_question) -> str:
        template = self._load_template()        
        prompt = template.format(user_query=user_query, user_question=user_question)

        return prompt




class ModifyPromptTemplateProcessor:
    PROMPT_PATH = Path(__file__).parent / "prompts" / "modify.md"
    


    def __init__(self):
        self._lock = threading.Lock()
        self._template_cache: Optional[str] = None # 템플릿 내용을 캐시할 변수
        self.IS_PROMPT_MODIFICATION_MODE = os.getenv('IS_PROMPT_MODIFICATION_MODE') == "True"



    def _load_template(self) -> str:
        with self._lock:
            if self._template_cache is None or self.IS_PROMPT_MODIFICATION_MODE:
                if not os.path.exists(self.PROMPT_PATH):
                    raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {self.PROMPT_PATH}")

                with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
                    self._template_cache = f.read()
                
        return self._template_cache

    def get_final_prompt(self, user_query, user_question, original_code, original_data) -> str:
        template = self._load_template()        
        prompt = template.format(user_query=user_query, user_question=user_question, original_code=original_code, original_data=original_data)

        return prompt






class QuestionTemplateProcessor:
    PROMPT_PATH = Path(__file__).parent / "prompts" / "question.md"
    


    def __init__(self):
        self._lock = threading.Lock()
        self._template_cache: Optional[str] = None # 템플릿 내용을 캐시할 변수
        self.IS_PROMPT_MODIFICATION_MODE = os.getenv('IS_PROMPT_MODIFICATION_MODE') == "True"



    def _load_template(self) -> str:
        with self._lock:
            if self._template_cache is None or self.IS_PROMPT_MODIFICATION_MODE:
                if not os.path.exists(self.PROMPT_PATH):
                    raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {self.PROMPT_PATH}")

                with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
                    self._template_cache = f.read()
                
        return self._template_cache

    def get_final_prompt(self, user_question, original_code, original_data) -> str:
        template = self._load_template()        
        prompt = template.format(user_question=user_question, original_code=original_code, original_data=original_data)

        return prompt







class SpecQuestionTemplateProcessor:
    PROMPT_PATH = Path(__file__).parent / "prompts" / "question.md"
    


    def __init__(self):
        self._lock = threading.Lock()
        self._template_cache: Optional[str] = None # 템플릿 내용을 캐시할 변수
        self.IS_PROMPT_MODIFICATION_MODE = os.getenv('IS_PROMPT_MODIFICATION_MODE') == "True"



    def _load_template(self) -> str:
        with self._lock:
            if self._template_cache is None or self.IS_PROMPT_MODIFICATION_MODE:
                if not os.path.exists(self.PROMPT_PATH):
                    raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {self.PROMPT_PATH}")

                with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
                    self._template_cache = f.read()
                
        return self._template_cache

    def get_final_prompt(self, history, user_query, specification) -> str:
        template = self._load_template()        
        prompt = template.format( history = history,
                                user_query=user_query,
                                specification=specification)

        return prompt



class SpecQuestionTemplateProcessor:
    PROMPT_PATH = Path(__file__).parent / "prompts" / "spec_question.md"
    


    def __init__(self):
        self._lock = threading.Lock()
        self._template_cache: Optional[str] = None # 템플릿 내용을 캐시할 변수
        self.IS_PROMPT_MODIFICATION_MODE = os.getenv('IS_PROMPT_MODIFICATION_MODE') == "True"



    def _load_template(self) -> str:
        with self._lock:
            if self._template_cache is None or self.IS_PROMPT_MODIFICATION_MODE:
                if not os.path.exists(self.PROMPT_PATH):
                    raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {self.PROMPT_PATH}")

                with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
                    self._template_cache = f.read()
                
        return self._template_cache

    def get_final_prompt(self, history, user_query, specification) -> str:
        template = self._load_template()        
        prompt = template.format( history = history,
                                user_query=user_query,
                                specification=specification)

        return prompt
    

    
class AnswerTemplateProcessor:
    PROMPT_PATH = Path(__file__).parent / "prompts" / "answer.md"
    


    def __init__(self):
        self._lock = threading.Lock()
        self._template_cache: Optional[str] = None # 템플릿 내용을 캐시할 변수
        self.IS_PROMPT_MODIFICATION_MODE = os.getenv('IS_PROMPT_MODIFICATION_MODE') == "True"



    def _load_template(self) -> str:
        with self._lock:
            if self._template_cache is None or self.IS_PROMPT_MODIFICATION_MODE:
                if not os.path.exists(self.PROMPT_PATH):
                    raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {self.PROMPT_PATH}")

                with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
                    self._template_cache = f.read()
                
        return self._template_cache

    def get_final_prompt(self, specification, qna_contents) -> str:
        template = self._load_template()        

        # qna_str = ""
        # i = 1
        # for item in qna:
        #     qna_str = f"q{i}: {item[0]}\na{i}: {item[1]}\n\n"
        #     i += 1

        prompt = template.format(specification=specification, qna_contents = qna_contents)

        return prompt
    


class PromptDeviderProcessor:
    PROMPT_PATH = Path(__file__).parent / "prompts" / "devide.md"
    


    def __init__(self):
        self._lock = threading.Lock()
        self._template_cache: Optional[str] = None # 템플릿 내용을 캐시할 변수
        self.IS_PROMPT_MODIFICATION_MODE = os.getenv('IS_PROMPT_MODIFICATION_MODE') == "True"



    def _load_template(self) -> str:
        with self._lock:
            if self._template_cache is None or self.IS_PROMPT_MODIFICATION_MODE:
                if not os.path.exists(self.PROMPT_PATH):
                    raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {self.PROMPT_PATH}")

                with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
                    self._template_cache = f.read()
                
        return self._template_cache

    def get_final_prompt(self, prompt) -> str:
        template = self._load_template()        

        # qna_str = ""
        # i = 1
        # for item in qna:
        #     qna_str = f"q{i}: {item[0]}\na{i}: {item[1]}\n\n"
        #     i += 1

        prompt = template.format(user_prompt=prompt)

        return prompt
        
    

# 클라이언트에서 전송되는 오류 데이터 구조
class ClientError(BaseModel):
    # 필수 필드
    type: str # 'js-error', 'unhandledrejection', 'console-error' 등
    message: str 
    time: str
    game_version: str
    
    # 선택적 필드 (오류 타입에 따라 다름)
    source: Optional[str] = None
    lineno: Optional[int] = None
    colno: Optional[int] = None
    stack: Optional[str] = None
    detail: Optional[Any] = None # console.error 호출 시 첫 번째 인수가 들어갈 수 있음