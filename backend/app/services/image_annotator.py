import cv2
import os


class ImageAnnotator:

    def draw(self, image_path, detections, output_path):

        print(f"[Annotator] Reading image: {image_path}")

        image = cv2.imread(image_path)

        if image is None:
            raise Exception(f"Cannot read image: {image_path}")

        # إنشاء مجلد الحفظ إذا لم يكن موجودًا
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        for det in detections:

            if "bbox" not in det:
                continue

            x1, y1, x2, y2 = det["bbox"]

            label = f'{det["class"]} {det["confidence"]:.2f}'

            name = det["class"].lower()

            if "no-" in name:
                color = (0, 0, 255)

            elif name in ["hardhat", "safety vest", "mask"]:
                color = (0, 180, 0)

            elif name in ["machinery", "vehicle"]:
                color = (0, 165, 255)

            else:
                color = (255, 0, 0)

            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                image,
                label,
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )

        success = cv2.imwrite(output_path, image)

        print(f"[Annotator] Saving to: {output_path}")
        print(f"[Annotator] Save success: {success}")

        if not success:
            raise Exception(f"Failed to save image to {output_path}")

        return output_path