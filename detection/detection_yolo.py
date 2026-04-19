"""Live object detection on a Raspberry Pi camera using a YOLO model."""

import argparse
from pathlib import Path
from typing import Dict

import cv2
from cv2.typing import MatLike
from ultralytics import YOLO
from picamera2 import Picamera2

from helpers.load_config import load_config


def initialise(config_filepath: str):
    """Load config, prepare the YOLO model and start the Pi camera."""
    # load config
    config = load_config(config_filepath)

    # load the YOLO model (defined in config)
    root = Path(__file__).resolve().parents[1]
    model_path = root / config["objdet"]["model"]

    # check if ncnn model already exists, if not export it
    ncnn_path = model_path.with_name(model_path.stem + "_ncnn_model")

    if not ncnn_path.exists():
        # export the model to ncnn format for faster inference on raspberry pi
        ncnn_path = YOLO(model_path).export(format="ncnn")

    # load the exported ncnn model
    ncnn_model = YOLO(ncnn_path)

    # initialise pi global shutter camera
    picam2 = Picamera2()
    preview = picam2.create_preview_configuration(
        main={
            "size": tuple(config["camera"]["resolution"]),
            "format": config["camera"]["format"],
        }
    )
    picam2.preview_configuration.align()
    picam2.configure(preview)
    picam2.start()
    return picam2, ncnn_model, config


def capture(picam2: Picamera2, config: Dict[str, any]):
    """Capture a frame."""
    frame = picam2.capture_array()
    if config["camera"]["flip_vertical"]:
        frame = cv2.flip(frame, 0)
    return frame


def inference(frame: MatLike, model: YOLO, config: Dict[str, any]) -> list:
    """Run inference to identify and classify objects on the frame."""
    return model(frame, conf=config["objdet"]["conf"], verbose=False)


def display(results: list) -> None:
    """Display object detection results over captured frame."""
    annotated_frame = results[0].plot()
    cv2.imshow("Camera", annotated_frame)


def capture_and_detect(picam2: Picamera2, model: YOLO, config: Dict):
    """Capture a frame, run inference and display the annotated result."""
    # capture frame
    frame = capture(picam2, config)

    # run inference
    results = inference(frame, model, config)

    # visualise results on frame
    display(results)


def main():
    """Entry point: parse args and run the detection loop."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--config", help="Absolute path to the config file.", required=True
    )
    args = parser.parse_args()

    config_filepath = args.config

    picam2, model, config = initialise(config_filepath)

    try:
        while True:
            capture_and_detect(picam2, model, config)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        picam2.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
