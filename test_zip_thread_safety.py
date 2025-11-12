#!/usr/bin/env python3
"""
Test script to verify ZIP processing thread safety
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

def create_test_zip():
    """Create a minimal test ZIP file"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "test.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        # Add a minimal manifest file
        zf.writestr("test_manifest.txt", "test content")
    
    return zip_path

def test_zip_processing():
    """Test ZIP processing with multiple rapid attempts"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from ui.main_window import MainWindow
    
    app = QApplication([])
    
    # Create test ZIP
    zip_path = create_test_zip()
    logger.info(f"Created test ZIP: {zip_path}")
    
    # Create main window
    window = MainWindow()
    window.show()
    
    def process_zip_1():
        logger.info("=== Processing ZIP #1 ===")
        window._start_zip_processing(zip_path)
    
    def process_zip_2():
        logger.info("=== Processing ZIP #2 (should not crash) ===")
        window._start_zip_processing(zip_path)
    
    def process_zip_3():
        logger.info("=== Processing ZIP #3 (should not crash) ===")
        window._start_zip_processing(zip_path)
    
    def close_app():
        logger.info("=== Closing application ===")
        window.close()
        app.quit()
    
    # Schedule rapid ZIP processing
    QTimer.singleShot(1000, process_zip_1)
    QTimer.singleShot(2000, process_zip_2)  # This used to crash
    QTimer.singleShot(3000, process_zip_3)  # This used to crash
    QTimer.singleShot(5000, close_app)
    
    logger.info("Starting ZIP processing test...")
    app.exec()
    
    # Cleanup
    os.unlink(zip_path)
    os.rmdir(os.path.dirname(zip_path))
    
    logger.info("✅ Test completed without crashes!")

if __name__ == "__main__":
    test_zip_processing()