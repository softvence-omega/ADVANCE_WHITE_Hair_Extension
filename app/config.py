from pathlib import Path
from dotenv import load_dotenv
import os
from dataclasses import dataclass, field

load_dotenv()  # Load env vars from .env if any

@dataclass
class Settings:
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    DATA_DIR: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", Path(__file__).resolve().parent.parent / "data")).resolve())
    OUTPUT_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    TEMP_DIR: Path = field(init=False)
    SHADE_JSON: Path = field(init=False)

    ENV: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    DEBUG: bool = field(default_factory=lambda: os.getenv("DEBUG", "true").lower() == "true")

    def __post_init__(self):
        self.TEMP_DIR = self.OUTPUT_DIR / "upload"
        self.SHADE_JSON = self.OUTPUT_DIR / "shade"

        # Create directories if they don't exist
        for directory in [self.DATA_DIR, self.OUTPUT_DIR, self.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# Instantiate settings
settings = Settings()

# Debug prints (comment out or remove in production)
print(f"BASE_DIR: {settings.BASE_DIR}")
print(f"DATA_DIR: {settings.DATA_DIR}")
print(f"OUTPUT_DIR: {settings.OUTPUT_DIR}")
print(f"TEMP_DIR: {settings.TEMP_DIR}")
print(f"SHADE_JSON: {settings.SHADE_JSON}")
print(f"ENV: {settings.ENV}")
print(f"DEBUG: {settings.DEBUG}")
