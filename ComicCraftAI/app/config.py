from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_NAME = os.getenv("APP_NAME", "ComicCraftAI").strip()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()

    HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
    HF_IMAGE_MODEL = os.getenv(
        "HF_IMAGE_MODEL",
        "black-forest-labs/FLUX.1-schnell",
    ).strip()

    PANEL_COUNT = max(1, min(int(os.getenv("PANELS", "5")), 10))

    BASE_DIR = BASE_DIR
    STATIC_DIR = BASE_DIR / "static"
    PANELS_DIR = STATIC_DIR / "panels"
    EXPORTS_DIR = STATIC_DIR / "exports"
    TEMPLATES_DIR = BASE_DIR / "templates"

    def ensure_dirs(self):
        self.STATIC_DIR.mkdir(parents=True, exist_ok=True)
        self.PANELS_DIR.mkdir(parents=True, exist_ok=True)
        self.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
