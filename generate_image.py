import urllib.parse
import urllib.request
import time
from io import BytesIO
from PIL import Image
from rembg import remove
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import random # 예시를 위한 임시 모듈


from base_dir import BASE_PUBLIC_DIR, GAME_DIR, CODE_PATH, DATA_PATH, SPEC_PATH, CHAT_PATH, ASSETS_PATH, ARCHIVE_LOG_PATH

def pil_image_to_bytes(pil_img: Image.Image, format="PNG") -> bytes:
    buffered = BytesIO()
    pil_img.save(buffered, format=format) 
    return buffered.getvalue()

def remove_background(image_data: bytes) -> bytes:
    """
    이미지의 배경을 제거합니다.
    
    Args:
        image_data: 원본 이미지 바이트 데이터
        
    Returns:
        배경이 제거된 이미지 바이트 데이터 (PNG 형식, 투명 배경)
    """
    print(f"\n========== [배경 제거 시작] ==========")
    
    try:
        # 바이트 데이터를 PIL Image로 변환
        input_image = Image.open(BytesIO(image_data))
        print(f"1. 원본 이미지 로드 완료: {input_image.size}")
        
        # rembg로 배경 제거
        print(f"2. 배경 제거 처리 중...")
        output_image = remove(input_image)
        
        # PIL Image를 바이트로 변환 (PNG 형식으로 저장하여 투명도 유지)
        result_bytes = pil_image_to_bytes(output_image, format="PNG")
        
        print(f"3. ✅ 배경 제거 완료!")
        print("========== [작업 완료] ==========\n")
        
        return result_bytes
        
    except Exception as e:
        print(f"\n❌ [배경 제거 오류]: {e}")
        return None

def remove_background_from_file(input_path: str, output_path: str) -> bool:
    """
    파일에서 이미지를 읽어 배경을 제거하고 저장합니다.
    
    Args:
        input_path: 입력 이미지 파일 경로
        output_path: 출력 이미지 파일 경로 (PNG 권장)
        
    Returns:
        성공 여부
    """
    try:
        # 파일 읽기
        with open(input_path, 'rb') as f:
            image_data = f.read()
        
        # 배경 제거
        result = remove_background(image_data)
        
        if result:
            # 결과 저장
            with open(output_path, 'wb') as f:
                f.write(result)
            print(f"💾 저장 완료: {output_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"\n❌ [파일 처리 오류]: {e}")
        return False

def generate_image(game_name, file_name, description, isBackgroundImage, width, height):
    file_path = ASSETS_PATH(game_name) / file_name

    result_image = generate_image_Pollinations_AI(description, width, height)

    if not isBackgroundImage:
        nobg_data = remove_background(result_image)
    else:
        nobg_data = result_image

    if nobg_data:        
        with open(file_path, 'wb') as f:
            f.write(nobg_data)
    else:
        print("⚠️ 배경 제거 실패")


def generate_image_Pollinations_AI(
    user_prompt: str,
    target_width: int, 
    target_height: int,
    seed = 777
) -> bytes:
    print(f"\n========== [이미지 생성 시작 (고속 안정성 모드)] ==========")
    print(f"1. 사용자 요청: {user_prompt}")
    
    try:
        # analyze_prompt = f"""
        # You are an expert prompt engineer. 
        # User request: "{editing_prompt}"
        # Based on the attached image and user's request, write a detailed English prompt for image generation.
        # Keep it concise (under 500 characters) to ensure stable generation.
        # Focus on style, colors, and key visual elements.
        # Output ONLY the prompt text.
        # """
        
        # 2. 무료 이미지 생성 (Pollinations AI)
        print(f"\n3. [Pollinations AI] 이미지 생성 요청 중...")        
        encoded_prompt = urllib.parse.quote(user_prompt, safe='')
                
        # 최대 4번 재시도
        for attempt in range(1, 5):
            try:
                prompt = "2d pixel art of Lumo the purple space mole holding a crystal, 16-bit SNES style, small sprite, game asset"
               
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width={target_width}&height={target_height}&model=flux-anime&nologo=true"

                req = urllib.request.Request(
                    image_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                # 🔥 [핵심] 타임아웃을 5분(300초)으로 설정하여 웬만해선 끊기지 않게 함
                with urllib.request.urlopen(req, timeout=300) as response:
                    image_data = response.read()
                
                if image_data:
                    print(f"   ✅ [Pollinations AI] 이미지 생성 성공! (시도 {attempt}회차)")
                    print("========== [작업 완료] ==========\n")
                    return image_data
            
            except Exception as e:
                print(f"   ⚠️ 시도 {attempt} 실패: {e}")
                if attempt < 4:
                    wait_time = attempt * 2 # 2초, 4초, 6초... 점진적 대기
                    print(f"   ⏳ {wait_time}초 후 다시 시도합니다...")
                    time.sleep(wait_time)
                else:
                    print("   ❌ 모든 시도 실패. (서버가 매우 혼잡합니다)")
                    return None

    except Exception as e:
        print(f"\n❌ [치명적 오류 발생]: {e}")
        return None
    

def run_image_generation_with_delay(game_name, asset_list, delay):
    # 사용할 최대 스레드 개수를 설정합니다. 일반적으로 CPU 코어 수의 몇 배를 사용합니다.
    # 여기서는 예를 들어 5개의 스레드를 사용하도록 설정합니다.
    MAX_WORKERS = 5
    futures = []

    # ThreadPoolExecutor를 'with' 문으로 사용하면 작업 완료 후 자동으로 정리됩니다.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        print("--- 이미지 생성 작업 제출 시작 ---")
        
        # 이미지 목록을 순회하며 작업을 executor에 제출합니다.
        for i, img in enumerate(asset_list):
            if i > 0:
                # 첫 번째 작업 이후부터 delay를 적용합니다.
                print(f"다음 작업 제출까지 {delay}초 대기...")
                time.sleep(delay)
            
            print(f"작업 {i+1} ({img['file_name']}) 제출...")
            
            # submit() 함수를 사용하여 generate_image 함수를 스레드 풀에 제출합니다.
            future = executor.submit(
                generate_image,
                game_name=game_name,
                file_name=img['file_name'],
                description=img['description'],
                isBackgroundImage=img['isBackgroundImage'],
                width=img['width'],
                height=img['height']
            )
            futures.append(future)

        print("\n--- 모든 작업이 스레드 풀에 제출되었습니다. 완료 대기 중... ---")
        
        # as_completed를 사용하여 완료되는 순서대로 결과를 처리하고, 모든 작업이 끝날 때까지 기다립니다.
        for future in as_completed(futures):
            try:
                result = future.result()  # 작업이 완료될 때까지 블록킹
                print(f"메인 스레드에서 결과 수신: {result}")
            except Exception as exc:
                print(f"작업 중 예외 발생: {exc}")

    print("\n--- 모든 이미지 생성 작업 완료! ---")
