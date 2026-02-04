# Ferry Monitor 🚢

Automated monitoring system for Pierce County Ferry docks using computer vision to detect ship presence.

## Features

- 🔄 Automatic checks every 60 seconds (configurable)
- 🤖 YOLOv8-based ship detection
- 🔧 Easy model switching (modular architecture)
- 📊 Real-time console output
- 📝 Optional logging to file
- 💾 Optional image saving of detections
- 🎯 Monitors multiple docks simultaneously

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - For downloading images
- `pillow` - For image processing
- `opencv-python` - OpenCV support
- `ultralytics` - YOLOv8 implementation
- `schedule` - Task scheduling

### 2. Run the Monitor

```bash
python monitor.py
```

That's it! The script will:
1. Load the YOLOv8 model (downloads automatically on first run)
2. Start checking both docks every minute
3. Print results to console

### Example Output

```

Ferry Check - 2024-02-04 14:30:00

Checking Steilacoom Dock...
🚢 SHIP PRESENT at Steilacoom Dock (2024-02-04 14:30:02)
   └─ Detected: 1 ship(s) | Confidence: 0.87

Checking Anderson Island Dock...
⚓ NO SHIP at Anderson Island Dock (2024-02-04 14:30:04)

```

## Configuration

Edit `config/settings.py` to customize:

### Change Detection Model

```python
DETECTION_CONFIG = {
    'model_type': 'yolov8',  # Model type
    'model_size': 'n',       # n=nano, s=small, m=medium, l=large, x=xlarge
    'confidence_threshold': 0.25,  # Detection threshold
    'target_classes': [8],   # COCO class IDs (8=boat)
}
```

**Model sizes** (speed vs accuracy tradeoff):
- `'n'` (nano) - Fastest, less accurate
- `'s'` (small) - Good balance
- `'m'` (medium) - Better accuracy
- `'l'` (large) - High accuracy
- `'x'` (xlarge) - Best accuracy, slowest

### Change Check Interval

```python
CHECK_INTERVAL_SECONDS = 60  # Check every 60 seconds
```

### Enable Logging

```python
LOG_DETECTIONS = True
LOG_FILE = "ferry_detections.log"
```

### Save Detection Images

```python
SAVE_IMAGES = True
SAVE_DIR = "detected_images"
```

### Add More Docks

```python
DOCKS = {
    "Steilacoom Dock": "https://online.co.pierce.wa.us/xml/abtus/ourorg/pwu/ferry/stlferry.jpg",
    "Anderson Island Dock": "https://online.co.pierce.wa.us/xml/abtus/ourorg/pwu/ferry/aiferry.jpg",
    "Your New Dock": "https://example.com/camera.jpg"
}
```

## Switching Detection Models

The project is designed for easy model switching. Here's how:

### Option 1: Change YOLOv8 Model Size

In `config/settings.py`:

```python
DETECTION_CONFIG = {
    'model_type': 'yolov8',
    'model_size': 'm',  # Changed from 'n' to 'm' for better accuracy
    ...
}
```

### Option 2: Add a Custom Model

1. Create a new detector class in `models/` (inherit from `BaseDetector`)
2. Implement the `load_model()` and `detect()` methods
3. Register it in `models/detector_factory.py`

Example custom detector:

```python
# models/my_custom_detector.py
from models.base_detector import BaseDetector
from PIL import Image
from typing import Tuple, Dict, Any

class MyCustomDetector(BaseDetector):
    def load_model(self):
        # Load your model here
        self.model = load_my_model()
    
    def detect(self, image: Image.Image) -> Tuple[bool, Dict[str, Any]]:
        # Run detection
        results = self.model.predict(image)
        ship_detected = results.has_ship
        
        detection_info = {
            'ship_detected': ship_detected,
            'confidence': results.confidence,
            # ... other info
        }
        
        return ship_detected, detection_info
```

Then in `models/detector_factory.py`, add:

```python
elif model_type == 'mycustom':
    from models.my_custom_detector import MyCustomDetector
    return MyCustomDetector(confidence_threshold=confidence)
```

Update `config/settings.py`:

```python
DETECTION_CONFIG = {
    'model_type': 'mycustom',
    ...
}
```

## Project Structure

