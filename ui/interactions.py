import logging
from PyQt6.QtWidgets import QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QColor

logger = logging.getLogger(__name__)

class HoverButton(QPushButton):
    """
    Enhanced button with smooth hover animations and visual feedback.
    """
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_animations()
        self._setup_style()
        
    def _setup_animations(self):
        """Setup smooth transition animations."""
        self._hover_animation = QPropertyAnimation(self, b"color")
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def _setup_style(self):
        """Apply modern styling with hover states."""
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #282828, stop:1 #1E1E1E);
                border: 1px solid #C06C84;
                color: #C06C84;
                font-weight: bold;
                padding: 8px 16px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #C06C84, stop:1 #A05C74);
                border: 1px solid #D07C94;
                color: #1E1E1E;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 #A05C74, stop:1 #804C64);
                border: 1px solid #905C74;
                transform: translateY(0px);
            }
        """)

class ModernFrame(QFrame):
    """
    Modern frame with glassmorphism effect and subtle shadows.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        
    def _setup_style(self):
        """Apply glassmorphism styling."""
        self.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.95);
                border: 1px solid rgba(192, 108, 132, 0.3);
                backdrop-filter: blur(10px);
            }
        """)

class AnimatedLabel(QLabel):
    """
    Label with smooth fade-in animations and enhanced typography.
    """
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_animations()
        self._setup_style()
        
    def _setup_animations(self):
        """Setup fade-in animation."""
        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_animation.setDuration(300)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def _setup_style(self):
        """Apply enhanced typography styling."""
        self.setStyleSheet("""
            QLabel {
                color: #C06C84;
                font-weight: 500;
                letter-spacing: 0.3px;
                padding: 4px;
            }
        """)
        
    def fade_in(self):
        """Trigger fade-in animation."""
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()

class NotificationWidget(QFrame):
    """
    Modern notification widget with auto-dismiss and smooth animations.
    """
    
    close_requested = pyqtSignal()
    
    def __init__(self, message, notification_type="info", parent=None):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self._setup_ui()
        self._setup_animations()
        self._setup_auto_dismiss()
        
    def _setup_ui(self):
        """Setup notification UI elements."""
        self.setFixedSize(300, 60)
        self._setup_style()
        
    def _setup_style(self):
        """Apply notification styling based on type."""
        colors = {
            "info": ("#6C84C0", "#5A6C9E"),
            "success": ("#6CC084", "#5AA06E"),
            "warning": ("#C0A06C", "#9E805A"),
            "error": ("#C06C84", "#A05C74")
        }
        
        primary, secondary = colors.get(self.notification_type, colors["info"])
        
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 {primary}, stop:1 {secondary});
                border: 1px solid {primary};
                color: #1E1E1E;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        
    def _setup_animations(self):
        """Setup slide and fade animations."""
        self._slide_animation = QPropertyAnimation(self, b"geometry")
        self._slide_animation.setDuration(400)
        self._slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def _setup_auto_dismiss(self):
        """Setup auto-dismiss timer."""
        from PyQt6.QtCore import QTimer
        self._dismiss_timer = QTimer()
        self._dismiss_timer.timeout.connect(self.close_requested.emit)
        self._dismiss_timer.setSingleShot(True)
        
    def show_notification(self):
        """Show notification with animation."""
        self._dismiss_timer.start(5000)  # Auto-dismiss after 5 seconds
        # Animation logic would go here
        
    def dismiss(self):
        """Dismiss notification with animation."""
        self._dismiss_timer.stop()
        # Dismiss animation logic would go here