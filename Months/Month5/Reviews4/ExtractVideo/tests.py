import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import cv2
from ideal_completion import capture_frames_at_0_25  

class TestCaptureFrames(unittest.TestCase):


    @patch('os.makedirs')
    @patch('cv2.VideoCapture')
    def test_output_folder_creation(self, mock_VideoCapture, mock_makedirs):
        """Test that the output folder is created."""
        mock_video = MagicMock()
        mock_VideoCapture.return_value = mock_video

        # Mock the video capture read to return a valid frame and end of video
        mock_video.read.side_effect = [(True, np.zeros((480, 640, 3), dtype=np.uint8)), (False, None)]

        listInputs = [1]
        videoPath = "your_video"
        output_folder2 = "output"

        capture_frames_at_0_25(listInputs, videoPath, output_folder2)

        # Check if os.makedirs was called to create the output directory
        mock_makedirs.assert_called_once_with('output1')

    @patch('cv2.VideoCapture')
    def test_frame_capture_time_intervals(self, mock_VideoCapture):
        """Test that frames are captured at the correct time intervals."""
        mock_video = MagicMock()
        mock_VideoCapture.return_value = mock_video

        # Mock the return of frames
        mock_video.read.side_effect = [(True, np.zeros((480, 640, 3), dtype=np.uint8)), 
                                       (True, np.zeros((480, 640, 3), dtype=np.uint8)),
                                       (True, np.zeros((480, 640, 3), dtype=np.uint8)), 
                                       (False, None)]
        mock_video.get.return_value = 30  # Mock fps

        listInputs = [1]
        videoPath = "your_video"
        output_folder2 = "outputs"

        capture_frames_at_0_25(listInputs, videoPath, output_folder2)

        # Check if cap.set was called with the correct time intervals: 0, 0.25, 0.5, 0.75
        expected_calls = [
            call(cv2.CAP_PROP_POS_MSEC, 0),
            call(cv2.CAP_PROP_POS_MSEC, 250),
            call(cv2.CAP_PROP_POS_MSEC, 500),
            call(cv2.CAP_PROP_POS_MSEC, 750)
        ]
        self.assertEqual(mock_video.set.call_args_list[:4], expected_calls)

    @patch('cv2.imwrite')
    @patch('cv2.VideoCapture')
    def test_frame_saving(self, mock_VideoCapture, mock_imwrite):
        """Test that frames are saved with the correct filenames."""
        mock_video = MagicMock()
        mock_VideoCapture.return_value = mock_video

        # Mock the return of frames (Valid frames, then end of video)
        mock_video.read.side_effect = [(True, np.zeros((480, 640, 3), dtype=np.uint8)), 
                                       (True, np.zeros((480, 640, 3), dtype=np.uint8)),
                                       (True, np.zeros((480, 640, 3), dtype=np.uint8)), 
                                       (False, None)]
        mock_video.get.return_value = 30  # Mock fps

        listInputs = [1]
        videoPath = "your_video"
        output_folder2 = "outputs"

        capture_frames_at_0_25(listInputs, videoPath, output_folder2)

        # Check that frames were saved with the correct filenames
        self.assertEqual(mock_imwrite.call_count, 3)  # We should save 3 frames
        saved_files = [call[0][0] for call in mock_imwrite.call_args_list]  # Extract the filenames from the calls
        self.assertIn('outputs1/1-frame_0.00s.jpg', saved_files)
        self.assertIn('outputs1/1-frame_0.25s.jpg', saved_files)
        self.assertIn('outputs1/1-frame_0.50s.jpg', saved_files)


if __name__ == "__main__":
    unittest.main(verbosity=2)
