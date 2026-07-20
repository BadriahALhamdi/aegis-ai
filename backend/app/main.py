from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.analyze import router as analyze_router

app = FastAPI(
    title="Aegis AI",
    version="1.0.0",
    description="Hazard Intelligence Engine"
)

app.include_router(upload_router)
app.include_router(analyze_router)


@app.get("/")
def home():
    return {
        "project": "Aegis AI",
        "status": "Running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }