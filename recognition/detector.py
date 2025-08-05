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
    
    def track_objects(self, frame):
        """
        Track objects in the given frame using the YOLO model.
        :param frame: Input image frame (BGR format).
        :return: Tracking results.
        """
        results = self.model.track(frame, persist=True, device=self.device, verbose=False, tracker='./recognition/custom_tracker.yaml')
        return results

    # 将结果中的边界框坐标转换为中心点坐标并按照y坐标将中心点及其标签排序输出
    def get_sorted_detections(self, results):
        """
        Sort detections by confidence score.
        :param results: Detection results from the YOLO model.
        :return: Sorted list of detections.
        """
        detections = []
        for result in results:
            boxes = result.boxes.xyxy  # 获取边界框坐标
            scores = result.boxes.conf  # 获取置信度分数
            classes = result.boxes.cls  # 获取类别标签
            
            for i, box in enumerate(boxes):
                detections.append({
                    'class': self.labels[int(classes[i])],
                    'x_center': (box[0] + box[2]) / 2,
                    'y_center': (box[1] + box[3]) / 2,
                    'score': scores[i],
                })
        
        # 按照y坐标降序排序
        return sorted(detections, key=lambda x: x['y_center'], reverse=True)

        # 将结果中的边界框坐标转换为中心点坐标并按照置信度分数将中心点及其标签排序输出
    def get_sorted_track_detections(self, results):
        """
        Sort tracking detections by confidence score.
        :param results: Tracking results from the YOLO model.
        :return: Sorted list of tracking detections.
        """
        track_detections = []
        for result in results:
            boxes = result.boxes.cpu().xyxy.numpy()  # 获取边界框坐标
            scores = result.boxes.cpu().conf.numpy()  # 获取置信度分数
            classes = result.boxes.cls.cpu().numpy().astype(int)  # 获取类别标签
            # 如果没有 id，填充为 -1
            if result.boxes.id is not None:
                ids = result.boxes.id.cpu().numpy().astype(int)
            else:
                ids = [-1] * len(boxes)

        for box, score, cls, track_id in zip(boxes, scores, classes, ids):
            track_detections.append({
                'id': int(track_id),
                'class': self.labels[cls],
                'x_center': float((box[0] + box[2]) / 2),
                'y_center': float((box[1] + box[3]) / 2),
                'score': float(score),
            })
        
        # 按照y坐标降序排序
        return sorted(track_detections, key=lambda x: x['y_center'], reverse=True)

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
    
    def draw_track_detections(self, frame, results):
        """
        Draw tracked bounding boxes, IDs, and labels on the frame.
        :param frame: Input image frame (BGR format).
        :param results: Tracking results from the YOLO model.
        :return: Annotated frame.
        """
        for result in results:
            boxes = result.boxes.xyxy
            scores = result.boxes.conf
            classes = result.boxes.cls
            ids = result.boxes.id if result.boxes.id is not None else [-1] * len(boxes)

            for box, score, cls, track_id in zip(boxes, scores, classes, ids):
                label = self.labels[int(cls)]
                score_val = float(score) if score is not None else 1.0
                track_id_val = int(track_id) if track_id is not None else -1

                label_text = f"ID:{track_id_val} {label} {score_val:.2f}"
                
                # Draw bounding box
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Draw label text
                cv2.putText(frame, label_text, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame