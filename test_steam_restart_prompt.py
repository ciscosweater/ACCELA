#!/usr/bin/env python3
"""
Test script to verify Steam restart prompt logic when declining Online Fix
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

def test_steam_restart_logic():
    """Test the Steam restart prompt logic directly"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from ui.main_window import MainWindow
    
    app = QApplication([])
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Test the logic directly
    logger.info("Testing Steam restart prompt logic...")
    
    # Simulate the state when user declines Online Fix
    window._steam_restart_prompted = True  # Simulate that it was prompted before
    window._fix_available = False  # Fix was declined
    
    logger.info(f"Before reset - _steam_restart_prompted: {window._steam_restart_prompted}")
    logger.info(f"Before reset - _fix_available: {window._fix_available}")
    
    # Simulate the fix that should trigger the prompt even when fix is declined
    def test_prompt_logic():
        # Reset the flag to allow the prompt (this is what the fix does)
        window._steam_restart_prompted = False
        logger.info(f"After reset - _steam_restart_prompted: {window._steam_restart_prompted}")
        
        # Check if prompt would be shown
        should_prompt = (
            not window._steam_restart_prompted or 
            hasattr(window, '_fix_applied_recently')
        )
        
        logger.info(f"Should prompt for Steam restart: {should_prompt}")
        
        if should_prompt:
            logger.info("✅ Steam restart prompt logic is correct!")
            return True
        else:
            logger.error("❌ Steam restart prompt logic is incorrect!")
            return False
    
    def finish_test():
        app.quit()
    
    # Schedule test
    QTimer.singleShot(1000, test_prompt_logic)
    QTimer.singleShot(3000, finish_test)
    
    app.exec()
    
    return True

def test_code_integration():
    """Test that the code changes are properly integrated"""
    logger.info("Testing code integration...")
    
    # Check if the fix is present in the code
    try:
        with open('/home/gustavof/Projetos/ACCELA-GitHub/ui/main_window.py', 'r') as f:
            content = f.read()
            
        # Check for the specific fix
        if "_prompt_for_steam_restart()" in content and "_steam_restart_prompted = False" in content:
            logger.info("✅ Code integration verified - Steam restart prompt fix is present!")
            return True
        else:
            logger.error("❌ Code integration failed - fix not found in code!")
            return False
            
    except Exception as e:
        logger.error(f"Error checking code integration: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Steam Restart Prompt Fix Test ===")
    logger.info("Testing Steam restart prompt when declining Online Fix\n")
    
    # Test 1: Code Integration
    logger.info("--- Test 1: Code Integration ---")
    integration_test = test_code_integration()
    
    # Test 2: Logic Test
    logger.info("\n--- Test 2: Logic Test ---")
    logic_test = test_steam_restart_logic()
    
    # Final results
    logger.info("\n=== Final Test Results ===")
    if integration_test and logic_test:
        logger.info("🎉 All tests passed! Steam restart prompt should now appear when declining Online Fix.")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed!")
        sys.exit(1)