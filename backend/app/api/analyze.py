from fastapi import APIRouter, Body, HTTPException

from pathlib import Path
import traceback

from app.config import RESULTS_DIR
from app.services.hazard_engine import HazardEngine
from app.services.yolo_detector import YOLODetector
from app.services.image_annotator import ImageAnnotator

router = APIRouter()

engine = HazardEngine()
detector = YOLODetector()
annotator = ImageAnnotator()


@router.post("/analyze")
def analyze(data: dict = Body(...)):

    image_path = data.get("image_path")

    if not image_path:
        raise HTTPException(
            status_code=400,
            detail="image_path is required."
        )

    try:

        # تشغيل نموذج YOLO
        detections = detector.detect(image_path)

        # استخراج اسم الملف فقط
        filename = Path(image_path).name

        # مسار الصورة الناتجة
        output_path = RESULTS_DIR / filename

        print(f"[Analyze] Output path: {output_path}")

        # رسم النتائج على الصورة
        annotator.draw(
            image_path,
            detections,
            str(output_path)
        )

        # تحليل المخاطر
        analysis = engine.analyze(detections)

        return {
            "success": True,
            "image": image_path,
            "annotated_image": str(output_path),
            "total_detections": len(detections),
            "detections": detections,
            "analysis": analysis
        }

    except Exception as e:

        print("\n========== ERROR ==========")
        traceback.print_exc()
        print("===========================\n")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )