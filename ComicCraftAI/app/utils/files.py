from pathlib import Path

from app.config import settings


def safe_export_path(filename: str) -> Path:
    name = Path(filename).name

    if name != filename:
        raise ValueError("Invalid export filename.")

    if not name.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are allowed.")

    base = settings.EXPORTS_DIR.resolve()
    path = (base / name).resolve()

    if path.parent != base:
        raise ValueError("Invalid export path.")

    return path
