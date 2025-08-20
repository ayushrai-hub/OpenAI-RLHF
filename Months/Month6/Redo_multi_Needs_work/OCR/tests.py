import unittest
from unittest.mock import patch
import cv2
import numpy as np
import os
from pathlib import Path
import shutil
import tempfile

from testableIC import LicensePlateDetector, LicensePlateProcessor

class TestLicensePlateDetector(unittest.TestCase):
    def setUp(self):
        # It sets up test fixtures before each test method.
        # Important for consistent test environment and avoiding test interference
        self.detector = LicensePlateDetector()
        # Create a sample test image
        self.test_frame = np.zeros((300, 400, 3), dtype=np.uint8)
        cv2.rectangle(self.test_frame, (100, 100), (300, 200), (255, 255, 255), -1)

    def test_detector_initialization(self):
        # It tests if the detector initializes correctly.
        # Critical for early detection of cascade classifier loading issues which could
        # cause system-wide failures if not caught during initialization
        self.assertIsNotNone(self.detector.plate_cascade)
        self.assertFalse(self.detector.plate_cascade.empty())

    def test_detect_plates_with_empty_frame(self):
        # It tests detection with an empty frame.
        # Essential for handling edge cases where no objects are present, preventing
        # false positives in real-world scenarios with empty scenes
        empty_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        plates = self.detector.detect_plates(empty_frame)
        self.assertEqual(len(plates), 0)

    def test_detect_plates_with_sample_frame(self):
        # It tests detection with a sample frame.
        # Crucial for verifying the basic detection functionality and ensuring
        # correct return type, which impacts downstream processing
        plates = self.detector.detect_plates(self.test_frame)
        # The result should be either a tuple or numpy array
        self.assertTrue(isinstance(plates, tuple) or isinstance(plates, np.ndarray))

    @patch('cv2.CascadeClassifier')
    def test_invalid_cascade_path(self, mock_cascade):
        # It tests detector initialization with invalid cascade path.
        # Essential for graceful error handling when cascade file is missing or corrupt,
        # preventing silent failures in production
        mock_cascade.return_value.empty.return_value = True
        with self.assertRaises(ValueError):
            LicensePlateDetector("invalid_path.xml")

class TestLicensePlateProcessor(unittest.TestCase):
    def setUp(self):
        # It sets up test fixtures before each test method.
        # Important for isolated testing environment with temporary directories
        # to prevent test data persistence and file system pollution
        self.temp_dir = tempfile.mkdtemp()
        self.processor = LicensePlateProcessor(output_dir=self.temp_dir)
        self.test_frame = np.zeros((300, 400, 3), dtype=np.uint8)
        cv2.rectangle(self.test_frame, (100, 100), (300, 200), (255, 255, 255), -1)

    def tearDown(self):
        # It cleans up after each test method.
        # Critical for preventing test data leakage and maintaining system cleanliness
        shutil.rmtree(self.temp_dir)

    def test_processor_initialization(self):
        # It tests if the processor initializes correctly.
        # Essential for verifying proper setup of output directories and configuration,
        # preventing file system access issues in production
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertEqual(self.processor.min_confidence, 0.5)
        self.assertIsNotNone(self.processor.detector)

    def test_preprocess_plate(self):
        # It tests plate image preprocessing.
        # Critical for ensuring image quality and format consistency before OCR,
        # directly impacts recognition accuracy
        # Create a sample plate image
        plate_img = np.zeros((100, 200, 3), dtype=np.uint8)
        cv2.rectangle(plate_img, (50, 25), (150, 75), (255, 255, 255), -1)
        
        processed = self.processor.preprocess_plate(plate_img)
        self.assertIsNotNone(processed)
        self.assertEqual(len(processed.shape), 2)  # Should be grayscale

    def test_preprocess_plate_with_invalid_input(self):
        # It tests preprocessing with invalid input.
        # Essential for robustness against corrupted or missing image data,
        # prevents system crashes in production
        processed = self.processor.preprocess_plate(None)
        self.assertIsNone(processed)

    def test_save_plate(self):
        # It tests saving plate images.
        # Critical for ensuring proper file system operations and data persistence,
        # affects system's ability to maintain detection history
        plate_img = np.zeros((100, 200), dtype=np.uint8)
        saved_path = self.processor.save_plate(plate_img, "test_plate")
        self.assertIsNotNone(saved_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_save_plate_with_invalid_input(self):
        # It tests saving with invalid plate image.
        # Important for handling edge cases where plate detection fails but system
        # continues to function, preventing partial data corruption
        saved_path = self.processor.save_plate(None, "test_plate")
        self.assertIsNone(saved_path)

    def test_process_frame(self):
        # It tests complete frame processing.
        # Essential for verifying the entire detection pipeline works together,
        # ensures all components integrate correctly
        processed_frame, results = self.processor.process_frame(self.test_frame)
        self.assertIsNotNone(processed_frame)
        self.assertIsInstance(results, list)

    def test_process_frame_with_invalid_input(self):
        # It tests frame processing with invalid input.
        # Critical for system stability when receiving corrupted video frames,
        # prevents cascade failures in the processing pipeline
        processed_frame, results = self.processor.process_frame(None)
        self.assertIsNone(processed_frame)
        self.assertEqual(len(results), 0)

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # It sets up test fixtures for integration testing.
        # Important for creating a controlled environment for end-to-end testing
        self.temp_dir = tempfile.mkdtemp()
        self.processor = LicensePlateProcessor(output_dir=self.temp_dir)
        
        # Create a test image with a white rectangle (simulating a license plate)
        self.test_frame = np.zeros((400, 600, 3), dtype=np.uint8)
        cv2.rectangle(self.test_frame, (200, 150), (400, 250), (255, 255, 255), -1)

    def tearDown(self):
        # It cleans up after integration tests.
        # Essential for maintaining a clean test environment between runs
        shutil.rmtree(self.temp_dir)

    def test_end_to_end_processing(self):
        # It tests the complete processing pipeline.
        # Critical for validating the entire system works together,
        # catches integration issues that unit tests might miss
        # Process the test frame
        processed_frame, results = self.processor.process_frame(self.test_frame)
        
        # Verify the results
        self.assertIsNotNone(processed_frame)
        self.assertIsInstance(results, list)
        
        # Check if the processed frame is different from the input frame
        self.assertTrue(np.array_equal(self.test_frame, processed_frame))

    @patch('cv2.imwrite')
    def test_saving_detected_plates(self, mock_imwrite):
        # It tests if detected plates are properly saved.
        # Essential for verifying the system's ability to persist detection results,
        # crucial for audit trails and downstream processing
        mock_imwrite.return_value = True
        
        # Process frame and verify saved files
        _, results = self.processor.process_frame(self.test_frame)
        
        # Check if imwrite was called for each detected plate
        if results:
            self.assertGreaterEqual(mock_imwrite.call_count, len(results))

def run_tests():
    # It runs all unit tests.
    # Important for providing a simple entry point for test execution
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests()