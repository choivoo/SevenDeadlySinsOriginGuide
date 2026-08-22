from pathlib import Path
import sys

APP_NAME = "일곱 개의 대죄 Origin 완전 공략"
APP_VERSION = "1.2.0"
DATA_VERSION = "1.8"
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
USER_DIR = Path.home() / "7DSOriginCompleteGuide"
USER_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = USER_DIR / "game.db"
SOURCES = {
    "official": "https://7origin.netmarble.com/",
    "community_db": "https://7dsorigin.app/en",
}
