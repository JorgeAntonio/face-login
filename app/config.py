from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
DATABASE_PATH = DATA_DIR / "app.db"
LEGACY_ROOT_FILES = {
    ".gitignore",
    "Login_Vision.py",
    "README.md",
    "requirements.txt",
}
CAMERA_INDEX = 0
CAPTURE_WINDOW_NAME = "Captura Facial"
PBKDF2_ITERATIONS = 120_000
FACE_MATCH_THRESHOLD = 0.65


def ensure_directories() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    FACES_DIR.mkdir(exist_ok=True)
