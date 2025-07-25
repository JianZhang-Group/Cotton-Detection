import cv2
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, model_path, device='cpu'):
        self.model = YOLO(model_path)
        self.device = device
        self.labels = self.model.names  # 获取类别名称
        print("Detected classes:", self.labels)

    def detect_objects(self, frame):
        """
        Detect objects in the given frame using the YOLO model.
        :param frame: Input image frame (BGR format).
        :return: Detection results.
        """
        # Ultralytics YOLO自动处理BGR/RGB，无需手动转换
        results = self.model(frame, device=self.device, verbose=False)
        return results

    def draw_detections(self, frame, results):
        """
        Draw detected bounding boxes and labels on the frame.
        :param frame: Input image frame (BGR format).
        :param results: Detection results from the YOLO model.
        :return: Annotated frame.
        """

        for result in results:
            boxes = result.boxes.xyxy  # 获取边界框坐标
            scores = result.boxes.conf  # 获取置信度分数
            classes = result.boxes.cls  # 获取类别标签

            for i, box in enumerate(boxes):
                label = self.labels[int(classes[i])]
                score = scores[i] if scores is not None else 1.0
                label_text = f"{label} {score:.2f}"
                
                # Draw bounding box and label
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        return frame