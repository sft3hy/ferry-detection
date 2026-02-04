"""
Image scraping utilities for ferry monitoring
"""
import requests
from PIL import Image
from io import BytesIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def download_image(url: str, timeout: int = 10) -> Optional[Image.Image]:
    """
    Download an image from a URL and return as PIL Image
    
    Args:
        url: Image URL to download
        timeout: Request timeout in seconds
        
    Returns:
        PIL Image object or None if failed
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        return image
    
    except requests.RequestException as e:
        logger.error(f"Failed to download image from {url}: {e}")
        return None
    
    except Exception as e:
        logger.error(f"Failed to process image from {url}: {e}")
        return None


def save_image(image: Image.Image, filepath: str) -> bool:
    """
    Save PIL Image to file
    
    Args:
        image: PIL Image object
        filepath: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        image.save(filepath)
        return True
    except Exception as e:
        logger.error(f"Failed to save image to {filepath}: {e}")
        return False