from camera.capture import CameraCapture
from recognition.detector import ObjectDetector
from network import server
import cv2

def main():
    # Initialize camera
    camera = CameraCapture()
    camera.start_pipeline()

    # Initialize object detector
    detector = ObjectDetector(model_path="./models/yolo11n.pt", device='0')

    while True:
        # Capture frame from camera
        color_image, depth_image = camera.get_frame()
        if color_image is None:
            continue
        
        # Detect objects in the frame
        results = detector.detect_objects(color_image)

        # Display the frame (optional)
        cv2.imshow("Camera Feed", color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # Draw detections on the frame
        if results:
            detector.draw_detections(color_image, results)
            cv2.imshow("Detections", color_image)

    camera.stop_capture()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    server_instance = server.AsyncServer()
    server_instance.run()
    