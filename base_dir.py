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