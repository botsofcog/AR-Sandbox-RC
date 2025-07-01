# AR Sandbox - Interactive Topographic Visualization

An augmented reality sandbox that creates real-time topographic maps using Xbox Kinect depth sensing and projector visualization.

## Hardware Requirements

- Xbox 360 Kinect sensor

- Epson projector (or compatible)

- Sand table/box

- Computer with USB ports

- Mounting system for Kinect and projector

## Software Stack

- Python 3.8+

- libfreenect (Kinect drivers)

- OpenCV (computer vision)

- NumPy (numerical computing)

- Pygame (graphics rendering)

- Matplotlib (contour generation)

## Project Structure

```

ar_sandbox/
├── src/
│   ├── kinect/          # Kinect depth sensing
│   ├── processing/      # Depth data processing
│   ├── visualization/   # Topographic rendering
│   ├── calibration/     # System calibration
│   └── main.py         # Main application
├── config/             # Configuration files
├── tests/              # Unit tests
└── requirements.txt    # Python dependencies

```

## Installation

1. Install libfreenect drivers
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run calibration: `python src/calibration/calibrate.py`
4. Start the sandbox: `python src/main.py`

## Features

- Real-time depth sensing

- Topographic contour generation

- Elevation color mapping

- Interactive sand manipulation

- Educational visualization modes

## Educational Applications

- Geography and topography learning

- Understanding elevation and contour lines

- Interactive landscape modeling

- STEM education tool
