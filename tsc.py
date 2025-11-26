import os
from pathlib import Path
import re
import subprocess
import json
import sys
from typing import Dict, Any, List

from base_dir import BASE_PUBLIC_DIR





# def check_typescript_file(config_path: Path, game_name: str) -> Dict[str, Any]:
#     """
#     루트에서 특정 게임의 game.ts만 타입 체크
#     """
#     project_root = os.path.dirname(config_path)
#     ts_file = f"public/{game_name}/game.ts"
    
#     # 디버깅 정보 출력
#     print(f"🔍 Debug Info:")
#     print(f"  config_path: {config_path}")
#     print(f"  project_root: {project_root}")
#     print(f"  ts_file: {ts_file}")
#     print(f"  cwd: {project_root}")
#     print(f"  tsconfig.json exists: {os.path.exists(os.path.join(project_root, 'tsconfig.json'))}")
    
#     result = subprocess.run(
#         ['npx', 'tsc', '--noEmit', ts_file],
#         capture_output=True,
#         text=True,
#         check=False,
#         shell=True,
#         cwd=project_root
#     )
    
#     return {
#         'success': result.returncode == 0,
#         'return_code': result.returncode,
#         'stdout': result.stdout,
#         'stderr': result.stderr
#     }


# #config_path = Path(r"c:\Users\spyco\Desktop\final_project\game3d_4\tsconfig.json")
# config_path = BASE_DIR / "tsconfig.json"
# result = check_typescript_file(config_path, "sample-3d-game")

# print(f"\n{'='*60}")
# print(f"✅ Success: {result['success']}")
# print(f"📊 Return Code: {result['return_code']}")

# if result['stdout']:
#     print(f"\n📝 STDOUT:\n{result['stdout']}")

# if result['stderr']:
#     print(f"\n❌ STDERR:\n{result['stderr']}")




