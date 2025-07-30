from camera.capture import CameraCapture
import cv2
from ultralytics import YOLO
from collections import defaultdict
import numpy as np

def test_camera_capture():
    model_path = "yolo11n.pt"  # Path to your YOLO model
    model = YOLO(model_path)
    camera = CameraCapture()
    camera.start_pipeline()
    while True:
        color, depth = camera.get_frame()
        if color is None:
            continue
        results = model.track(color, persist=True)
        annotated_frame = results[0].plot()

        cv2.imshow("YOLO Tracking", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            camera.stop_pipeline()
            cv2.destroyAllWindows()    
            break
if __name__ == "__main__":
    test_camera_capture()
