"""
Image processing utilities for ferry detection
"""
import cv2
import numpy as np
from PIL import Image, ImageOps
import logging

logger = logging.getLogger(__name__)

def optimize_image(image: Image.Image, target_size: int = 640) -> Image.Image:
    """
    Optimize image for YOLOv8 inference:
    1. Auto-orient (fix EXIF)
    2. Resize while maintaining aspect ratio
    3. Letterbox (pad) to square
    
    Args:
        image: Input PIL Image
        target_size: Target size (e.g., 640 or 1280)
        
    Returns:
        Optimized PIL Image (padded to square)
    """
    try:
        # 1. Auto-orient
        image = ImageOps.exif_transpose(image)
        
        # 2. Resize maintaining aspect ratio
        original_width, original_height = image.size
        ratio = min(target_size / original_width, target_size / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # Resize using LANCZOS for high quality
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 3. Letterbox (pad to square)
        # Create a new square image with 114 gray background (standard for YOLO)
        new_image = Image.new("RGB", (target_size, target_size), (114, 114, 114))
        
        # Paste resized image in center
        pad_w = (target_size - new_width) // 2
        pad_h = (target_size - new_height) // 2
        new_image.paste(image, (pad_w, pad_h))
        
        return new_image
        
    except Exception as e:
        logger.error(f"Error optimizing image: {e}")
        # Return original image if optimization fails, potentially resized to ensure not too huge
        return image

