import logging
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QToolTip, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen

from core.slssteam_checker import SlssteamChecker, SlssteamStatus
from ui.interactions import HoverButton, ModernFrame
from ui.slssteam_setup_dialog import SlssteamSetupDialog

logger = logging.getLogger(__name__)

class StatusIndicator(QLabel):
    """Custom status indicator with colored circles"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.status = SlssteamStatus.ERROR
        self.setStyleSheet("border-radius: 8px;")
    
    def set_status(self, status: SlssteamStatus):
        """Update indicator color based on status"""
        self.status = status
        
        colors = {
            SlssteamStatus.INSTALLED_GOOD_CONFIG: "#4CAF50",  # Green
            SlssteamStatus.INSTALLED_BAD_CONFIG: "#FF9800",  # Orange  
            SlssteamStatus.NOT_INSTALLED: "#F44336",         # Red
            SlssteamStatus.ERROR: "#9E9E9E"                  # Gray
        }
        
        color = colors.get(status, "#9E9E9E")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 8px;
                border: 2px solid #1E1E1E;
            }}
        """)
        
        # Set tooltip
        tooltips = {
            SlssteamStatus.INSTALLED_GOOD_CONFIG: "SLSsteam OK",
            SlssteamStatus.INSTALLED_BAD_CONFIG: "Configuration needed",
            SlssteamStatus.NOT_INSTALLED: "Not installed",
            SlssteamStatus.ERROR: "Verification error"
        }
        
        tooltip = tooltips.get(status, "Status desconhecido")
        self.setToolTip(tooltip)
    
    def paintEvent(self, a0):
        """Custom paint for smooth circle"""
        super().paintEvent(a0)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circle
        pen = QPen(QColor("#1E1E1E"), 2)
        painter.setPen(pen)
        
        colors = {
            SlssteamStatus.INSTALLED_GOOD_CONFIG: QColor("#4CAF50"),
            SlssteamStatus.INSTALLED_BAD_CONFIG: QColor("#FF9800"),
            SlssteamStatus.NOT_INSTALLED: QColor("#F44336"),
            SlssteamStatus.ERROR: QColor("#9E9E9E")
        }
        
        color = colors.get(self.status, QColor("#9E9E9E"))
        painter.setBrush(color)
        
        painter.drawEllipse(2, 2, 12, 12)

