COMICCRAFTAI - SIMPLE SETUP

1. Open this folder in VS Code.

2. Create/activate the virtual environment:
   python -m venv .venv

3. Activate it in PowerShell:
   .\.venv\Scripts\Activate.ps1

4. Install packages:
   python -m pip install -r requirements.txt

5. Open .env and add:
   GEMINI_API_KEY=YOUR_REAL_GEMINI_KEY

   For real generated images, also add:
   HF_TOKEN=YOUR_REAL_HUGGINGFACE_TOKEN

6. Test the project:
   python -c "from app.main import app; print('ComicCraft OK')"

7. Start:
   python -m uvicorn app.main:app --reload

8. Open:
   http://127.0.0.1:8000

IMPORTANT:
- Do NOT run app/routes.py directly.
- Do NOT run app/ai/gemini_flash.py directly.
- Run the application only through:
  python -m uvicorn app.main:app --reload

If HF_TOKEN is empty, the project still creates a local placeholder image
so the preview page can be tested. For real AI images, configure HF_TOKEN.
