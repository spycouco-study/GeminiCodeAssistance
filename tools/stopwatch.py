import time

# 여러 스톱워치를 저장할 딕셔너리
stopwatches = {}

def start_stopwatch(name: str):
    """지정한 이름으로 스톱워치 시작"""
    stopwatches[name] = time.perf_counter()
    print("\n================================================")
    print(f"<{name} 스톱워치 시작>")
    print("================================================\n")

def end_stopwatch(name: str):
    """지정한 이름의 스톱워치 종료 및 경과 시간 출력"""
    if name not in stopwatches:
        print(f"[{name}] 스톱워치가 시작되지 않았습니다.")
        return
    
    end_time = time.perf_counter()
    elapsed_time = end_time - stopwatches[name]
    print("\n================================================")
    print(f"<{name} 소요 시간: {elapsed_time:.2f}초>")
    print("================================================\n")
    
    # 사용 끝났으면 딕셔너리에서 제거
    del stopwatches[name]

    return elapsed_time