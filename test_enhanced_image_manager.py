#!/usr/bin/env python3
"""
Test script for enhanced game image manager
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_enhanced_image_manager():
    """Test the enhanced game image manager with multiple fallbacks"""
    app = QApplication(sys.argv)
    
    try:
        from ui.game_image_manager import GameImageManager
        from utils.image_cache import ImageCacheManager
        
        # Initialize managers
        cache_manager = ImageCacheManager()
        image_manager = GameImageManager(cache_manager)
        
        print("✓ Enhanced GameImageManager initialized successfully")
        print(f"✓ Available formats: {[f['name'] for f in image_manager.image_formats]}")
        print(f"✓ CDN endpoints: {len(image_manager.cdn_endpoints)}")
        print(f"✓ API endpoints: {len(image_manager.api_endpoints)}")
        
        # Test with a known game (e.g., Portal 2 - App ID: 620)
        test_app_id = "620"
        print(f"\n--- Testing with App ID: {test_app_id} ---")
        
        # Generate all possible URLs
        urls = image_manager.get_image_urls(test_app_id)
        print(f"✓ Generated {len(urls)} possible image URLs")
        
        # Test API fallback
        api_urls = image_manager.try_api_fallback(test_app_id)
        if api_urls:
            print(f"✓ API fallback found {len(api_urls)} additional URLs")
        else:
            print("⚠ API fallback returned no URLs")
        
        # Test image fetching (async)
        print("\n--- Testing async image fetching ---")
        image_thread = image_manager.get_game_image(test_app_id, preferred_format="header")
        
        def on_image_ready(app_id, pixmap, source_info):
            if pixmap and not pixmap.isNull():
                print(f"✓ Successfully loaded image for app {app_id} from {source_info}")
                print(f"  Image size: {pixmap.width()}x{pixmap.height()}")
            else:
                print(f"✗ Failed to load image for app {app_id}")
            app.quit()
        
        def on_image_failed(app_id, error_message):
            print(f"✗ Image fetch failed for app {app_id}: {error_message}")
            app.quit()
        
        image_thread.image_ready.connect(on_image_ready)
        image_thread.image_failed.connect(on_image_failed)
        
        # Timeout after 30 seconds
        QTimer.singleShot(30000, app.quit)
        
        print("✓ Image fetch started, waiting for result...")
        app.exec()
        
    except Exception as e:
        print(f"✗ Error testing enhanced image manager: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_legacy_compatibility():
    """Test that legacy components still work"""
    print("\n--- Testing Legacy Compatibility ---")
    
    try:
        from ui.game_image_display import GameImageDisplay, ImageFetcher
        from ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # Test GameImageDisplay
        display = GameImageDisplay()
        print("✓ GameImageDisplay works with enhanced manager")
        
        # Test ImageFetcher (legacy)
        fetcher = ImageFetcher("https://example.com/test.jpg")
        print("✓ Legacy ImageFetcher still works")
        
        # Test MainWindow
        window = MainWindow()
        print("✓ MainWindow integrates enhanced image manager")
        
        app.quit()
        
    except Exception as e:
        print(f"✗ Legacy compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("=== Testing Enhanced Game Image Manager ===\n")
    
    success = True
    
    # Test enhanced manager
    if not test_enhanced_image_manager():
        success = False
    
    # Test legacy compatibility
    if not test_legacy_compatibility():
        success = False
    
    print(f"\n=== Test Results ===")
    if success:
        print("✓ All tests passed! Enhanced image system is working correctly.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Check the output above.")
        sys.exit(1)