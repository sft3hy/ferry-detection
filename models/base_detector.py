"""
Base detector class for ship detection models
"""
from abc import ABC, abstractmethod
from PIL import Image
from typing import Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseDetector(ABC):
    """
    Abstract base class for ship detection models
    Implement this interface to add new detection models
    """
    
    def __init__(self, confidence_threshold: float = 0.25):
        """
        Initialize detector
        
        Args:
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        logger.info(f"Initialized {self.__class__.__name__} with confidence threshold {confidence_threshold}")
    
    @abstractmethod
    def load_model(self) -> None:
        """
        Load the detection model
        """
        pass
    
    @abstractmethod
    def detect(self, image: Image.Image) -> Tuple[bool, Dict[str, Any]]:
        """
        Detect ships in an image
        
        Args:
            image: PIL Image to analyze
            
        Returns:
            Tuple of (ship_detected: bool, detection_info: dict)
            detection_info should contain details like confidence, count, etc.
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(threshold={self.confidence_threshold})"