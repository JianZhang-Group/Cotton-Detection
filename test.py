from camera.capture import CameraCapture
import cv2

def test_camera_capture():
    camera = CameraCapture()
    camera.start_pipeline()
    color, depth = camera.get_frame()
    # 保存图片
    cv2.imwrite("test_color_image.jpg", color)
    cv2.imwrite("test_depth_image.jpg", depth)
    camera.stop_capture()
    print("Camera capture test passed.")

if __name__ == "__main__":
    test_camera_capture()
