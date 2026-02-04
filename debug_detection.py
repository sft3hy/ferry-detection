"""
Debug script for ferry detection
Shows what the model is actually detecting and visualizes results
"""
import sys
from pathlib import Path
from datetime import datetime
import logging

from config.settings import DOCKS, DETECTION_CONFIG
from utils.scraper import download_image, save_image
from models.detector_factory import DetectorFactory

# Set up logging to see more details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def debug_detection(dock_name, image_url, detector, save_dir="debug_output"):
    """
    Debug detection on a single dock with detailed output
    """
    print(f"\n{'='*70}")
    print(f"Debugging: {dock_name}")
    print(f"{'='*70}")
    
    # Create output directory
    output_path = Path(save_dir)
    output_path.mkdir(exist_ok=True)
    
    # Download image
    print("📥 Downloading image...")
    image = download_image(image_url)
    if image is None:
        print("❌ Failed to download image")
        return
    
    print(f"✅ Downloaded: {image.size[0]}x{image.size[1]} pixels")
    
    # Save original image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_file = output_path / f"{dock_name.replace(' ', '_')}_{timestamp}_original.jpg"
    save_image(image, str(original_file))
    print(f"💾 Saved original: {original_file}")
    
    # Run detection with very low threshold to see everything
    print(f"\n🔍 Running detection...")
    print(f"   Model: {detector}")
    print(f"   Confidence threshold: {detector.confidence_threshold}")
    
    # First, try with current threshold
    ship_detected, detection_info = detector.detect(image)
    
    print(f"\n📊 Detection Results:")
    print(f"   Ship detected: {ship_detected}")
    print(f"   Number of detections: {detection_info.get('count', 0)}")
    
    if detection_info.get('detections'):
        print(f"\n   Detections found:")
        for i, det in enumerate(detection_info['detections'], 1):
            print(f"   {i}. Class: {det.get('class_name', 'unknown')} (ID: {det.get('class_id')})")
            print(f"      Confidence: {det.get('confidence', 0):.4f}")
            print(f"      BBox: {det.get('bbox', [])}")
    
    # Now run with VERY low threshold to see ALL detections
    print(f"\n🔬 Running with LOW threshold (0.01) to see all possible detections...")
    detector_low = DetectorFactory.create_detector({
        **DETECTION_CONFIG,
        'confidence_threshold': 0.01
    })
    
    ship_detected_low, detection_info_low = detector_low.detect(image)
    
    print(f"\n📊 ALL Detections (confidence > 0.01):")
    print(f"   Total detections: {detection_info_low.get('count', 0)}")
    
    if detection_info_low.get('detections'):
        # Group by class
        by_class = {}
        for det in detection_info_low['detections']:
            class_name = det.get('class_name', 'unknown')
            class_id = det.get('class_id', -1)
            conf = det.get('confidence', 0)
            
            if class_id not in by_class:
                by_class[class_id] = {'name': class_name, 'detections': []}
            by_class[class_id]['detections'].append(conf)
        
        print(f"\n   Detections by class:")
        for class_id, info in sorted(by_class.items()):
            confs = info['detections']
            print(f"   Class {class_id} ({info['name']}): {len(confs)} detection(s)")
            print(f"      Confidences: {[f'{c:.4f}' for c in sorted(confs, reverse=True)[:5]]}")
            print(f"      Max confidence: {max(confs):.4f}")
    else:
        print("   ⚠️  NO detections found even at 0.01 threshold!")
        print("   This means the model doesn't see ANY objects in this image.")
    
    # Try detecting ALL classes (not just boats)
    print(f"\n🌐 Checking for ANY object class (not just boats)...")
    detector_all_classes = DetectorFactory.create_detector({
        **DETECTION_CONFIG,
        'confidence_threshold': 0.01,
        'target_classes': list(range(80))  # All 80 COCO classes
    })
    
    _, detection_info_all = detector_all_classes.detect(image)
    
    if detection_info_all.get('detections'):
        print(f"   Found {len(detection_info_all['detections'])} objects of any class:")
        
        # Show top 10 by confidence
        sorted_dets = sorted(
            detection_info_all['detections'], 
            key=lambda x: x.get('confidence', 0), 
            reverse=True
        )[:10]
        
        for i, det in enumerate(sorted_dets, 1):
            print(f"   {i}. {det.get('class_name', 'unknown')} - {det.get('confidence', 0):.4f}")
    else:
        print("   ⚠️  Still nothing detected!")
    
    # Save annotated image
    try:
        from ultralytics import YOLO
        import cv2
        import numpy as np
        
        # Run YOLO and save annotated result
        model = YOLO(f"yolov8{DETECTION_CONFIG['model_size']}.pt")
        results = model(image, conf=0.01)
        
        # Save annotated image
        annotated_file = output_path / f"{dock_name.replace(' ', '_')}_{timestamp}_annotated.jpg"
        for result in results:
            annotated = result.plot()  # This draws boxes on the image
            cv2.imwrite(str(annotated_file), annotated)
            print(f"\n💾 Saved annotated image: {annotated_file}")
            print(f"   (Open this to see what the model is detecting)")
    except Exception as e:
        print(f"\n⚠️  Could not save annotated image: {e}")
    
    print(f"\n{'='*70}\n")


def main():
    """Main debug function"""
    print("="*70)
    print("Ferry Detection Debugger")
    print("="*70)
    print("\nThis script will:")
    print("1. Download images from both docks")
    print("2. Run detection with multiple thresholds")
    print("3. Show ALL detected objects (not just boats)")
    print("4. Save annotated images showing what's detected")
    print("="*70)
    
    # Create detector
    detector = DetectorFactory.create_detector(DETECTION_CONFIG)
    
    # Debug each dock
    for dock_name, image_url in DOCKS.items():
        debug_detection(dock_name, image_url, detector)
    
    print("\n" + "="*70)
    print("Debug complete! Check the 'debug_output' folder for annotated images.")
    print("="*70)
    
    # Print suggestions
    print("\n💡 Troubleshooting suggestions:")
    print("1. Check the annotated images to see what's being detected")
    print("2. If boats are detected but with low confidence, lower the threshold")
    print("3. If boats aren't detected at all, try a larger model (m, l, or x)")
    print("4. If the camera angle is unusual, you may need a custom-trained model")
    print("5. Run the threshold tuning tool next: python tune_threshold.py")


if __name__ == "__main__":
    main()