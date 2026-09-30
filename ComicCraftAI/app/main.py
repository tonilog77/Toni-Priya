from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router

app = FastAPI(title=settings.APP_NAME)

app.mount(
    "/static",
    StaticFiles(directory=str(settings.STATIC_DIR)),
    name="static",
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
