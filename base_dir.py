from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent

def BASE_PUBLIC_DIR():
    is_docker = os.getenv('RUNNING_IN_DOCKER', 'False') == 'True'
    if is_docker:
        return Path("/app/public")
    else:
        #return Path("../VerySimpleTypeScriptProject_AtoZ_Game/public")
        return PROJECT_ROOT.parent / "VerySimpleTypeScriptProject_AtoZ_Game" / "public"
    

    
def GAME_DIR(game_name:str):
    return BASE_PUBLIC_DIR() / game_name

def CODE_PATH(game_name:str):
    return BASE_PUBLIC_DIR() / game_name / "game.ts"

def DATA_PATH(game_name:str):
    return BASE_PUBLIC_DIR() / game_name / "data.json"

def SPEC_PATH(game_name:str):
    return BASE_PUBLIC_DIR() / game_name / "spec.md"

def CHAT_PATH(game_name:str):
    return BASE_PUBLIC_DIR() / game_name / "chat.json"

def ASSETS_PATH(game_name:str):
    return BASE_PUBLIC_DIR() / game_name / "assets"

def ARCHIVE_LOG_PATH(game_name:str):
     return BASE_PUBLIC_DIR() / game_name / "archive" / "change_log.json"