class SlssteamStatusWidget(ModernFrame):
    """
    SLSsteam status indicator widget for ACCELA main window.
    
    Shows installation status with visual indicator and action button.
    """
    
    # Signals
    setup_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checker = SlssteamChecker()
        self.current_status = SlssteamStatus.ERROR
        self.current_details = {}
        self.setup_dialog = None
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.setInterval(30000)  # 30 seconds
        
        self._setup_ui()
        self.refresh_status()
        
        # Start auto-refresh
        self.refresh_timer.start()
    
    def _setup_ui(self):
        """Setup the UI components"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            ModernFrame {
                background-color: #1E1E1E;
                border: none;
                border-radius: 0px;
                margin: 0px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)
        
        # Status indicator
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator)
        
        # Status text - single line for cleaner look
        self.status_label = QLabel("Checking SLSsteam...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #C06C84;
                font-weight: bold;
                font-size: 12px;
                background-color: transparent;
            }
        """)
        self.status_label.setFont(QFont("TrixieCyrG-Plain", 11))
        self.status_label.setWordWrap(False)
        layout.addWidget(self.status_label, 1)  # Takes available space
        
        # Action button
        self.action_button = HoverButton("Configure")
        self.action_button.setFixedSize(75, 28)
        self.action_button.setStyleSheet("""
            HoverButton {
                background-color: #C06C84;
                color: #1E1E1E;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            HoverButton:hover {
                background-color: #D07C94;
            }
        """)
        self.action_button.setFont(QFont("TrixieCyrG-Plain", 9))
        self.action_button.clicked.connect(self._on_action_clicked)
        self.action_button.hide()  # Hide initially
        
        layout.addWidget(self.action_button)
    
    def refresh_status(self):
        """Refresh SLSsteam status"""
        try:
            status, details = self.checker.check_installation()
            self.current_status = status
            self.current_details = details
            
            self._update_ui()
            
        except Exception as e:
            logger.error(f"Error refreshing SLSsteam status: {e}")
            self.current_status = SlssteamStatus.ERROR
            self.current_details = {"error_message": str(e)}
            self._update_ui()
    
    def _update_ui(self):
        """Update UI based on current status"""
        # Update indicator
        self.status_indicator.set_status(self.current_status)
        
        # Update text with tooltip info
        status_message = self.checker.get_status_message(self.current_status, self.current_details)
        
        # Add blocking indicator if not ready
        if not self.can_start_operations():
            status_message += " (BLOCKED)"
        
        self.status_label.setText(status_message)
        
        # Set detailed tooltip
        description = self.checker.get_status_description(self.current_status, self.current_details)
        if not self.can_start_operations():
            description += "\n\nACCELA operations are blocked until SLSsteam is configured."
        
        self.setToolTip(description)
        
        # Update action button
        if self.current_status in [SlssteamStatus.NOT_INSTALLED, SlssteamStatus.INSTALLED_BAD_CONFIG]:
            self.action_button.show()
            
            if self.current_status == SlssteamStatus.NOT_INSTALLED:
                self.action_button.setText("Install")
            else:
                self.action_button.setText("Fix")
        else:
            self.action_button.hide()
    
    def _update_tooltip(self):
        """Update widget tooltip with detailed information"""
        if self.current_status == SlssteamStatus.ERROR:
            tooltip = f"Error: {self.current_details.get('error_message', 'Unknown')}"
        elif self.current_status == SlssteamStatus.INSTALLED_BAD_CONFIG:
            pno = self.current_details.get('play_not_owned_games', 'unknown')
            tooltip = f"PlayNotOwnedGames: {pno} (should be 'yes')"
        elif self.current_status == SlssteamStatus.INSTALLED_GOOD_CONFIG:
            tooltip = "SLSsteam is ready for use"
        else:
            tooltip = "Click to install/configure"
        
        self.setToolTip(tooltip)
    
    def _on_action_clicked(self):
        """Handle action button click"""
        try:
            if self.current_status == SlssteamStatus.NOT_INSTALLED:
                self._show_install_dialog()
            elif self.current_status == SlssteamStatus.INSTALLED_BAD_CONFIG:
                self._show_fix_dialog()
        except Exception as e:
            logger.error(f"Error handling action click: {e}")
    
    def _show_install_dialog(self):
        """Show SLSsteam installation dialog"""
        if not self.setup_dialog:
            self.setup_dialog = SlssteamSetupDialog(self)
            self.setup_dialog.setup_completed.connect(self._on_setup_completed)
        
        self.setup_dialog.set_mode("install")
        self.setup_dialog.show()
    
    def _show_fix_dialog(self):
        """Show SLSsteam configuration fix dialog"""
        if not self.setup_dialog:
            self.setup_dialog = SlssteamSetupDialog(self)
            self.setup_dialog.setup_completed.connect(self._on_setup_completed)
        
        self.setup_dialog.set_mode("fix")
        self.setup_dialog.show()
    
    def _on_setup_completed(self, success: bool):
        """Handle setup completion"""
        if success:
            # Refresh status after a short delay to allow file operations to complete
            QTimer.singleShot(1000, self.refresh_status)
        
        self.setup_requested.emit()
    
    def get_current_status(self) -> tuple[SlssteamStatus, dict]:
        """Get current status and details"""
        return self.current_status, self.current_details
    
    def is_slssteam_ready(self) -> bool:
        """Check if SLSsteam is ready for use"""
        return self.current_status == SlssteamStatus.INSTALLED_GOOD_CONFIG
    
    def can_start_operations(self) -> bool:
        """Check if ACCELA operations can start (SLSsteam must be ready)"""
        return self.is_slssteam_ready()
    
    def get_blocking_message(self) -> str:
        """Get message explaining why operations are blocked"""
        if self.current_status == SlssteamStatus.INSTALLED_GOOD_CONFIG:
            return ""
        
        return self.checker.get_status_description(self.current_status, self.current_details)
    
    def closeEvent(self, a0):
        """Handle widget close event"""
        if self.refresh_timer:
            self.refresh_timer.stop()
        
        if self.setup_dialog:
            self.setup_dialog.close()
        
        super().closeEvent(a0)