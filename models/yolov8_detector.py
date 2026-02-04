"""
YOLOv8 implementation for ship detection
"""
from PIL import Image
from typing import Tuple, Dict, Any
import logging
import numpy as np

from models.base_detector import BaseDetector

logger = logging.getLogger(__name__)


class YOLOv8Detector(BaseDetector):
    """
    YOLOv8 detector for ship/boat detection using Ultralytics
    """
    
    def __init__(self, model_path: str = None, model_size: str = 'n', 
                 confidence_threshold: float = 0.25, target_classes: list = None):
        """
        Initialize YOLOv8 detector
        
        Args:
            model_path: Specific model path or Hugging Face ID
            model_size: Model size ('n', 's', 'm', 'l', 'x')
            confidence_threshold: Minimum confidence for detections
            target_classes: List of class IDs to detect (default: [8] for boat)
        """
        super().__init__(confidence_threshold)
        self.model_path = model_path
        self.model_size = model_size
        self.target_classes = target_classes or [8]  # 8 is 'boat' in COCO
        self.model = None
        self.device = self._get_device()
        logger.info(f"Using device: {self.device}")
        self.load_model()
    
    def _get_device(self) -> str:
        """
        Determine the best available device for inference
        """
        try:
            import torch
            if torch.backends.mps.is_available():
                return 'mps'
            elif torch.cuda.is_available():
                return 'cuda'
            else:
                return 'cpu'
        except ImportError:
            logger.warning("Torch not found, defaulting to CPU")
            return 'cpu'
    
    def load_model(self) -> None:
        """
        Load YOLOv8 model from Ultralytics
        """
        try:
            from ultralytics import YOLO
            
            # Determine model file path
            if self.model_path:
                if self.model_path.endswith('.pt'):
                    model_file = self.model_path
                else:
                    # Assume it's a HF repo, convert to local filename
                    safe_name = self.model_path.replace('/', '_')
                    if not safe_name.endswith('.pt'):
                        safe_name += '.pt'
                    model_file = safe_name
            else:
                model_file = f'yolov8{self.model_size}.pt'

            # Download if missing and looks like a HF repo or URL
            import os
            if not os.path.exists(model_file) and self.model_path and '/' in self.model_path:
                logger.info(f"Model {model_file} not found locally. Attempting download from Hugging Face...")
                try:
                    import requests
                    url = f"https://huggingface.co/{self.model_path}/resolve/main/best.pt"
                    logger.info(f"Downloading from {url}...")
                    response = requests.get(url, allow_redirects=True)
                    response.raise_for_status()
                    
                    with open(model_file, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Downloaded model to {model_file}")
                except Exception as e:
                    logger.error(f"Failed to download model: {e}")
                    # Don't raise yet, let YOLO try to load it or fail
                    pass

            logger.info(f"Loading YOLOv8 model from: {model_file}")
            self.model = YOLO(model_file)
            logger.info(f"Successfully loaded {model_file}")
            
            # Log class names to help with debugging target classes
            # if hasattr(self.model, 'names'):
                # logger.info(f"Model classes: {self.model.names}")
        except ImportError:
            logger.error("Ultralytics not installed. Run: pip install ultralytics")
            raise
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            raise
    
    def detect(self, image: Image.Image) -> Tuple[bool, Dict[str, Any]]:
        """
        Detect ships/boats in an image using YOLOv8
        
        Args:
            image: PIL Image to analyze
            
        Returns:
            Tuple of (ship_detected: bool, detection_info: dict)
        """
        if self.model is None:
            logger.error("Model not loaded")
            return False, {"error": "Model not loaded"}
        
        try:
            # Run inference
            results = self.model(image, conf=self.confidence_threshold, verbose=False, device=self.device)
            
            # Process results
            detections = []
            all_detections = []  # Keep track of ALL detections for debugging
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    detection_obj = {
                        'class_id': cls,
                        'class_name': result.names[cls],
                        'confidence': conf,
                        'bbox': box.xyxy[0].tolist()
                    }
                    
                    all_detections.append(detection_obj)
                    
                    # Check if detected class is in target classes
                    if cls in self.target_classes:
                        detections.append(detection_obj)
            
            ship_detected = len(detections) > 0
            
            # Log what was detected for debugging
            if all_detections:
                # logger.info(f"Detected {len(all_detections)} objects. Target classes: {self.target_classes}")
                for det in all_detections:
                    status = "[MATCH]" if det['class_id'] in self.target_classes else "[IGNORE]"
                    # logger.info(f"  - {status} {det['class_name']} (ID: {det['class_id']}): {det['confidence']:.4f}")
            
            # Generate annotated image
            # plot() returns a numpy array in BGR
            annotated_array = results[0].plot() 
            annotated_image = Image.fromarray(annotated_array[..., ::-1])  # BGR to RGB
            
            detection_info = {
                'ship_detected': ship_detected,
                'count': len(detections),
                'detections': detections,
                'all_detections': all_detections,  # Include all for debugging
                'max_confidence': max([d['confidence'] for d in detections]) if detections else 0.0,
                'annotated_image': annotated_image
            }
            
            return ship_detected, detection_info
        
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return False, {"error": str(e)}
    
    def __str__(self) -> str:
        return f"YOLOv8Detector(size={self.model_size}, threshold={self.confidence_threshold}, device={self.device})"