import json
import time
import requests

from app.config import settings
from app.models import PanelOutline, PromptRequest


def _call_gemini(prompt: str, schema: dict) -> str:
    """
    Call the Gemini API and handle common API errors,
    including 429 quota errors.
    """

    # Check API key
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing in .env. "
            "Add your Google Gemini API key and restart the server."
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{settings.GEMINI_MODEL}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": settings.GEMINI_API_KEY,
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
    }

    # Retry only temporary 503 errors.
    # We intentionally DO NOT retry 429 quota errors.
    for attempt in range(3):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Could not connect to Gemini API: {exc}"
            ) from exc

        # Temporary Gemini server error.
        if response.status_code == 503 and attempt < 2:
            time.sleep(2 ** attempt)
            continue

        break

    # ---------------------------------------------------------
    # GEMINI QUOTA / RATE LIMIT ERROR
    # ---------------------------------------------------------
    if response.status_code == 429:
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise RuntimeError(
            "GEMINI_QUOTA_EXCEEDED: "
            f"Gemini API quota has been exceeded. "
            f"Please wait until your Gemini quota resets "
            f"and try again. Details: {detail}"
        )

    # ---------------------------------------------------------
    # API KEY / AUTHENTICATION ERROR
    # ---------------------------------------------------------
    if response.status_code in (401, 403):
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise RuntimeError(
            "GEMINI_AUTH_ERROR: "
            "Gemini API authentication failed. "
            "Please check your GEMINI_API_KEY and Google AI project. "
            f"Details: {detail}"
        )

    # ---------------------------------------------------------
    # MODEL NOT FOUND
    # ---------------------------------------------------------
    if response.status_code == 404:
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise RuntimeError(
            "GEMINI_MODEL_NOT_FOUND: "
            f"The Gemini model '{settings.GEMINI_MODEL}' "
            "could not be found or is not available. "
            f"Details: {detail}"
        )

    # ---------------------------------------------------------
    # OTHER GEMINI API ERRORS
    # ---------------------------------------------------------
    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"Gemini API error {response.status_code}: {detail}"
        )

    # ---------------------------------------------------------
    # READ GEMINI RESPONSE
    # ---------------------------------------------------------
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]

    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Gemini returned an unexpected response: {data}"
        ) from exc


def generate_outline(request_data: PromptRequest):
    """
    Generate the comic panel outline using Gemini.
    """

    count = settings.PANEL_COUNT

    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "panel_number": {
                    "type": "INTEGER"
                },
                "title": {
                    "type": "STRING"
                },
                "scene_description": {
                    "type": "STRING"
                },
                "image_prompt": {
                    "type": "STRING"
                },
            },
            "required": [
                "panel_number",
                "title",
                "scene_description",
                "image_prompt",
            ],
        },
    }

    prompt = f"""
Create a {count}-panel comic outline.

Story prompt: {request_data.story_prompt}
Main character: {request_data.character_name}
Setting: {request_data.setting}
Tone: {request_data.tone}
Art style: {request_data.art_style}

Rules:
- Return exactly {count} panels.
- panel_number must be 1 through {count}.
- Keep the same main character throughout.
- Make each image_prompt detailed and visual.
- Do not include markdown.
"""

    raw = _call_gemini(prompt, schema)

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON. "
            "Please try generating the comic again."
        ) from exc

    if not isinstance(items, list) or len(items) != count:
        raise RuntimeError(
            f"Gemini returned "
            f"{len(items) if isinstance(items, list) else 0} panels; "
            f"expected {count}."
        )

    return [
        PanelOutline(**item)
        for item in items
    ]