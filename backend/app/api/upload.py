from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil
import uuid

from app.config import UPLOAD_DIR

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    extension = Path(file.filename).suffix.lower()

    filename = f"{uuid.uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "filename": filename,
        "saved_to": str(file_path)
    }