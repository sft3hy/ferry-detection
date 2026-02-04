"""
Quick test script to verify ferry monitor setup
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all required packages are installed"""
    print("Testing package imports...")
    
    required_packages = {
        'requests': 'requests',
        'PIL': 'pillow',
        'cv2': 'opencv-python',
        'ultralytics': 'ultralytics',
        'schedule': 'schedule'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ All packages installed!")
    return True


def test_config():
    """Test that configuration is valid"""
    print("\nTesting configuration...")
    
    try:
        from config.settings import DOCKS, DETECTION_CONFIG, CHECK_INTERVAL_SECONDS
        
        print(f"  ✓ Found {len(DOCKS)} docks configured")
        print(f"  ✓ Model type: {DETECTION_CONFIG['model_type']}")
        print(f"  ✓ Check interval: {CHECK_INTERVAL_SECONDS}s")
        print("\n✅ Configuration valid!")
        return True
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False


def test_image_download():
    """Test downloading an image from one dock"""
    print("\nTesting image download...")
    
    try:
        from config.settings import DOCKS
        from utils.scraper import download_image
        
        # Test first dock
        dock_name, url = list(DOCKS.items())[0]
        print(f"  Downloading from {dock_name}...")
        
        image = download_image(url, timeout=10)
        if image:
            print(f"  ✓ Downloaded {image.size[0]}x{image.size[1]} image")
            print("\n✅ Image download working!")
            return True
        else:
            print("  ✗ Failed to download image")
            print("\n❌ Image download failed!")
            return False
    except Exception as e:
        print(f"\n❌ Image download error: {e}")
        return False


def test_model_loading():
    """Test loading the detection model"""
    print("\nTesting model loading...")
    
    try:
        from models.detector_factory import DetectorFactory
        from config.settings import DETECTION_CONFIG
        
        print("  Loading detector (this may take a moment)...")
        detector = DetectorFactory.create_detector(DETECTION_CONFIG)
        print(f"  ✓ Loaded: {detector}")
        print("\n✅ Model loading successful!")
        return True
    except Exception as e:
        print(f"\n❌ Model loading error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Ferry Monitor - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("Image Download", test_image_download),
        ("Model Loading", test_model_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("\n🎉 All tests passed! Ready to run monitor.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running.")
        return 1


if __name__ == "__main__":
    sys.exit(main())