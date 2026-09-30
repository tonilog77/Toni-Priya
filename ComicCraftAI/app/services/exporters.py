from pathlib import Path
import re

from fpdf import FPDF

from app.config import settings


def _pdf_text(value: str) -> str:
    # Built-in Helvetica in fpdf2 does not support all Unicode characters.
    replacements = {
        "—": "-",
        "–": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "…": "...",
        "•": "-",
        "🎨": "",
        "🦊": "",
    }

    text = str(value)
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "replace").decode("latin-1")


def _local_image(image_url: str) -> Path:
    if image_url.startswith("/static/"):
        return settings.BASE_DIR / image_url.lstrip("/")

    return Path(image_url)


def save_pdf(layout, title="ComicCraft"):
    safe_title = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        title,
    ).strip("_") or "ComicCraft"

    filename = f"{safe_title}_comic.pdf"
    output = settings.EXPORTS_DIR / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(
            0,
            10,
            _pdf_text(
                f"Panel {panel['panel_number']}: {panel['title']}"
            ),
            ln=True,
        )

        image_path = _local_image(panel["image_url"])

        if image_path.exists():
            try:
                pdf.image(
                    str(image_path),
                    x=15,
                    y=28,
                    w=180,
                )
                pdf.ln(125)
            except Exception:
                pdf.ln(5)

        pdf.set_font("Helvetica", "", 11)

        for label in ("scene_description", "caption", "narration"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.write(6, _pdf_text(label.replace("_", " ").title() + ": "))
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(
                0,
                6,
                _pdf_text(panel[label]),
            )
            pdf.ln(2)

        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(
            0,
            8,
            _pdf_text(panel["dialogue"]),
        )

    pdf.output(str(output))
    return filename
