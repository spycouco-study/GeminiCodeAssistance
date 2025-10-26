# --- 1. 필수 라이브러리 설치 확인 및 자동 설치 ---
def install_packages(package_list):
    import subprocess, sys    
    for package in package_list:
        try:
            # 패키지가 이미 설치되었는지 확인합니다.
            __import__(package)
            print(f"✅ '{package}'가 이미 설치되어 있습니다.")
        except ImportError as e:
            print(f"📦 '{package}'가 설치되어 있지 않습니다. 설치를 시작합니다...")
            # 'pip install' 명령어를 실행합니다.
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ '{package}' 설치 완료.")


# #############################################################################################################
# #                                              필요 패키지 설치                                              #
# #############################################################################################################
# import sys, os, pathlib
# sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent)) # install_packages.py의 경로 추가
# #sys.path.append(str(pathlib.Path(os.getcwd())))
# from install_packages import install_packages
# install_packages(["openai", "dotenv"]) # 설치가 필요한 패키지 리스트
# #############################################################################################################



#############################################################################################################
#                                              필요 패키지 설치                                              #
#############################################################################################################
import sys, os, pathlib
#sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent)) # install_packages.py의 경로 추가
sys.path.append(str(pathlib.Path(os.getcwd()))) # install_packages.py의 경로 추가
# from tools.install_packages import install_packages
install_packages(["google.genai", "dotenv", "keyboard", "fastapi", "uvicorn"]) # 설치가 필요한 패키지 리스트
#############################################################################################################