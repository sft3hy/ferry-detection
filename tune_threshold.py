"""
Interactive threshold tuning tool for ferry detection
Allows you to test different thresholds on saved images
"""
import sys
from pathlib import Path
from PIL import Image
import logging

from models.detector_factory import DetectorFactory
from config.settings import DETECTION_CONFIG

logging.basicConfig(level=logging.WARNING)  # Reduce noise


def load_images_from_directory(directory):
    """Load all images from a directory"""
    image_dir = Path(directory)
    
    if not image_dir.exists():
        print(f"❌ Directory not found: {directory}")
        return []
    
    # Common image extensions
    extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    
    images = []
    for ext in extensions:
        images.extend(image_dir.glob(f'*{ext}'))
        images.extend(image_dir.glob(f'*{ext.upper()}'))
    
    return sorted(images)


def test_threshold(image_path, threshold, model_size='n', target_classes=None, show_all_classes=False):
    """
    Test detection with a specific threshold
    """
    if target_classes is None:
        target_classes = [8]  # Default to boat class
    
    # Load image
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"❌ Error loading {image_path}: {e}")
        return None
    
    # Create detector with specified threshold
    config = {
        'model_type': 'yolov8',
        'model_size': model_size,
        'confidence_threshold': threshold,
        'target_classes': target_classes if not show_all_classes else list(range(80))
    }
    
    detector = DetectorFactory.create_detector(config)
    
    # Run detection
    ship_detected, detection_info = detector.detect(image)
    
    return {
        'ship_detected': ship_detected,
        'detection_info': detection_info,
        'image_path': image_path
    }


def format_detection_result(result, threshold):
    """Format detection result for display"""
    if result is None:
        return "Error processing image"
    
    info = result['detection_info']
    count = info.get('count', 0)
    max_conf = info.get('max_confidence', 0.0)
    
    status = "🚢 SHIP" if result['ship_detected'] else "⚓ NO SHIP"
    
    output = f"{status} | Count: {count} | Max Conf: {max_conf:.4f}"
    
    if info.get('detections'):
        output += "\n      Detections:"
        for i, det in enumerate(info['detections'][:5], 1):  # Show top 5
            class_name = det.get('class_name', 'unknown')
            conf = det.get('confidence', 0)
            output += f"\n        {i}. {class_name}: {conf:.4f}"
        
        if len(info['detections']) > 5:
            output += f"\n        ... and {len(info['detections']) - 5} more"
    
    return output


def interactive_tuning(images, initial_threshold=0.25):
    """
    Interactive tuning mode
    """
    current_threshold = initial_threshold
    current_model = 'n'
    show_all = False
    
    print("\n" + "="*70)
    print("Interactive Threshold Tuning")
    print("="*70)
    print(f"Loaded {len(images)} images")
    print("\nCommands:")
    print("  t <value>  - Set threshold (e.g., 't 0.3')")
    print("  m <size>   - Change model size: n/s/m/l/x (e.g., 'm s')")
    print("  a          - Toggle showing all classes (not just boats)")
    print("  r          - Re-run with current settings")
    print("  s          - Show current settings")
    print("  q          - Quit")
    print("="*70)
    
    while True:
        print(f"\n📊 Current settings:")
        print(f"   Threshold: {current_threshold}")
        print(f"   Model: YOLOv8-{current_model}")
        print(f"   Detect all classes: {show_all}")
        print(f"   Target classes: {'All (0-79)' if show_all else '8 (boat)'}")
        
        cmd = input(f"\nEnter command (or press Enter to run): ").strip().lower()
        
        if cmd == 'q':
            print("👋 Exiting...")
            break
        
        elif cmd.startswith('t '):
            try:
                current_threshold = float(cmd.split()[1])
                print(f"✅ Threshold set to {current_threshold}")
            except (ValueError, IndexError):
                print("❌ Invalid threshold. Use: t 0.25")
            continue
        
        elif cmd.startswith('m '):
            try:
                size = cmd.split()[1].lower()
                if size in ['n', 's', 'm', 'l', 'x']:
                    current_model = size
                    print(f"✅ Model set to YOLOv8-{current_model}")
                else:
                    print("❌ Invalid model size. Use: n, s, m, l, or x")
            except IndexError:
                print("❌ Invalid command. Use: m s")
            continue
        
        elif cmd == 'a':
            show_all = not show_all
            print(f"✅ Showing all classes: {show_all}")
            continue
        
        elif cmd == 's':
            continue  # Settings already displayed above
        
        elif cmd != '' and cmd != 'r':
            print("❌ Unknown command")
            continue
        
        # Run detection
        print(f"\n🔍 Running detection on {len(images)} images...")
        print("-"*70)
        
        results = []
        for i, img_path in enumerate(images, 1):
            print(f"\n[{i}/{len(images)}] {img_path.name}")
            print(f"   Threshold: {current_threshold}")
            
            result = test_threshold(
                img_path, 
                current_threshold, 
                current_model,
                show_all_classes=show_all
            )
            
            print(f"   {format_detection_result(result, current_threshold)}")
            results.append(result)
        
        # Summary
        print("\n" + "-"*70)
        print("📈 Summary:")
        ships_detected = sum(1 for r in results if r and r['ship_detected'])
        print(f"   Images with ships: {ships_detected}/{len(results)}")
        
        if results:
            all_confs = []
            for r in results:
                if r and r['detection_info'].get('detections'):
                    all_confs.extend([d['confidence'] for d in r['detection_info']['detections']])
            
            if all_confs:
                print(f"   Confidence range: {min(all_confs):.4f} - {max(all_confs):.4f}")
                print(f"   Average confidence: {sum(all_confs)/len(all_confs):.4f}")


