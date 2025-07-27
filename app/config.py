from pathlib import Path

class Settings:
    """Application settings and configuration"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODEL_DIR = BASE_DIR / "model"
    MODEL_PATH = MODEL_DIR / "model.pth"
    SHADE_PATH = BASE_DIR / "app" / "shade" / "shade_rgb_signatures.json"
    print(f"SHADE_PATH: {SHADE_PATH}")
    UPLOAD_DIR = BASE_DIR / "uploaded_images"
    RESULT_DIR = BASE_DIR / "result_images"

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.RESULT_DIR.mkdir(exist_ok=True)
