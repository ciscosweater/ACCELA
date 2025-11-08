import logging
import sys
from PyQt6.QtCore import QObject, pyqtSignal

class QtLogHandler(QObject, logging.Handler):
    """
    A custom logging handler that emits a signal for each log record.
    This allows log messages to be displayed in a PyQt widget.
    """
    new_record = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        """
        Emits the formatted log record as a signal.
        """
        msg = self.format(record)
        self.new_record.emit(msg)

# --- MODIFICATION START ---
# Initialize the handler immediately when the module is imported.
# This prevents a race condition where other modules might try to use it
# before it's been initialized by setup_logging().
qt_log_handler = QtLogHandler()
# --- MODIFICATION END ---

def setup_logging():
    """
    Configures the root logger for the application.

    Sets up three handlers:
    1. A stream handler to print logs to the console (for debugging).
    2. A file handler to save logs to 'app.log'.
    3. A custom Qt handler to display logs in the GUI.

    Returns:
        The configured root logger instance.
    """
    # The global qt_log_handler is already created, so we just add it.
    logging.basicConfig(
        level=logging.DEBUG,  # Capture all levels of logs
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", mode='w'),  # Log to a file
            logging.StreamHandler(sys.stdout),         # Log to console
            qt_log_handler                             # Log to GUI
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging configured.")
    return logger
