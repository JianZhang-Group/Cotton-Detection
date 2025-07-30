import cv2
import numpy as np
from pyorbbecsdk import *
from utils.utils import frame_to_bgr_image
import yaml

with open("./config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

ESC_KEY = config.get("ESC_KEY", 27)
MIN_DEPTH = config.get("MIN_DEPTH", 20)
MAX_DEPTH = config.get("MAX_DEPTH", 10000)
FRAME_WAIT_TIMEOUT = config.get("FRAME_WAIT_TIMEOUT", 500)

class CameraCapture:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.pipeline = None

    def start_capture(self):
        # 如果是普通摄像头
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

    def start_pipeline(self):
        # 如果是Orbbec深度摄像头
        self.pipeline = Pipeline()
        self.pipeline.start()
        print("Pipeline started successfully.")

    def get_frame(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Failed to capture frame")
            return frame
        elif self.pipeline is not None:
            frames = self.pipeline.wait_for_frames(FRAME_WAIT_TIMEOUT)
            if frames is None:
                return None, None
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            if color_frame is None or depth_frame is None:
                return None, None
            color_image = frame_to_bgr_image(color_frame)
            if depth_frame.get_format() != OBFormat.Y16:
                print("Depth format is not Y16")
                return color_image, None
            width = depth_frame.get_width()
            height = depth_frame.get_height()
            scale = depth_frame.get_depth_scale()
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16).reshape((height, width))
            depth_data = depth_data.astype(np.float32) * scale
            depth_data = np.where((depth_data > MIN_DEPTH) & (depth_data < MAX_DEPTH), depth_data, 0).astype(np.uint16)
            depth_image = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            depth_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)
            return color_image, depth_image
        else:
            raise Exception("Camera not initialized.")

    def show_stream(self, window_width=1280, window_height=720):
        cv2.namedWindow("QuickStart Viewer", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("QuickStart Viewer", window_width, window_height)
        while True:
            try:
                color_image, depth_image = self.get_frame()
                if color_image is None:
                    continue
                color_image_resized = cv2.resize(color_image, (window_width // 2, window_height))
                if depth_image is not None:
                    depth_image_resized = cv2.resize(depth_image, (window_width // 2, window_height))
                    combined_image = np.hstack((color_image_resized, depth_image_resized))
                else:
                    combined_image = color_image_resized
                cv2.imshow("QuickStart Viewer", combined_image)
                if cv2.waitKey(1) in [ord('q'), ESC_KEY]:
                    break
            except KeyboardInterrupt:
                break
        cv2.destroyAllWindows()
        if self.pipeline is not None:
            self.pipeline.stop()
            print("Pipeline stopped and all windows closed.")
        if self.cap is not None:
            self.cap.release()

    def stop_capture(self):
        if self.pipeline is not None:
            self.pipeline.stop()
            self.pipeline = None
            print("Pipeline stopped.")
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("Camera released.")
    
    def get_depth_from_point(depth_frame, x, y, window_size=5, min_depth=20, max_depth=10000):
        """
        根据图像坐标 (x, y) 获取深度值 (mm)，使用一个小窗口取中位数来减少噪声
        :param depth_frame: Orbbec 的 depth_frame 对象
        :param x: 像素坐标 x
        :param y: 像素坐标 y
        :param window_size: 邻域大小 (必须是奇数)，默认 5 表示取 5x5 窗口
        :param min_depth: 最小有效深度，单位 mm
        :param max_depth: 最大有效深度，单位 mm
        :return: 中位数深度 (int, mm)，无效时返回 None
        """
        try:
            width = depth_frame.get_width()
            height = depth_frame.get_height()
            scale = depth_frame.get_depth_scale() * 1000  # 转换为 mm

            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16).reshape((height, width))
            depth_data = depth_data.astype(np.float32) * scale

            # 过滤不合理深度
            depth_data = np.where((depth_data > min_depth) & (depth_data < max_depth), depth_data, 0)

            # 限制窗口范围
            half_w = window_size // 2
            x_min, x_max = max(0, x - half_w), min(width, x + half_w + 1)
            y_min, y_max = max(0, y - half_w), min(height, y + half_w + 1)

            roi = depth_data[y_min:y_max, x_min:x_max]
            valid_depths = roi[roi > 0]

            if valid_depths.size == 0:
                return None

            return int(np.median(valid_depths))

        except Exception as e:
            print(f"[get_depth_from_point] Failed: {e}")
            return None

# 用法示例
if __name__ == "__main__":
    cam = CameraCapture()
    # 如果是普通摄像头
    # cam.start_capture()
    # 如果是Orbbec深度摄像头
    cam.start_pipeline()
    cam.show_stream()