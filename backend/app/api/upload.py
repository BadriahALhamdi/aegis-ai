from fastapi import APIRouter, UploadFile, File
import shutil

from app.config import UPLOAD_DIR

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "filename": file.filename,
        "saved_to": str(file_path)
    }