"""
Ferry Monitor - Main monitoring script
Checks ferry docks for ship presence every minute
"""
from requests import session
import logging
import schedule
import time
from datetime import datetime
from pathlib import Path
from utils.cs_helpers import send_public_message
import time

from config.settings import (
    DOCKS, DETECTION_CONFIG, CHECK_INTERVAL_SECONDS,
    LOG_DETECTIONS, LOG_FILE, SAVE_IMAGES, SAVE_ALL_CAPTURES, SAVE_DIR,
    DOCK_SCHEDULES, TIMEZONE
)
from utils.scraper import download_image, save_image
from utils.image_processing import optimize_image, crop_width, add_padding, draw_detections
from models.detector_factory import DetectorFactory
from dateutil import tz


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE) if LOG_DETECTIONS else logging.NullHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class FerryMonitor:
    """
    Main ferry monitoring class
    """
    
    def __init__(self):
        """Initialize the ferry monitor"""
        logger.info("Initializing Ferry Monitor")
        
        
        # Create detector
        self.detector = DetectorFactory.create_detector(DETECTION_CONFIG)
        logger.info(f"Using detector: {self.detector}")
        
        # Create save directory if needed
        if SAVE_IMAGES:
            Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)
            logger.info(f"Image saving enabled: {SAVE_DIR}")
        
        logger.info(f"Monitoring {len(DOCKS)} docks")
        for dock_name in DOCKS.keys():
            logger.info(f"  - {dock_name}")
        
        logger.info(f"Check interval: {CHECK_INTERVAL_SECONDS} seconds")
        
    
    def is_dock_active(self, dock_name: str) -> bool:
        """
        Check if the dock is currently active based on the schedule
        """
        if dock_name not in DOCK_SCHEDULES:
            return True
            
        schedule = DOCK_SCHEDULES[dock_name]
        
        # Get current time in target timezone
        zone = tz.gettz(TIMEZONE)
        now = datetime.now(zone)
        
        # Parse schedule times
        start_str = schedule['start']
        end_str = schedule['end']
        
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()
        
        # Check if current time is within range
        # Handle overnight schedules if needed (though not required for current request)
        if start_time <= end_time:
            return start_time <= now.time() <= end_time
        else:
            # Crosses midnight
            return now.time() >= start_time or now.time() <= end_time
    
    def check_dock(self, dock_name: str, image_url: str) -> None:
        """
        Check a single dock for ship presence
        
        Args:
            dock_name: Name of the dock
            image_url: URL of the dock camera image
        """
        logger.info(f"Checking {dock_name}...")
        
        if not self.is_dock_active(dock_name):
            logger.info(f"{dock_name} is currently inactive (outside schedule)")
            print(f"💤 {dock_name}: Inactive (Sleep Mode)")
            return

        # Download image
        image = download_image(image_url)
        if image is None:
            logger.error(f"Failed to download image for {dock_name}")
            print(f"❌ {dock_name}: Failed to retrieve image")
            return

        # Apply cropping based on dock
        if dock_name == "Anderson Island Dock":
            # Keep left 65% for Anderson Island
            image = crop_width(image, percentage=0.65)
        elif dock_name == "Steilacoom Dock":
            # No cropping for Steilacoom
            pass
        else:
            # Default behavior (if any other docks are added): keep left 50%
            image = crop_width(image, percentage=0.5)
        
        # Add padding to prevent edge detection issues
        image = add_padding(image)
            
        # logger.info(f"Image downloaded successfully (Size: {image.size})")
        
        # Apply image optimization if enabled
        if DETECTION_CONFIG.get('image_optimization', False):
            logger.info("Applying image optimization...")
            target_size = DETECTION_CONFIG.get('imgsz', 640)
            image = optimize_image(image, target_size=target_size)

        # Detect ships
        ship_detected, detection_info = self.detector.detect(image)
        
        # Filter detections by size
        min_width = DETECTION_CONFIG.get('min_bbox_width', 0)
        filtered_detections = []
        
        if ship_detected:
            initial_count = len(detection_info.get('detections', []))
            for detection in detection_info.get('detections', []):
                bbox = detection['bbox']
                # bbox format is usually [x1, y1, x2, y2]
                width = abs(bbox[2] - bbox[0])
                height = abs(bbox[3] - bbox[1])
                
                if width >= min_width:
                    filtered_detections.append(detection)
                else:
                    if LOG_DETECTIONS:
                        logger.info(f"Filtered out small detection at {dock_name}: width={width:.1f}px (threshold={min_width}px)")
            
            # Update detection info
            detection_info['detections'] = filtered_detections
            detection_info['count'] = len(filtered_detections)
            ship_detected = len(filtered_detections) > 0
            
            if initial_count > 0 and len(filtered_detections) == 0:
                 logger.info(f"All detections filtered out for {dock_name} due to size threshold")

        
        # Format output
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "🚢 FERRY PRESENT" if ship_detected else "❌ NO FERRY"
        
        # Print result
        print(f"{status} at {dock_name} ({timestamp})")

        # Define docks with their coordinates
        docks_info = {
            "Steilacoom Dock": {
                "lat": 47.172912, 
                "lon": -122.603891,
                "mgrs": "10TET3001724455"
            },
            "Anderson Island Dock": {
                "lat": 47.178611, 
                "lon": -122.677250,
                "mgrs": "10TET2445525063"
            }
        }
        
        display_name = dock_name
        if dock_name in docks_info:
            info = docks_info[dock_name]
            lat = info['lat']
            lon = info['lon']
            mgrs_coord = info['mgrs']
            
            # user format: 47.172912N,122.603891W
            lat_str = f"{abs(lat):.6f}{'N' if lat >= 0 else 'S'}"
            lon_str = f"{abs(lon):.6f}{'E' if lon >= 0 else 'W'}"
            
            display_name = f"{dock_name} ({lat_str},{lon_str} | {mgrs_coord})"

        cs_message_text = f"{display_name}: {status}"
        send_public_message(message_text=cs_message_text, roomName="pierce_county_ferry_detector")

        
        # Save image if configured (ALWAYS if SAVE_IMAGES is True)
        if SAVE_IMAGES:
            filename = f"{dock_name.replace(' ', '_')}_{timestamp.replace(':', '-').replace(' ', '_')}.jpg"
            filepath = Path(SAVE_DIR) / filename
            if save_image(image, str(filepath)):
                pass

        if ship_detected:
            count = detection_info.get('count', 0)
            max_conf = detection_info.get('max_confidence', 0.0)
            # print(f"   └─ Detected: {count} ship(s) | Confidence: {max_conf:.2f}")
            
            
            # Log detections
            if LOG_DETECTIONS:
                logger.info(f"{dock_name}: SHIP DETECTED - {detection_info}")
            
            # Generate annotated image with filtered detections
            if SAVE_IMAGES:
                annotated_image = draw_detections(image, filtered_detections)
                annotated_filename = f"{dock_name.replace(' ', '_')}_{timestamp.replace(':', '-').replace(' ', '_')}_annotated.jpg"
                annotated_filepath = Path(SAVE_DIR) / annotated_filename
                if save_image(annotated_image, str(annotated_filepath)):
                    pass
                        # logger.info(f"Saved annotated detection image: {annotated_filepath}")
        else:
            if LOG_DETECTIONS:
                logger.info(f"{dock_name}: No ship detected")
            
            # Debug: Save all captures if enabled
            if SAVE_ALL_CAPTURES:
                filename = f"DEBUG_{dock_name.replace(' ', '_')}_{timestamp.replace(':', '-').replace(' ', '_')}.jpg"
                filepath = Path(SAVE_DIR) / filename
                if save_image(image, str(filepath)):
                    # logger.info(f"Saved debug image: {filepath}")
                    pass
                    
                # Save annotated version if available
                if 'annotated_image' in detection_info:
                    annotated_filename = f"DEBUG_{dock_name.replace(' ', '_')}_{timestamp.replace(':', '-').replace(' ', '_')}_annotated.jpg"
                    annotated_filepath = Path(SAVE_DIR) / annotated_filename
                    if save_image(detection_info['annotated_image'], str(annotated_filepath)):
                        # logger.info(f"Saved annotated debug image: {annotated_filepath}")
                        pass
    
    def check_all_docks(self) -> None:
        """
        Check all configured docks
        """
        print("\n" + "=" * 60)
        print(f"Ferry Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        for dock_name, image_url in DOCKS.items():
            self.check_dock(dock_name, image_url)
        
        print("=" * 60 + "\n")
    
    def run(self) -> None:
        """
        Run the monitoring loop
        """
        # Run once immediately
        self.check_all_docks()
        
        # Schedule regular checks
        schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(self.check_all_docks)
        
        logger.info("Monitor started. Press Ctrl+C to stop.")
        print(f"🔄 Monitoring active - checking every {CHECK_INTERVAL_SECONDS} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            # logger.info("Monitor stopped by user")
            print("\n👋 Monitor stopped")


def main():
    """Main entry point"""
    # time.sleep(300)
    try:
        monitor = FerryMonitor()
        monitor.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())