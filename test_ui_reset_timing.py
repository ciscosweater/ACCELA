#!/usr/bin/env python3
"""
Test script to verify UI reset timing fix with Online Fixes dialog.
This simulates the scenario where UI reset timer conflicts with fix dialogs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QFont
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MockMainWindow(QMainWindow):
    """Mock main window to test UI reset timing logic"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UI Reset Timing Test")
        self.setGeometry(100, 100, 600, 400)
        
        # Initialize flags
        self._fix_dialog_open = False
        self._ui_reset_cancelled = False
        self._ui_reset_timer = None
        
        # Setup UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("Ready to test UI reset timing")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Test buttons
        test_btn = QPushButton("Simulate Download Completion")
        test_btn.clicked.connect(self._simulate_download_completion)
        layout.addWidget(test_btn)
        
        fix_btn = QPushButton("Simulate Fix Dialog")
        fix_btn.clicked.connect(self._simulate_fix_dialog)
        layout.addWidget(fix_btn)
        
        reset_btn = QPushButton("Manual UI Reset")
        reset_btn.clicked.connect(self._safe_reset_ui_state)
        layout.addWidget(reset_btn)
        
        # Apply font
        font = QFont("Arial", 10)
        self.setFont(font)
        
    def _simulate_download_completion(self):
        """Simulate download completion with UI reset timer"""
        self.status_label.setText("Download completed! UI reset timer started (8 seconds)...")
        logger.info("Download completed - UI reset timer started")
        
        # Reset flags
        self._ui_reset_cancelled = False
        self._fix_dialog_open = False
        
        # Start UI reset timer (8 seconds as in the fix)
        self._ui_reset_timer = QTimer.singleShot(8000, self._safe_reset_ui_state)
        logger.debug("UI reset timer scheduled for 8 seconds")
        
    def _simulate_fix_dialog(self):
        """Simulate fix dialog opening"""
        self.status_label.setText("Fix dialog opened! UI reset timer cancelled.")
        logger.info("Fix dialog opened - cancelling UI reset timer")
        
        # Cancel UI reset timer (simulate fix availability)
        self._ui_reset_cancelled = True
        self._fix_dialog_open = True
        
        # Simulate fix dialog closing after 3 seconds
        QTimer.singleShot(3000, self._close_fix_dialog)
        
    def _close_fix_dialog(self):
        """Simulate fix dialog closing"""
        self.status_label.setText("Fix dialog closed. UI reset scheduled for 2 seconds...")
        logger.info("Fix dialog closed - scheduling UI reset")
        
        self._fix_dialog_open = False
        
        # Schedule UI reset after fix operations complete
        QTimer.singleShot(2000, self._safe_reset_ui_state)
        
    def _safe_reset_ui_state(self):
        """Safe reset that preserves critical data if fix might be applied"""
        # Check if UI reset was cancelled due to fix operations
        if hasattr(self, '_ui_reset_cancelled') and self._ui_reset_cancelled:
            logger.debug("UI reset cancelled - fix operations in progress")
            self.status_label.setText("UI reset cancelled - fix operations in progress")
            return
            
        # Only reset if we're not in the middle of fix operations
        if not hasattr(self, '_fix_dialog_open') or not self._fix_dialog_open:
            logger.info("UI reset completed successfully")
            self.status_label.setText("UI reset completed successfully!")
            self._reset_ui_state()
        else:
            logger.debug("Skipping UI reset - fix dialog might be open")
            self.status_label.setText("Skipping UI reset - fix dialog is open")
            
    def _reset_ui_state(self):
        """Actual UI reset logic"""
        # Reset flags
        self._ui_reset_cancelled = False
        self._fix_dialog_open = False
        logger.debug("UI state reset to initial values")

def main():
    app = QApplication(sys.argv)
    
    window = MockMainWindow()
    window.show()
    
    logger.info("UI Reset Timing Test started")
    logger.info("Instructions:")
    logger.info("1. Click 'Simulate Download Completion' to start 8-second reset timer")
    logger.info("2. Click 'Simulate Fix Dialog' within 8 seconds to cancel timer")
    logger.info("3. Observe that UI reset is properly cancelled and rescheduled")
    logger.info("4. Test manual reset with 'Manual UI Reset' button")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()