def check_typescript_errors_with_options(ts_file_path: str) -> Dict[str, Any]:
    # # # 1. tsconfig.json 파일에서 컴파일러 옵션 로드 (이 부분은 동일)
    # try:
    #     with open(config_path, 'r', encoding='utf-8') as f:
    #         config_data = json.load(f)
    #         options = config_data.get('compilerOptions', {})
    # # ... (생략: FileNotFoundError 및 JSONDecodeError 처리)
    # except Exception as e:
    #     return {
    #         'success': False,
    #         'return_code': -1,
    #         'stdout': '',
    #         'stderr': f"Error: tsconfig file handling error: {e}"
    #     }

    # # 2. tsc 명령 인자 리스트 생성
    # command_args: List[str] = ['npx', 'tsc', '--noEmit']
    # #command_args: List[str] = ['npx', 'tsc']
        
    # # ✨✨✨ 핵심 수정 부분: 오류가 있어도 JS 파일 생성을 강제합니다.
    # # tsconfig.json의 noEmitOnError 설정을 덮어씁니다.
    # #command_args.extend(['--noEmitOnError', 'false'])
    



    # # 🌟 [수정된 부분]: lib 옵션 처리
    # lib_value = options.get('lib')
    # if lib_value:
    #     if isinstance(lib_value, list):
    #         # 배열인 경우, 콤마로 연결하여 하나의 인수로 전달합니다.
    #         command_args.extend(['--lib', ','.join(lib_value)])
    #     else:
    #         # 배열이 아닌 경우 (예: 문자열) 그대로 전달합니다.
    #         command_args.extend(['--lib', str(lib_value)])
            
    # # [이전과 동일]: target, module 등의 문자열 값 옵션
    # for key in ['target', 'module']: # lib는 위에서 처리했으므로 제외
    #     value = options.get(key)
    #     if value:
    #         command_args.extend([f'--{key}', str(value)])
            
    # # [이전과 동일]: strict, esModuleInterop 등의 부울 값 옵션
    # for key in ['strict', 'esModuleInterop', 'skipLibCheck']:
    #     value = options.get(key)
    #     if value is True:
    #         command_args.append(f'--{key}')
            



    # # 3. 마지막에 검사할 파일 경로 추가 (이 부분은 동일)
    # command_args.append(ts_file_path)

    # tsconfig.json 파일이 있는 디렉터리 경로를 추출합니다.
    #config_dir = os.path.dirname(config_path)

    config_dir = os.path.dirname(ts_file_path)



    






    # 4. 명령어 실행 (shell=True가 포함되어 있다고 가정)
    try:
        # #shell=True를 반드시 포함해야 npx 실행 오류가 발생하지 않습니다.
        # result = subprocess.run(
        #     command_args,
        #     capture_output=True,
        #     text=True,
        #     check=False,
        #     shell=True,
        #     cwd=config_dir
        # )

        project_file_name = 'tsconfig.json' 

        result = subprocess.run(
            ['npx', 'tsc', '--noEmit', '--project', project_file_name], 
            cwd=config_dir,
            capture_output=True,
            text=True,
            shell=True 
        )
        
        return {
            'success': result.returncode == 0,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    except Exception as e:
        # ... (생략: 예외 처리)
        return {
            'success': False,
            'return_code': -2,
            'stdout': '',
            'stderr': f"An unexpected error occurred during execution: {e}"
        }


def check_typescript_errors(ts_file_path):
    """
    tsc로 TypeScript 파일의 타입 오류 체크
    
    Args:
        ts_file_path: TypeScript 파일 경로
        
    Returns:
        dict: {'success': bool, 'errors': str}
    """
    try:
        # 절대 경로로 변환
        ts_file_path = os.path.abspath(ts_file_path)
        file_name = os.path.basename(ts_file_path)
        work_dir = os.path.dirname(os.path.dirname(os.path.dirname(ts_file_path)))
        
        # # tsc로 타입 체크 (빌드 없이 검증만)
        # result = subprocess.run(
        #     ['npx', 'tsc', file_name, '--noEmit', '--skipLibCheck', 
        #      '--target', 'ES2020', '--module', 'ES2020', 
        #      '--lib', 'ES2020,DOM', '--moduleResolution', 'bundler'],
        #     cwd=work_dir,
        #     capture_output=True,
        #     text=True,
        #     shell=True  # Windows에서 npx 실행을 위해 필요
        # )

        # tsc로 타입 체크 (빌드 없이 검증만)
        result = subprocess.run(
            ['npx', 'tsc', file_name, '--noEmit'],
            cwd=work_dir,
            capture_output=True,
            text=True,
            shell=True  # Windows에서 npx 실행을 위해 필요
        )
        
        if result.returncode == 0:
            return {'success': True, 'errors': None}
        else:
            return {'success': False, 'errors': result.stdout + result.stderr}
            
    except Exception as e:
        return {'success': False, 'errors': str(e)}



# 정규 표현식 패턴:
# (?:^|\n) : 줄의 시작(^) 또는 줄바꿈(\n)으로 시작
# (.*?\.ts) : .ts로 끝나는 문자열을 캡처 (이것이 파일 이름입니다)
# \( : 괄호 '(' 이스케이프
# (.*) : 나머지 오류 메시지 텍스트 캡처
# $ : 줄의 끝
pattern = re.compile(r'(?:^|\n)(.*?\.ts)(\(.*\n)')

def format_error_message(error_text: str) -> str:
    """오류 메시지에서 파일 경로를 제거하고 파일 이름부터 시작하도록 포맷합니다."""
    
    # 각 오류 줄을 찾아 패턴에 맞게 치환합니다.
    # group(1)이 파일 이름 (예: 'bubble game.ts')
    # group(2)가 나머지 오류 정보 (예: '(961,4): error TS2304: Cannot find name 'gg'.\n')
    
    # 🌟 re.sub를 사용하여 일치하는 모든 패턴을 치환합니다.
    # 경로는 제거하고 캡처 그룹 1(파일 이름)과 캡처 그룹 2(나머지 오류)만 사용합니다.
    formatted_text = re.sub(pattern, r'\n\1\2', error_text)
    
    # 시작 부분에 불필요한 공백/줄바꿈이 있다면 정리합니다.
    return formatted_text.lstrip()




def format_error_message_simplified(error_text: str, filename: str) -> str:
    """
    오류 메시지에서 파일 경로를 제거하고, 파일 이름부터 시작하도록 포맷합니다.
    
    Args:
        error_text: 원본 오류 메시지 (예: "../../경로/bubble game.ts(961,4): error...")
        filename: 오류가 발생한 파일 이름 (예: "bubble game.ts")
        
    Returns:
        파일 이름부터 시작하는 포맷된 메시지.
    """
    # 1. 메시지 시작과 끝의 공백을 제거합니다.
    error_text = error_text.strip()
    
    # 2. 파일 이름이 메시지에서 처음 나타나는 위치를 찾습니다.
    # filename 변수는 'bubble game.ts' 처럼 공백을 포함해도 됩니다.
    start_index = error_text.find(filename)
    
    if start_index != -1:
        # 3. 파일 이름이 시작하는 위치부터 끝까지 문자열을 잘라냅니다.
        # 즉, 파일 이름 앞의 모든 경로 문자열을 제거합니다.
        formatted_text = error_text[start_index:]
        return formatted_text
    else:
        # 파일 이름을 찾지 못했다면 원본 메시지를 반환합니다.
        return error_text



def build_with_esbuild(ts_file_path, output_path=None, format='esm', target='es2020', sourcemap='inline'):
    """
    esbuild로 TypeScript 파일 빌드
    
    Args:
        ts_file_path: TypeScript 파일 경로
        output_path: 출력 파일 경로 (None이면 .ts를 .js로 변경)
        format: 출력 포맷 ('esm', 'cjs', 'iife')
        target: 타겟 버전 ('es2020', 'es2015' 등)
        sourcemap: 소스맵 옵션 ('inline', 'external', None)
        
    Returns:
        dict: {'success': bool, 'output': str, 'error': str}
    """
    try:
        # 절대 경로로 변환
        ts_file_path = os.path.abspath(ts_file_path)
        file_name = os.path.basename(ts_file_path)
        work_dir = os.path.dirname(ts_file_path)
        
        # 출력 경로 설정
        if output_path is None:
            output_path = ts_file_path.replace('.ts', '.js')
        
        # esbuild 명령어 구성
        cmd = [
            'npx', 'esbuild', file_name,
            f'--outfile={os.path.basename(output_path)}',
            f'--format={format}',
            f'--target={target}'
        ]
        
        if sourcemap:
            cmd.append(f'--sourcemap={sourcemap}')
        
        # esbuild 실행
        result = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            shell=True  # Windows에서 npx 실행을 위해 필요
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'output': output_path,
                'message': result.stdout + result.stderr
            }
        else:
            return {
                'success': False,
                'output': None,
                'error': result.stdout + result.stderr
            }
            
    except Exception as e:
        return {'success': False, 'output': None, 'error': str(e)}




