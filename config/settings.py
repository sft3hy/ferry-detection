"""
Configuration file for Ferry Monitor
"""

import os

# Dock cameras to monitor
DOCKS = {
    "Steilacoom Dock": "https://online.co.pierce.wa.us/xml/abtus/ourorg/pwu/ferry/stlferry.jpg",
    "Anderson Island Dock": "https://online.co.pierce.wa.us/xml/abtus/ourorg/pwu/ferry/aiferry.jpg"
}


# Detection settings
DETECTION_CONFIG = {
    # Pre-processing settings
    'image_optimization': False,  # Enable resize, letterbox, and auto-orient
    'imgsz': 640,               # Target size for resizing (e.g., 640 or 1280)
    
    # Model type: 'yolov8', 'yolov5', or 'custom'
    'model_type': 'yolo26',
    
    # Specific model path (Hugging Face ID or local path)
    # Set this to a valid Hugging Face repo ID or local path to use a custom model
    # Example: 'keremberke/yolov8m-ship-detection' (may require authentication)
    'model_path': None,
    
    # Model size for standard YOLO models (ignored if model_path is set)
    'model_size': 'x',
    
    # Confidence threshold for detection (0.0 to 1.0)
    'confidence_threshold': 0.04,
    
    # Classes to detect
    # Standard COCO: 8 is 'boat'
    # For custom models, check the model's class list (often 0 for single-class)
    'target_classes': [8],
    
    # Custom model path (only used if model_type is 'custom')
    'custom_model_path': None
}

# Scheduling
CHECK_INTERVAL_SECONDS = 60  # Run every minute

# Logging
LOG_DETECTIONS = False
LOG_FILE = "ferry_detections.log"

# Image saving (optional)
SAVE_IMAGES = True
SAVE_DIR = "detected_images"
SAVE_ALL_CAPTURES = True  # Debug: save all downloaded images regardless of detection


CS_HOST = "chatsurfer.nro.mil"
TEST = os.environ["TEST_LOCAL"]
CHATKEY = os.environ["CHATKEY"]
SESSION_EXPIRATION_TIME=60*60*12

if TEST == "True":
    CERT_PATH = "/usr/local/share/ca-certificates/justcert.crt"
    KEY_PATH = "/usr/local/share/ca-certificates/decrypted.key"
    CA_BUNDLE_PATH = "/usr/local/share/ca-certificates/dod_CAs.pem"

else:
    CERT_PATH = "/config/justcert.crt" #/etc/rancher/ssl/npe/tls.crt"
    KEY_PATH = "/config/decrypted.key"#/etc/rancher/ssl/npe/tls.key"
    CA_BUNDLE_PATH = "/config/dod_CA.pem"#/etc/rancher/ssl/ca/ca-bundle"  # Path is mountPath + keyName
