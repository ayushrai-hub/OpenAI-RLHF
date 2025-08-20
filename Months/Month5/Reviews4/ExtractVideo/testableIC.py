import cv2
import os

def capture_frames_at_0_25(listInputs: list[int], videoPath: str, output_folder2: str) -> None:

    for index, item in enumerate(listInputs):

        # Open the video file
        video_path = f'{videoPath}{item}.mp4'
        output_folder = f'{output_folder2}{item}'
        fileName2 = item

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        cap = cv2.VideoCapture(video_path)

        # Get the frames per second (fps) of the video
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * 0.25)  # Calculate the interval for 0.25 seconds

        # Initialize a counter for the frames
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Check if the current frame is at 0.25-second intervals
            if frame_count % frame_interval == 0:
                # Calculate the time in seconds
                seconds = frame_count / fps
                
                # Generate the file name
                filename = f'{fileName2}-frame_{seconds:.2f}s.jpg'
                file_path = os.path.join(output_folder, filename)
                
                # Put the seconds and file name on the frame
                cv2.putText(frame, f'Time: {seconds:.2f}s', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f'File: {fileName2}-{filename}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                
                # Show the frame (optional)
                # cv2.imshow('Frame', frame)
                
                # Save the frame with the file name
                cv2.imwrite(file_path, frame)
            
            frame_count += 1
            
            # Press 'q' to quit the video display
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture object and close all windows
        cap.release()
        cv2.destroyAllWindows()
