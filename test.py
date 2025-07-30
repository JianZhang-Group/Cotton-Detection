from camera.capture import CameraCapture
import cv2
from ultralytics import YOLO
from recognition.detector import ObjectDetector

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

def test_tracker():
    model_path = 'models/best.pt'  # 替换为你的模型路径
    detector = ObjectDetector(model_path, device='0')

    # 启动摄像头捕获
    camera = CameraCapture()
    camera.start_pipeline()

    while True:
        color,depth = camera.get_frame()
        if color is None:
            continue
        results = detector.track_objects(color)
        print("Tracking results:", results)
        sorted_detections = detector.get_sorted_track_detections(results)
        color = detector.draw_track_detections(color, results)
        cv2.imshow("Object Detection", color)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.stop_capture()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    test_tracker()
