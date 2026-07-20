from huggingface_hub import hf_hub_download
from ultralytics import YOLO


class YOLODetector:

    DUPLICATE_DISTANCE = 40

    def __init__(self):

        print("Loading PPE detection model...")

        model_path = hf_hub_download(
            repo_id="Hansung-Cho/yolov8-ppe-detection",
            filename="best.pt"
        )

        self.model = YOLO(model_path)

        print("PPE model loaded successfully.")

    def _distance(self, p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    def _remove_duplicates(self, detections):

        detections = sorted(
            detections,
            key=lambda d: d["confidence"],
            reverse=True
        )

        filtered = []

        for det in detections:

            duplicate = False

            for kept in filtered:

                if (
                    det["class"].lower() == kept["class"].lower()
                    and self._distance(
                        det["center"],
                        kept["center"]
                    ) < self.DUPLICATE_DISTANCE
                ):
                    duplicate = True
                    break

            if not duplicate:
                filtered.append(det)

        return filtered

    def detect(self, image_path):

        results = self.model(image_path)

        detections = []

        for result in results:

            for box in result.boxes:

                cls = int(box.cls[0])

                conf = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                detections.append({
                    "class": self.model.names[cls],
                    "confidence": round(conf, 3),
                    "bbox": [
                        round(x1),
                        round(y1),
                        round(x2),
                        round(y2)
                    ],
                    "center": [
                        round(center_x),
                        round(center_y)
                    ]
                })

        detections = self._remove_duplicates(detections)

        return detections