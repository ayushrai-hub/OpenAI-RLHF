import os
import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict
from pathlib import Path

class LicensePlateDetector:
    def __init__(self, cascade_path: str = "haarcascade_russian_plate_number.xml") -> None:
        self.plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)

    def detect_plates(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = self.plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return plates

class LicensePlateProcessor:
    def __init__(self, output_dir: str = "captured_plates", min_confidence: float = 0.5) -> None:
        self.output_dir = output_dir
        self.min_confidence = min_confidence
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def preprocess_plate(self, plate_img: np.ndarray) -> Optional[np.ndarray]:
        if plate_img is None or plate_img.size == 0:
            return None
        return cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

    def save_plate(self, plate_img: np.ndarray, object_id: str) -> Optional[str]:
        if plate_img is None:
            return None
        filename = os.path.join(self.output_dir, f"plate_{object_id}.jpg")
        cv2.imwrite(filename, plate_img)
        return filename

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        detected_plates = []
        plates = LicensePlateDetector().detect_plates(frame)

        for i, (x, y, w, h) in enumerate(plates):
            plate_img = frame[y:y+h, x:x+w]
            processed_plate = self.preprocess_plate(plate_img)
            saved_path = self.save_plate(processed_plate, str(i))

            detected_plates.append({
                "object_id": str(i),
                "bounding_box": (x, y, w, h),
                "saved_path": saved_path
            })

        return frame, detected_plates

def main() -> None:
    cap = cv2.VideoCapture(0)
    processor = LicensePlateProcessor()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, detected_plates = processor.process_frame(frame)

        for plate in detected_plates:
            x, y, w, h = plate["bounding_box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("License Plate Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
