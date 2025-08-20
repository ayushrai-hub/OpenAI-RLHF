# ideal_completion.py
import cv2
from datetime import datetime, timezone
from pathlib import Path
import logging

MIN_CONFIDENCE_THRESHOLD = 0.6

class LicensePlateDetector:
    def __init__(self, cascade_path="haarcascade_russian_plate_number.xml"):
        """Initialize the license plate detector with Haar Cascade"""
        self.plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)
        if self.plate_cascade.empty():
            raise ValueError("Error loading cascade classifier")
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def detect_plates(self, frame):
        """Detect license plates in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = self.plate_cascade.detectMultiScale(gray, 1.1, 4)
        return plates

class LicensePlateProcessor:
    def __init__(self, output_dir="captured_plates", min_confidence=0.5):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.min_confidence = min_confidence
        self.detector = LicensePlateDetector()
        self.logger = logging.getLogger(__name__)

    def preprocess_plate(self, plate_img): 
        try:
            if plate_img is None:
                return None
            gray = cv2.cvtColor(plate_img, cv2.COLOR_RGB2GRAY)
            denoised = cv2.bilateralFilter(gray, 11, 17, 17)
            thresh = cv2.adaptiveThreshold(
                denoised, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            return processed
        except Exception as e:
            self.logger.error(f"Error preprocessing plate: {str(e)}")
            return None

    def save_plate(self, plate_img, object_id):  
        if plate_img is None:
            return None
            
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = f"plate_{object_id}_{timestamp}.png"
        filepath = self.output_dir / filename  
        try:
            cv2.imwrite(str(filepath), plate_img)
            self.logger.info(f"Saved license plate: {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Error saving plate: {str(e)}")
            return None

    def process_frame(self, frame):
        """Process a single frame for license plate detection"""
        if frame is None:
            return frame, []
            
        # Make a copy of the frame for drawing
        draw_frame = frame.copy()
        results = []
        
        try:
            # Detect license plates
            plates = self.detector.detect_plates(frame)
            
            for i, (x, y, w, h) in enumerate(plates):
                # Extract the plate region
                plate_img = frame[y:y+h, x:x+w]
                
                # Process the plate
                processed_plate = self.preprocess_plate(plate_img)
                if processed_plate is not None:
                    # Save the processed plate
                    plate_id = f"plate_{i}"
                    saved_path = self.save_plate(processed_plate, plate_id)
                    
                    if saved_path:
                        # Draw rectangle around plate
                        cv2.rectangle(draw_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        # Add text label
                        label = f"Plate {i+1}"
                        cv2.putText(draw_frame, label, (x, y-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        results.append({
                            'plate_id': plate_id,
                            'bbox': (x, y, w, h),
                            'image_path': saved_path
                        })
            
            return draw_frame, results
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            return frame, []

def main():
    # Initialize the processor
    processor = LicensePlateProcessor()
    
    # Open video capture (can be camera or video file)
    video_source = 0  
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        print("Error: Could not open video source")
        return
    
    try:
        while True:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame, results = processor.process_frame(frame)
            
            # Display results
            cv2.imshow('License Plate Detection', processed_frame)
            
            # Print detection results
            if results:
                print(f"Found {len(results)} license plates")
                for result in results:
                    print(f"Saved plate image: {result['image_path']}")
            
            # Break loop on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()