def batch_test_thresholds(images, thresholds=None, model_size='n'):
    """
    Test multiple thresholds and show results
    """
    if thresholds is None:
        thresholds = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
    
    print("\n" + "="*70)
    print("Batch Threshold Testing")
    print("="*70)
    print(f"Testing {len(thresholds)} thresholds on {len(images)} images")
    print(f"Thresholds: {thresholds}")
    print("="*70)
    
    # Store results
    threshold_results = {t: [] for t in thresholds}
    
    for img_path in images:
        print(f"\n📷 {img_path.name}")
        
        for threshold in thresholds:
            result = test_threshold(img_path, threshold, model_size)
            threshold_results[threshold].append(result)
            
            if result:
                status = "🚢" if result['ship_detected'] else "⚓"
                count = result['detection_info'].get('count', 0)
                max_conf = result['detection_info'].get('max_confidence', 0.0)
                print(f"   {threshold:.2f}: {status} (count={count}, conf={max_conf:.4f})")
    
    # Summary table
    print("\n" + "="*70)
    print("Summary Table")
    print("="*70)
    print(f"{'Threshold':<12} {'Ships Detected':<18} {'Total Detections':<18} {'Avg Confidence'}")
    print("-"*70)
    
    for threshold in thresholds:
        results = threshold_results[threshold]
        ships_detected = sum(1 for r in results if r and r['ship_detected'])
        total_detections = sum(r['detection_info'].get('count', 0) for r in results if r)
        
        all_confs = []
        for r in results:
            if r and r['detection_info'].get('detections'):
                all_confs.extend([d['confidence'] for d in r['detection_info']['detections']])
        
        avg_conf = sum(all_confs) / len(all_confs) if all_confs else 0.0
        
        print(f"{threshold:<12.2f} {ships_detected}/{len(images):<15} {total_detections:<18} {avg_conf:.4f}")
    
    print("="*70)
    
    # Recommendation
    print("\n💡 Recommendation:")
    best_threshold = None
    best_count = 0
    
    for threshold in thresholds:
        results = threshold_results[threshold]
        ships_detected = sum(1 for r in results if r and r['ship_detected'])
        
        if ships_detected > best_count:
            best_count = ships_detected
            best_threshold = threshold
    
    if best_threshold:
        print(f"   Best threshold for detection: {best_threshold:.2f}")
        print(f"   (Detected ships in {best_count}/{len(images)} images)")
        print(f"\n   Update config/settings.py:")
        print(f"   'confidence_threshold': {best_threshold},")


def main():
    """Main function"""
    print("="*70)
    print("Ferry Detection Threshold Tuner")
    print("="*70)
    
    # Check for command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Tune detection threshold')
    parser.add_argument('directory', nargs='?', default='detected_images',
                       help='Directory containing images (default: detected_images)')
    parser.add_argument('--batch', action='store_true',
                       help='Run batch test with multiple thresholds')
    parser.add_argument('--thresholds', type=str,
                       help='Comma-separated thresholds for batch mode (e.g., 0.1,0.2,0.3)')
    parser.add_argument('--model', type=str, default='n', choices=['n', 's', 'm', 'l', 'x'],
                       help='YOLO model size (default: n)')
    
    args = parser.parse_args()
    
    # Load images
    images = load_images_from_directory(args.directory)
    
    if not images:
        print(f"\n❌ No images found in '{args.directory}'")
        print(f"\nTips:")
        print(f"1. Make sure you have images saved in the directory")
        print(f"2. Run 'python debug_detection.py' first to save some images")
        print(f"3. Enable SAVE_IMAGES in config/settings.py and run monitor.py")
        return 1
    
    print(f"\n✅ Found {len(images)} images in '{args.directory}'")
    
    if args.batch:
        # Batch mode
        if args.thresholds:
            thresholds = [float(t.strip()) for t in args.thresholds.split(',')]
        else:
            thresholds = None  # Use defaults
        
        batch_test_thresholds(images, thresholds, args.model)
    else:
        # Interactive mode
        interactive_tuning(images)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())