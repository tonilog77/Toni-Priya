from pathlib import Path
import io
import time

import requests
from PIL import Image, ImageDraw, ImageFont

from app.config import settings


def _placeholder(prompt: str, panel_number: int) -> str:
    """
    Creates a local comic-style placeholder when HF_TOKEN is not configured.
    This keeps the application usable while the image API is being configured.
    """
    width, height = 1000, 700
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Try a standard Windows font; fall back to Pillow's default.
    try:
        font_big = ImageFont.truetype(
            "C:/Windows/Fonts/arialbd.ttf",
            42,
        )
        font_small = ImageFont.truetype(
            "C:/Windows/Fonts/arial.ttf",
            24,
        )
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.rectangle(
        (20, 20, width - 20, height - 20),
        outline="black",
        width=8,
    )
    draw.text(
        (50, 50),
        f"ComicCraftAI - Panel {panel_number}",
        fill="black",
        font=font_big,
    )

    text = prompt[:500]
    draw.multiline_text(
        (60, 140),
        text,
        fill="black",
        font=font_small,
        spacing=10,
    )

    filename = f"panel_{panel_number}_{int(time.time() * 1000)}.png"
    output = settings.PANELS_DIR / filename
    image.save(output, "PNG")

    return f"/static/panels/{filename}"


def generate_image(prompt: str, panel_number: int) -> str:
    """
    Generate a real image with Hugging Face when HF_TOKEN is configured.
    Otherwise create a local placeholder image instead of crashing.
    """
    if not settings.HF_TOKEN:
        return _placeholder(prompt, panel_number)

    url = (
        "https://router.huggingface.co/hf-inference/models/"
        f"{settings.HF_IMAGE_MODEL}"
    )

    headers = {
        "Authorization": f"Bearer {settings.HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {"inputs": prompt}

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=180,
        )

        if not response.ok:
            raise RuntimeError(
                f"Hugging Face image API error "
                f"{response.status_code}: {response.text}"
            )

        image = Image.open(io.BytesIO(response.content)).convert("RGB")

        filename = f"panel_{panel_number}_{int(time.time() * 1000)}.png"
        output = settings.PANELS_DIR / filename
        image.save(output, "PNG")

        return f"/static/panels/{filename}"

    except Exception as exc:
        # The story should still be visible if the image provider fails.
        print(f"[Image generator] {exc}")
        return _placeholder(prompt, panel_number)
