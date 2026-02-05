"""
Image processing utilities for ferry detection
"""
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
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


def crop_width(image: Image.Image, percentage: float = 0.5) -> Image.Image:
    """
    Crop the image to keep only the left percentage of the width.
    
    Args:
        image: Input PIL Image
        percentage: Float between 0.0 and 1.0 representing the left portion to keep
        
    Returns:
        Cropped PIL Image
    """
    width, height = image.size
    new_width = int(width * percentage)
    return image.crop((0, 0, new_width, height))


def add_padding(image: Image.Image, padding: int = 50, color: tuple = (114, 114, 114)) -> Image.Image:
    """
    Add padding around the image.
    
    Args:
        image: Input PIL Image
        padding: Padding size in pixels
        color: Padding color (default: YOLO gray)
        
    Returns:
        Padded PIL Image
    """
    width, height = image.size
    new_width = width + 2 * padding
    new_height = height + 2 * padding
    
    new_image = Image.new(image.mode, (new_width, new_height), color)
    new_image.paste(image, (padding, padding))
    
    return new_image
    return new_image


def draw_detections(image: Image.Image, detections: list) -> Image.Image:
    """
    Draw bounding boxes and labels on the image.
    
    Args:
        image: Input PIL Image
        detections: List of detection dictionaries (containing 'bbox', 'confidence', 'class_name')
        
    Returns:
        Annotated PIL Image
    """
    annotated_image = image.copy()
    draw = ImageDraw.Draw(annotated_image)
    
    try:
        # Try to load a font, fallback to default
        font = ImageFont.truetype("Arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()
        
    for detection in detections:
        bbox = detection['bbox']
        # bbox is [x1, y1, x2, y2]
        x1, y1, x2, y2 = bbox
        
        # specific color for boats/ferries (e.g., red/orange)
        color = "#FF3838" 
        
        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        
        # Draw label
        label = f"{detection.get('class_name', 'ferry')} {detection.get('confidence', 0.0):.2f}"
        
        # Get text size
        try:
             # PIL < 10.0
            text_size = draw.textsize(label, font=font)
        except AttributeError:
             # PIL >= 10.0
            left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
            text_size = (right - left, bottom - top)
            
        # Draw background for label
        draw.rectangle([x1, y1 - text_size[1] - 4, x1 + text_size[0] + 4, y1], fill=color)
        
        # Draw text
        draw.text((x1 + 2, y1 - text_size[1] - 2), label, fill="white", font=font)
        
    return annotated_image

