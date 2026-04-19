# AI Security Camera
## Project Description
This repository contains code relating to my project of creating a custom security camera. This system will include the following features:
- A camera running local object detection algorithms to identify, locate and track features in the frame.
- A pan and tilt system utilising PID control to track features as they move through the image frame.
- A gRPC-based network architecture such that the camera module can stream detection events to a remote client and trigger desktop notifications when some criteria are met (such as a person within a certain distance of the camera).

## Usage

Clone the repo onto a Raspberry Pi with a connected camera module, then set up the environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install the required YOLO model. You can edit `install_yolo.sh` if you would like to use a different model instead, or alternatively download one from the internet.
```bash
./scripts/install_yolo.sh
```

Run object detection from the repo root:

```bash
python -m detection.detection_yolo --config configs/yolo_config.yaml
```

Press `q` in the preview window to exit. Detection parameters (model path, confidence threshold) and camera settings (resolution, pixel format) can be tuned in [configs/yolo_config.yaml](configs/yolo_config.yaml).

## Tech Stack

- **Hardware**: Raspberry Pi + Pi Global Shutter Camera (pan/tilt servos planned)
- **Object detection**: [Ultralytics YOLO](https://docs.ultralytics.com/) (YOLOv26n), exported to [NCNN](https://github.com/Tencent/ncnn) for faster inference on ARM
- **Camera capture**: [picamera2](https://github.com/raspberrypi/picamera2)
- **Image processing / display**: OpenCV
- **Config**: YAML via PyYAML
- **Control (planned)**: PID loop driving pan/tilt servos
- **Networking (planned)**: [gRPC](https://grpc.io/) over HTTP/2 with [Protobuf](https://protobuf.dev/) schemas — server-streaming for detection events, bidirectional streaming for remote pan/tilt control
- **Client notifications (planned)**: desktop pop-ups via `notify-send` (Linux)
- **Polyglot stubs (planned)**: Python server on the Pi, with a Go or C++ client generated from the same `.proto` definitions

## Repo Structure

```
security_camera/
├── .github/
│   └── workflows/
│       ├── pylint.yml
│       └── ruff.yml
├── configs/                  # YAML configs for detection + camera
│   └── yolo_config.yaml
├── detection/                # Detection pipeline
│   └── detection_yolo.py     # Capture frames, run YOLO, render output
├── helpers/                  # Shared utilities
│   └── load_config.py        # YAML config loader
├── models/                   # YOLO weights + exported NCNN model
│   ├── yolo26n.pt
│   └── yolo26n_ncnn_model/
├── scripts/
│   ├── install_yolo.sh       # Shell script to install the YOLO model
├── .gitignore
├── .pylintrc
├── README.md
├── requirements-pi.txt       # Pi-specific libraries
└── requirements.txt
```

