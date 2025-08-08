from collections import defaultdict

import cv2
import numpy as np

from ultralytics import YOLO
from camera.capture import CameraCapture

# Load the YOLO11 model
model = YOLO("models/best.pt")

# Open the video file
# video_path = "path/to/video.mp4"
# cap = cv2.VideoCapture(video_path)
cam = CameraCapture()
cam.start_pipeline()
# Store the track history
track_history = defaultdict(lambda: [])

# Loop through the video frames
while True:
    # Read a frame from the video
    color_frame,_ = cam.get_frame()

    if color_frame is None:
        continue
    else:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        result = model.track(color_frame, persist=True)[0]

        # Get the boxes and track IDs
        if result.boxes and result.boxes.is_track:
            boxes = result.boxes.xywh.cpu()
            track_ids = result.boxes.id.int().cpu().tolist()

            # Visualize the result on the frame
            color_frame = result.plot()

            # Plot the tracks
            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))  # x, y center point
                if len(track) > 30:  # retain 30 tracks for 30 frames
                    track.pop(0)

                # Draw the tracking lines
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(color_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            # Display the annotated frame
        cv2.imshow("YOLO11 Tracking", color_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Release the video capture object and close the display window
cam.stop_capture
cv2.destroyAllWindows()