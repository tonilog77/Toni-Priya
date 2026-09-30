import json

from app.ai.gemini_flash import _call_gemini
from app.config import settings
from app.models import PanelOutline, PromptRequest, StoryPanel


def generate_story(
    request_data: PromptRequest,
    outline: list[PanelOutline],
):
    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "panel_number": {"type": "INTEGER"},
                "title": {"type": "STRING"},
                "scene_description": {"type": "STRING"},
                "caption": {"type": "STRING"},
                "narration": {"type": "STRING"},
                "dialogue": {"type": "STRING"},
                "image_prompt": {"type": "STRING"},
            },
            "required": [
                "panel_number",
                "title",
                "scene_description",
                "caption",
                "narration",
                "dialogue",
                "image_prompt",
            ],
        },
    }

    outline_text = json.dumps(
        [item.model_dump() for item in outline],
        ensure_ascii=False,
    )

    prompt = f"""
Turn this comic outline into the final story panels.

Character: {request_data.character_name}
Setting: {request_data.setting}
Tone: {request_data.tone}
Art style: {request_data.art_style}
Original story: {request_data.story_prompt}

Outline:
{outline_text}

Rules:
- Return exactly {settings.PANEL_COUNT} panels.
- Keep character appearance and identity consistent.
- Make dialogue short and natural.
- Make image_prompt suitable for an image generation model.
- Do not include markdown.
"""

    raw = _call_gemini(prompt, schema)
    items = json.loads(raw)

    if not isinstance(items, list):
        raise RuntimeError("Gemini story response was not a list.")

    return [StoryPanel(**item) for item in items]
