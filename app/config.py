from pathlib import Path

class Settings:
    """Application settings and configuration"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    NEW_DATA_DIR = BASE_DIR / "new_data"
    NEW4_DATA_DIR = BASE_DIR / "new4_data"
    NEW_SHADE_DIR= BASE_DIR / "new_shade"
    MODEL_DIR = BASE_DIR / "model"
    MODEL_PATH = MODEL_DIR / "model.pth"
    PERFECT_SHADE_PATH = BASE_DIR / "app" / "shade" / "perfect_shades.json"
    CLEAN_SHADE_PATH = BASE_DIR / "app" / "shade" / "clean_shades.json"
    FINAL_SHADE_PATH = BASE_DIR / "app" / "shade" / "final_shades.json"
    # print(f"SHADE_PATH: {SHADE_PATH}")
    UPLOAD_DIR = BASE_DIR / "uploaded_images"
    RESULT_DIR = BASE_DIR / "result_images"

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.RESULT_DIR.mkdir(exist_ok=True)
