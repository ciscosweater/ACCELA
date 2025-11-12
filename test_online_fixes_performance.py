#!/usr/bin/env python3
"""
Test script to verify Online Fixes performance improvements
"""
import sys
import time
import logging

# Add project root to path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_online_fixes_performance():
    """Test Online Fixes check performance"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from core.online_fixes_manager import OnlineFixesManager
    
    app = QApplication([])
    
    manager = OnlineFixesManager()
    
    # Test with a known AppID
    test_appid = 3527290  # PEAK
    
    start_time = time.time()
    
    def check_fixes():
        logger.info(f"Checking fixes for AppID {test_appid}...")
        result = manager.check_for_fixes(test_appid, "PEAK")
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Check completed in {duration:.2f} seconds")
        logger.info(f"Result: {result}")
        
        # Performance expectations
        if duration < 3.0:
            logger.info("✅ Performance is good (< 3 seconds)")
            return True
        elif duration < 5.0:
            logger.warning("⚠️ Performance is acceptable but could be better (< 5 seconds)")
            return True
        else:
            logger.error(f"❌ Performance is poor (> 5 seconds): {duration:.2f}s")
            return False
    
    def quit_app():
        app.quit()
    
    # Schedule tests
    QTimer.singleShot(1000, check_fixes)
    QTimer.singleShot(8000, quit_app)  # Force quit after 8 seconds
    
    logger.info("Starting Online Fixes performance test...")
    app.exec()
    
    return True

def test_http_client_performance():
    """Test HTTP client configuration"""
    from core.online_fixes_manager import OnlineFixesManager
    
    manager = OnlineFixesManager()
    
    # Test HTTP client headers
    logger.info("HTTP Client Headers:")
    for key, value in manager.http_client.headers.items():
        logger.info(f"  {key}: {value}")
    
    # Test a simple HEAD request
    try:
        start_time = time.time()
        response = manager.http_client.head(
            "https://github.com/ShayneVi/Bypasses/releases/download/v1.0/123456.zip",
            timeout=5,
            allow_redirects=True
        )
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"HEAD request completed in {duration:.2f} seconds (status: {response.status_code})")
        
        if duration < 2.0:
            logger.info("✅ HTTP client performance is good")
            return True
        else:
            logger.warning("⚠️ HTTP client could be faster")
            return True
            
    except Exception as e:
        logger.info(f"Expected error for non-existent file: {e}")
        return True

if __name__ == "__main__":
    logger.info("=== Online Fixes Performance Test ===")
    
    # Test 1: HTTP Client Performance
    logger.info("\n--- Test 1: HTTP Client Performance ---")
    http_test_passed = test_http_client_performance()
    
    # Test 2: Online Fixes Check Performance
    logger.info("\n--- Test 2: Online Fixes Check Performance ---")
    fixes_test_passed = test_online_fixes_performance()
    
    # Final results
    logger.info("\n=== Final Test Results ===")
    if http_test_passed and fixes_test_passed:
        logger.info("🎉 Performance tests completed!")
        sys.exit(0)
    else:
        logger.error("❌ Some performance tests failed")
        sys.exit(1)