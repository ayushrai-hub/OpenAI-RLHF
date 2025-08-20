#ideal_completion.py
import cv2
import os

def capture_frames_at_0_25(listInputs,videoPath,output_folder2):

    for index, item in enumerate(listInputs):
        # Open the video file
        video_path = f'{videoPath}{item}.mp4'
        print("video_path : " + video_path)
        output_folder = f'{output_folder2}{item}'
        fileName2 = item
        print(fileName2)

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        cap = cv2.VideoCapture(video_path)

        # Get the frames per second (fps) of the video
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:  # Handle the case where fps can't be retrieved
            print(f"Error: Cannot determine FPS for {video_path}")
            continue

        # First, capture the frame at 0.00s
        cap.set(cv2.CAP_PROP_POS_MSEC, 0)  # Set to the first frame (0.00 seconds)
        ret, frame = cap.read()
        if ret:
            filename = f'{fileName2}-frame_0.00s.jpg'
            file_path = os.path.join(output_folder, filename)
            cv2.putText(frame, f'Time: 0.00s', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f'File: {fileName2}-{filename}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imwrite(file_path, frame)
    
        # Interval for capturing frames at 0.25 second
        time_interval = 0.25  # 0.25 seconds

        # Initialize the time counter
        time_counter = 0.25  # Start at 0.25 seconds to avoid double capture of 0.00s

        while cap.isOpened():
            # Set the current position in the video based on the time interval
            cap.set(cv2.CAP_PROP_POS_MSEC, time_counter * 1000)  # Set position in milliseconds
            ret, frame = cap.read()

            if not ret:
                break
            # Calculate the time in seconds (for labeling)
            seconds = time_counter
        
            # Generate the file name
            filename = f'{fileName2}-frame_{seconds:.2f}s.jpg'
            file_path = os.path.join(output_folder, filename)

            # Put the seconds and file name on the frame
            cv2.putText(frame, f'Time: {seconds:.2f}s', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f'File: {fileName2}-{filename}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
            # Save the frame with the file name
            cv2.imwrite(file_path, frame)
        
            # Move to the next time interval (0.25 seconds ahead)z
            time_counter += time_interval

            # Press 'q' to quit the video display (optional, only if displaying frames)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture object and close all windows
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    listInputs = [7, 1, 71, 12, 26, 35, 55, 58, 61, 32, 9, 2, 3, 23, 50, 63]
    videoPath = "/Volumes/NO NAME/dataset/upload to kaggle/video test detection Socket EV/In youtube/"
    output_folder2 = f"/Volumes/NO NAME/dataset/upload to kaggle/image est detection Socket EV/extracted_frames/"
    capture_frames_at_0_25(listInputs,videoPath,output_folder2)