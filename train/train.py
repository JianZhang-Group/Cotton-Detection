from ultralytics import YOLO


if __name__ == "__main__":
    # Load a model
    model = YOLO("yolo11n.yaml")  # build a new model from YAML
    model = YOLO("yolo11n.pt")  # load a pretrained model (recommended for training)
    model = YOLO("yolo11n.yaml").load("yolo11n.pt")  # build from YAML and transfer weights

    # Train the model
    results = model.train(data="train/datasets/bottle cap.v2i.yolov11/data.yaml", epochs=64, imgsz=640)