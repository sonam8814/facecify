import cv2
import os

def extract_frames_from_videos(input_dir, output_dir, frame_count=10):
    """
    Extract frames from videos in the input directory and save them to the output directory.

    Parameters:
    - input_dir: Directory containing input videos.
    - output_dir: Directory to save extracted frames.
    - frame_count: Number of frames to extract per video.

    Returns:
    - 'no_videos': If no videos are found in the input directory.
    - 'frames_already_extracted': If frames already exist and extraction is skipped.
    - 'success': If frames are successfully extracted.
    - 'error': If an error occurs during extraction.
    """
    # Check if there are any video files in the input directory
    video_files = [f for f in os.listdir(input_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
    if not video_files:
        print("No videos found in the input directory.")
        return 'no_videos'
    
    # Iterate over all the video files in the input directory
    for filename in video_files:
        video_path = os.path.join(input_dir, filename)
        video_name = os.path.splitext(filename)[0]
        video_output_dir = os.path.join(output_dir, video_name)
        
        # Skip extraction if frames already exist
        if os.path.exists(video_output_dir) and len(os.listdir(video_output_dir)) >= frame_count:
            print(f"Frames already extracted for {filename}. Skipping extraction.")
            continue
        
        # Create a directory for each video to store the frames
        os.makedirs(video_output_dir, exist_ok=True)
        
        # Capture the video
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Error opening video file: {filename}")
                return 'error'
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / cap.get(cv2.CAP_PROP_FPS)
            print(f'Processing Video: {filename}, Duration: {duration:.2f}s, Total Frames: {total_frames}')
            
            # Calculate the interval to capture frames
            interval = max(1, int(total_frames / frame_count))
            frame_number = 0
            extracted_frame_count = 0
            
            while cap.isOpened() and extracted_frame_count < frame_count:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_number % interval == 0:
                    frame_filename = os.path.join(video_output_dir, f'frame_{frame_number}.jpg')
                    cv2.imwrite(frame_filename, frame)
                    extracted_frame_count += 1
                frame_number += 1
            
            cap.release()
            print(f'Extracted {extracted_frame_count} frames from {filename}')
        
        except Exception as e:
            print(f"Error during frame extraction from {filename}: {e}")
            return 'error'
    
    print('Frame extraction completed successfully.')
    return 'success'
