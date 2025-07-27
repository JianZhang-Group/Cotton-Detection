from camera.capture import CameraCapture
from recognition.detector import ObjectDetector
from network import server
import cv2

def main():
    server_instance = server.AsyncServer()
    server_instance.run()

if __name__ == "__main__":
    main()
    