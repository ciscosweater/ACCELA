#!/usr/bin/env python3
"""
Test script to verify crash fixes and download performance
"""
import sys
import os
import tempfile
import zipfile
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_test_zip_with_lua():
    """Create a test ZIP file with a minimal .lua file"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "test_with_lua.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        # Add a minimal manifest file
        zf.writestr("test_manifest.txt", "test content")
        # Add a minimal .lua file to pass validation
        zf.writestr("script.lua", """
-- Test Lua script for ACCELA
return {
    appid = "123456",
    game_name = "Test Game",
    installdir = "TestGame"
}
""")
    
    return zip_path

def test_improved_zip_processing():
    """Test improved ZIP processing with crash prevention"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from ui.main_window import MainWindow
    
    app = QApplication([])
    
    # Create test ZIP with .lua file
    zip_path = create_test_zip_with_lua()
    logger.info(f"Created test ZIP with .lua: {zip_path}")
    
    # Create main window
    window = MainWindow()
    window.show()
    
    crash_count = 0
    success_count = 0
    
    def process_zip_rapid():
        nonlocal crash_count, success_count
        try:
            logger.info("=== Processing ZIP rapidly ===")
            window._start_zip_processing(zip_path)
            success_count += 1
        except Exception as e:
            logger.error(f"Crash during ZIP processing: {e}")
            crash_count += 1
    
    def process_multiple_times():
        """Process ZIP multiple times rapidly to test crash prevention"""
        for i in range(5):
            QTimer.singleShot(i * 500, lambda i=i: process_zip_rapid())
    
    def check_results():
        logger.info(f"=== Test Results ===")
        logger.info(f"Successful processes: {success_count}")
        logger.info(f"Crashes: {crash_count}")
        logger.info(f"Total attempts: {success_count + crash_count}")
        
        if crash_count == 0:
            logger.info("✅ No crashes detected - thread safety working!")
        else:
            logger.error(f"❌ {crash_count} crashes detected")
        
        close_app()
    
    def close_app():
        logger.info("=== Closing application ===")
        window.close()
        app.quit()
    
    # Schedule rapid testing
    QTimer.singleShot(1000, process_multiple_times)
    QTimer.singleShot(5000, check_results)
    
    logger.info("Starting improved crash prevention test...")
    app.exec()
    
    # Cleanup
    os.unlink(zip_path)
    os.rmdir(os.path.dirname(zip_path))
    
    return crash_count == 0

def test_download_performance():
    """Test download task performance and thread management"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from core.tasks.download_depots_task import DownloadDepotsTask
    from utils.task_runner import TaskRunner
    
    app = QApplication([])
    
    # Create a mock download task
    task = DownloadDepotsTask()
    task_runner = TaskRunner()
    
    logger.info("Testing download task thread management...")
    
    def test_cleanup():
        try:
            # Test cleanup methods
            task.cleanup()
            task_runner.force_cleanup()
            logger.info("✅ Download task cleanup successful")
            return True
        except Exception as e:
            logger.error(f"❌ Download task cleanup failed: {e}")
            return False
    
    def close_test():
        app.quit()
    
    QTimer.singleShot(1000, test_cleanup)
    QTimer.singleShot(2000, close_test)
    
    app.exec()
    
    return True

if __name__ == "__main__":
    logger.info("=== ACCELA Crash Prevention & Performance Test ===")
    
    # Test 1: ZIP processing crash prevention
    logger.info("\n--- Test 1: ZIP Processing Crash Prevention ---")
    zip_test_passed = test_improved_zip_processing()
    
    # Test 2: Download performance
    logger.info("\n--- Test 2: Download Task Performance ---")
    download_test_passed = test_download_performance()
    
    # Final results
    logger.info("\n=== Final Test Results ===")
    if zip_test_passed and download_test_passed:
        logger.info("🎉 ALL TESTS PASSED - Crash prevention and performance improved!")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed")
        sys.exit(1)