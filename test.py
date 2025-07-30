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
        sorted_detections = detector.get_sorted_track_detections(results)
        # 根据点获得深度信息
        for detection in sorted_detections:
            x_center = int(detection['x_center'])
            y_center = int(detection['y_center'])
            depth_value = camera.get_depth_from_point(depth_data, x_center, y_center)
            if depth_value is not None:
                cv2.putText(color, f"Depth: {depth_value}mm", (x_center, y_center - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        color = detector.draw_track_detections(color, results)
        cv2.imshow("Object Detection", color)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.stop_capture()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    test_tracker()
