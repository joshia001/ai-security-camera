import sys
from typing import Dict
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2
from ultralytics import YOLO
from picamera2 import Picamera2

from helpers.load_config import load_config


def initialise(config_filepath: str):
    # load config
    config = load_config(config_filepath)

    # load the YOLO model (defined in config)
    ROOT = Path(__file__).resolve().parents[1]
    model_path = ROOT / config["objdet"]["model"]

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


def capture_and_detect(picam2: Picamera2, model: YOLO, config: Dict):
    # capture frame
    frame = picam2.capture_array()
    frame = cv2.flip(frame, 0)

    # run inference
    results = model(frame, conf=config["objdet"]["conf"], verbose=False)

    # visualise results on frame
    annotated_frame = results[0].plot()

    cv2.imshow("Camera", annotated_frame)


def main():
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