#CONFIG_FILE_NAME = "tsconfig.json"
#CONFIG_CODE_PATH = BASE_DIR / CONFIG_FILE_NAME


def check_typescript_compile_error(file_path:Path):
    print(f"📄 {file_path.name} 파일을 tsconfig.json 설정으로 검사 시작...")

    #analysis_result = check_typescript_errors(file_path)
    analysis_result = check_typescript_errors_with_options(file_path)
    build_with_esbuild(file_path)

    print("\n--- 검사 결과 ---")
    if not analysis_result['success']:
        print(f"🚨 파일 ({file_path.name}) 오류가 발견되었습니다.")
        error_message = analysis_result['stdout']
        parts = error_message.split('\n')

        formatted_messages = []

        # 오류 메시지 확인
        print("\n=== AI에게 전달할 오류 메시지 (stderr) ===")
        # 'parts'는 나눠진 오류 문자열들의 리스트라고 가정합니다.
        for p in parts:
            # 2. 함수를 호출하고 그 결과를 변수에 저장합니다.
            formatted_p = format_error_message_simplified(p, file_path.name)
            
            # 3. 리스트에 결과를 추가합니다.
            formatted_messages.append(formatted_p)    
            print(formatted_p)
            
        print("------------------------------------------")    

        multi_line_string = "\n".join(formatted_messages)
        return multi_line_string
    else:
        print(f"✅ 파일 game.ts에 오류가 없습니다.")
        # 정상적인 경우 출력은 보통 비어있습니다.
        # print(analysis_result['stdout'])
        return ""
    






# entries = os.listdir(BASE_PUBLIC_DIR)
#     # 2. 각 항목이 실제로 디렉터리(폴더)인지 확인합니다.
# for entry in entries:
#     # 항목의 전체 경로를 만듭니다.
#     full_path = os.path.join(BASE_PUBLIC_DIR, entry)
    
#     # 전체 경로가 디렉터리인지 확인합니다.
#     if os.path.isdir(full_path):
#         check_typescript_compile_error(Path(full_path) / "game.ts")



#check_typescript_compile_error(Path(BASE_PUBLIC_DIR) / "sy_vampire_survivors" / "game.ts")
#check_typescript_compile_error(Path(BASE_PUBLIC_DIR) / "sy_3d_dddd2" / "game.ts")
