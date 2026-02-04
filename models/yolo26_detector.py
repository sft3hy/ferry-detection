"""
YOLO26 implementation for ship detection
"""
import logging
from .yolov8_detector import YOLOv8Detector

logger = logging.getLogger(__name__)


class YOLO26Detector(YOLOv8Detector):
    """
    YOLO26 detector for ship/boat detection using Ultralytics.
    Inherits from YOLOv8Detector as they share the same Ultralytics API.
    """
    
    def load_model(self) -> None:
        """
        Load YOLO26 model from Ultralytics
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
                # Default naming convention for YOLO26
                model_file = f'yolo26{self.model_size}.pt'

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
                    pass
            print(self.model)
            if hasattr(self.model, 'names'):
                logger.info(f"Model classes: {self.model.names}")

            logger.info(f"Loading YOLO26 model from: {model_file}")
            self.model = YOLO(model_file)
            logger.info(f"Successfully loaded {model_file}")
            
        except ImportError:
            logger.error("Ultralytics not installed. Run: pip install ultralytics")
            raise
        except Exception as e:
            logger.error(f"Failed to load YOLO26 model: {e}")
            raise

    def __str__(self) -> str:
        return f"YOLO26Detector(size={self.model_size}, threshold={self.confidence_threshold}, device={self.device})"
