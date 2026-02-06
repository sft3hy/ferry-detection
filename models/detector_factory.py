"""
Detector factory for creating detection models
"""
from models.base_detector import BaseDetector
from models.yolov8_detector import YOLOv8Detector
from models.yolo26_detector import YOLO26Detector
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DetectorFactory:
    """
    Factory class for creating detector instances
    Makes it easy to switch between different detection models
    """
    
    @staticmethod
    def create_detector(config: Dict[str, Any]) -> BaseDetector:
        """
        Create a detector based on configuration
        
        Args:
            config: Detection configuration dictionary
            
        Returns:
            BaseDetector instance
            
        Raises:
            ValueError: If model type is not supported
        """
        model_type = config.get('model_type', 'yolov8').lower()
        confidence = config.get('confidence_threshold', 0.25)
        
        if model_type == 'yolov8':
            model_size = config.get('model_size', 'm')
            model_path = config.get('model_path')
            target_classes = config.get('target_classes', [8])
            
            logger.info(f"Creating YOLOv8 detector (path={model_path or 'default'}, size={model_size})")
            return YOLOv8Detector(
                model_path=model_path,
                model_size=model_size,
                confidence_threshold=confidence,
                target_classes=target_classes
            )
            
        elif model_type == 'yolo26':
            model_size = config.get('model_size', 'x')
            model_path = config.get('model_path')
            target_classes = config.get('target_classes', [8])
            
            logger.info(f"Creating YOLO26 detector (path={model_path or 'default'}, size={model_size})")
            return YOLO26Detector(
                model_path=model_path,
                model_size=model_size,
                confidence_threshold=confidence,
                target_classes=target_classes
            )
        
        elif model_type == 'custom':
            # You can add custom model implementations here
            custom_path = config.get('custom_model_path')
            if not custom_path:
                raise ValueError("Custom model path must be specified for 'custom' model type")
            
            # Example: return CustomDetector(custom_path, confidence)
            raise NotImplementedError("Custom detector not implemented yet")
        
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    @staticmethod
    def list_available_models() -> list:
        """
        List all available detector types
        
        Returns:
            List of available model type strings
        """
        return ['yolov8', 'yolo26', 'custom']