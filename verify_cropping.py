from utils.image_processing import crop_width
from PIL import Image

def test_cropping():
    # Create a 100x100 dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    
    # Test 50% crop
    cropped_50 = crop_width(img, 0.5)
    print(f"Original size: {img.size}")
    print(f"50% crop size: {cropped_50.size}")
    assert cropped_50.size == (50, 100)
    
    # Test 65% crop
    cropped_65 = crop_width(img, 0.65)
    print(f"65% crop size: {cropped_65.size}")
    assert cropped_65.size == (65, 100)
    
    # Test no crop (100%) - though specific function handles this via logic in monitor.py, 
    # crop_width(1.0) should work too
    cropped_100 = crop_width(img, 1.0)
    print(f"100% crop size: {cropped_100.size}")
    assert cropped_100.size == (100, 100)

if __name__ == "__main__":
    test_cropping()
