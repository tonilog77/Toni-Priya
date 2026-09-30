from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from app.models import PromptRequest
from app.services.gemini_flash import generate_outline
from app.utils.gemini_errors import (
    is_gemini_quota_error,
    get_gemini_error_message,
)

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# ============================================================
# HOME PAGE
# ============================================================

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


# ============================================================
# GENERATE COMIC
# ============================================================

@router.post("/generate")
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form("light-hearted"),
    art_style: str = Form("comic book"),
):

    try:
        print("\n========================================")
        print("ComicCraft: Starting comic generation")
        print("========================================")

        # Create PromptRequest from the HTML form
        request_data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        print("Story prompt:", story_prompt)
        print("Character:", character_name)
        print("Setting:", setting)
        print("Tone:", tone)
        print("Art style:", art_style)

        # ----------------------------------------------------
        # Generate comic outline using Gemini
        # ----------------------------------------------------

        print("\nCalling Gemini API...")

        outline = generate_outline(request_data)

        print("Gemini outline generated successfully.")
        print("Number of panels:", len(outline))

        # ----------------------------------------------------
        # Show comic preview
        # ----------------------------------------------------

        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "outline": outline,
                "prompt": request_data,
            }
        )

    except Exception as exc:

        # ----------------------------------------------------
        # Print complete error in terminal
        # ----------------------------------------------------

        print("\n")
        print("========================================")
        print("COMICCRAFT ERROR")
        print("========================================")
        print("Error type:", type(exc).__name__)
        print("Error message:", str(exc))
        print("Full error:", repr(exc))
        print("========================================")
        print("\n")

        # Convert technical Gemini error into friendly message
        error_message = get_gemini_error_message(exc)

        # ----------------------------------------------------
        # Detect Gemini quota error
        # ----------------------------------------------------

        if is_gemini_quota_error(exc):
            status_code = 429
        else:
            status_code = 500

        # ----------------------------------------------------
        # Show friendly error page
        # ----------------------------------------------------

        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": error_message,
            },
            status_code=status_code,
        )


# ============================================================
# JSON API
# ============================================================

@router.post("/generate-comic/json")
async def generate_comic_json(
    data: PromptRequest,
):

    try:
        print("\n========================================")
        print("ComicCraft JSON generation")
        print("========================================")

        # Generate comic outline
        outline = generate_outline(data)

        print("Gemini outline generated successfully.")

        return {
            "success": True,
            "outline": [
                panel.model_dump()
                for panel in outline
            ],
        }

    except Exception as exc:

        # Print error to terminal
        print("\n")
        print("========================================")
        print("COMICCRAFT JSON ERROR")
        print("========================================")
        print("Error type:", type(exc).__name__)
        print("Error message:", str(exc))
        print("Full error:", repr(exc))
        print("========================================")
        print("\n")

        # Friendly error message
        error_message = get_gemini_error_message(exc)

        # Status code
        if is_gemini_quota_error(exc):
            status_code = 429
        else:
            status_code = 500

        return {
            "success": False,
            "error": error_message,
            "status_code": status_code,
        }