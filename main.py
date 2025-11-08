import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFontDatabase, QFont

# Add the project root to the Python path. This allows absolute imports
# (e.g., 'from core.tasks...') to work from any submodule.
# This must be done BEFORE importing any project modules.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.main_window import MainWindow
from ui.theme import theme
from utils.logger import setup_logging

def main():
    """
    The main entry point for the Depot Downloader GUI application.
    Initializes logging, sets the application style, and launches the main window.
    """
    # Set up the application-wide logger to capture logs from all modules.
    logger = setup_logging()
    logger.info("========================================")
    logger.info("Application starting...")
    logger.info("========================================")

    app = QApplication(sys.argv)

    # Set a custom dark theme using the new design system
    app.setStyle("Fusion")
    
    # --- MODIFICATION START ---
    # Load and Apply Custom Font FIRST
    font_path = "assets/fonts/TrixieCyrG-Plain Regular.otf"
    font_id = QFontDatabase.addApplicationFont(font_path)
    
    if font_id == -1:
        logger.warning(f"Failed to load custom font from: {font_path}")
        font_name = "Arial"  # Fallback font
    else:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            font_name = font_families[0]
            custom_font = QFont(font_name, 10)
            app.setFont(custom_font)
            logger.info(f"Successfully loaded and applied custom font: '{font_name}'")
        else:
            logger.warning(f"Could not retrieve font family name from: {font_path}")
            font_name = "Arial"  # Fallback font
    
    # Apply theme after font is loaded
    theme.apply_theme_to_app(app)
    # --- MODIFICATION END ---

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
        # Start the Qt event loop.
        sys.exit(app.exec())
    except Exception as e:
        # A global catch-all for any unhandled exceptions during initialization.
        logger.critical(f"A critical error occurred, and the application must close. Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
