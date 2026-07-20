from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.upload import router as upload_router
from app.api.analyze import router as analyze_router
from app.config import RESULTS_DIR, UPLOAD_DIR

app = FastAPI(
    title="Aegis AI",
    version="1.0.0",
    description="Hazard Intelligence Engine"
)

# API Routes
app.include_router(upload_router)
app.include_router(analyze_router)

# Static folders
app.mount(
    "/results",
    StaticFiles(directory=str(RESULTS_DIR)),
    name="results"
)

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads"
)

# Frontend folder (../frontend)
FRONTEND_DIR = (
    Path(__file__).resolve().parent.parent.parent / "frontend"
)

app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="frontend"
)


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }