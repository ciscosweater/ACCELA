import sys
import os
import logging

# Add project root to Python path. This allows absolute imports
# (e.g., 'from core.tasks...') to work from any submodule.
# This must be done BEFORE importing any project modules.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.main_window import MainWindow
from ui.theme_manager import theme_manager
from utils.logger import setup_logging

logger = logging.getLogger(__name__)

def restart_application():
    """Restart the application"""
    logger.info("Restarting application...")
    QApplication.quit()
    os.execl(sys.executable, sys.executable, *sys.argv)

def main():
    """
    The main entry point for ACCELA application.
    Initializes logging, theme system, and launches main window.
    """
    # Set up application-wide logger to capture logs from all modules.
    logger = setup_logging()
    logger.info("========================================")
    logger.info("ACCELA Application starting...")
    logger.info("========================================")

    app = QApplication(sys.argv)
    app.setApplicationName("ACCELA")
    app.setOrganizationName("ACCELA")
    app.setStyle("Fusion")
    
    # Initialize theme manager
    theme_manager.initialize(app)
    
    # Connect theme manager restart signal
    theme_manager.restart_requested.connect(restart_application)
    
    try:
        # Check if a zip file was passed as command line argument
        zip_file_arg = None
        if len(sys.argv) > 1:
            zip_file_arg = sys.argv[1]
            if zip_file_arg.lower().endswith('.zip') and os.path.isfile(zip_file_arg):
                logger.info(f"Zip file provided as argument: {zip_file_arg}")
            else:
                zip_file_arg = None

        main_win = MainWindow(zip_file_arg)
        main_win.show()
        logger.info("Main window displayed successfully.")
        
        # Start Qt event loop
        sys.exit(app.exec())
    except Exception as e:
        # A global catch-all for any unhandled exceptions during initialization.
        logger.critical(f"A critical error occurred, and application must close. Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