```
ferry_monitor/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration file
├── models/
│   ├── __init__.py
│   ├── base_detector.py     # Abstract base class
│   ├── yolov8_detector.py   # YOLOv8 implementation
│   └── detector_factory.py  # Model factory
├── utils/
│   ├── __init__.py
│   └── scraper.py           # Image download utilities
├── monitor.py               # Main script
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Detected Classes

The default configuration detects class ID 8 from the COCO dataset, which is "boat". This includes:

- Sailboats
- Motorboats
- Ferries
- Ships
- Yachts

To detect additional classes, modify `target_classes` in config:

```python
'target_classes': [8, 9],  # 8=boat, 9=traffic light (example)
```

Common COCO class IDs:
- 0: person
- 1: bicycle
- 2: car
- 8: boat
- 16: bird
- More at: https://tech.amikelive.com/node-718/what-object-categories-labels-are-in-coco-dataset/

## Troubleshooting

### Ship Detection Not Working?

**Step 1: Run the debug script**
```bash
python debug_detection.py
```

This will show you exactly what the model is detecting and save annotated images.

**Step 2: Tune the threshold**
```bash
python tune_threshold.py --batch
```

This tests multiple thresholds and recommends the best one.

**Step 3: Read the troubleshooting guide**
```bash
# See TROUBLESHOOTING.md for detailed help
```

### Common Solutions

**If boats are detected with low confidence:**
```python
# Lower the threshold in config/settings.py
'confidence_threshold': 0.15,
```

**If boats aren't detected at all:**
```python
# Try a larger model
'model_size': 's',  # or 'm', 'l', 'x'
```

See `TROUBLESHOOTING.md` for complete guide.

### Debug Detection Script

The `debug_detection.py` script helps diagnose detection issues:

```bash
python debug_detection.py
```

**What it does:**
- Downloads current images from both docks
- Tests detection at multiple thresholds (0.01 to current)
- Shows ALL detected objects, not just boats
- Saves annotated images with bounding boxes
- Provides detailed statistics on what's being detected

**Output files** (in `debug_output/`):
- `*_original.jpg` - Original camera image
- `*_annotated.jpg` - Image with detection boxes drawn

### Threshold Tuning Tool

Find the optimal detection threshold with `tune_threshold.py`:

**Batch Mode** (automatic):
```bash
# Test default thresholds
python tune_threshold.py --batch

# Test with specific model
python tune_threshold.py --batch --model m

# Test custom thresholds
python tune_threshold.py --batch --thresholds "0.1,0.15,0.2,0.25,0.3"
```

**Interactive Mode** (manual):
```bash
python tune_threshold.py

# Commands:
# t 0.15    - Set threshold to 0.15
# m s       - Change model to small
# a         - Toggle showing all classes
# [Enter]   - Run detection
# q         - Quit
```

The tool shows:
- Detection results for each threshold
- Summary statistics
- Recommended optimal threshold

### Model Download Notes

First run downloads YOLOv8 weights automatically:
- nano (n): ~6 MB
- small (s): ~22 MB
- medium (m): ~52 MB
- large (l): ~131 MB
- xlarge (x): ~137 MB

If download fails:
- Check internet connection
- Try a larger timeout in `utils/scraper.py`
- Manually download from Ultralytics

### False Detections

Adjust confidence threshold:

```python
'confidence_threshold': 0.5,  # Higher = fewer false positives
```

Or use a larger model:

```python
'model_size': 'm',  # Medium model for better accuracy
```

### Image Download Fails

- Check if URLs are accessible
- Verify network connection
- Check firewall settings

## Running as a Service (Linux)

To run continuously in background:

1. Create systemd service file:

```bash
sudo nano /etc/systemd/system/ferry-monitor.service
```

2. Add:

```ini
[Unit]
Description=Ferry Monitor Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/ferry_monitor
ExecStart=/usr/bin/python3 /path/to/ferry_monitor/monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start:

```bash
sudo systemctl enable ferry-monitor
sudo systemctl start ferry-monitor
sudo systemctl status ferry-monitor
```

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues or questions:
- Check configuration in `config/settings.py`
- Review logs in `ferry_detections.log`
- Ensure all dependencies are installed
- Verify image URLs are accessible

## Future Enhancements

Possible additions:
- Web dashboard for monitoring
- Email/SMS alerts when ships detected
- Historical tracking and statistics
- Multiple detection models comparison
- GPU acceleration support
- Docker containerization