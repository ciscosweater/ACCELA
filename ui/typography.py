"""
Typography components for ACCELA application
Provides consistent text styling throughout the application
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from .theme import theme, Typography


class HeadingLabel(QLabel):
    """
    Heading label with consistent typography
    """
    
    def __init__(self, text="", level=1, parent=None):
        super().__init__(text, parent)
        self.level = level
        self._setup_style()
        
    def _setup_style(self):
        """Setup heading style based on level"""
        sizes = {
            1: Typography.H1_SIZE,
            2: Typography.H2_SIZE,
            3: Typography.H3_SIZE
        }
        
        size = sizes.get(self.level, Typography.BODY_SIZE)
        self.setStyleSheet(f"""
            QLabel {{
                color: {theme.colors.TEXT_PRIMARY};
                font-family: '{Typography.get_font_family()}';
                font-size: {size}px;
                font-weight: {Typography.WEIGHT_BOLD};
                margin-bottom: {theme.spacing.SM}px;
            }}
        """)
        
        if self.level == 1:
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class BodyLabel(QLabel):
    """
    Body text label with standard typography
    """
    
    def __init__(self, text="", secondary=False, parent=None):
        super().__init__(text, parent)
        self.secondary = secondary
        self._setup_style()
        
    def _setup_style(self):
        """Setup body text style"""
        color = theme.colors.TEXT_SECONDARY if self.secondary else theme.colors.TEXT_PRIMARY
        weight = Typography.WEIGHT_NORMAL
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-family: '{Typography.get_font_family()}';
                font-size: {Typography.BODY_SIZE}px;
                font-weight: {weight};
            }}
        """)


class CaptionLabel(QLabel):
    """
    Small caption text for metadata and secondary information
    """
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_style()
        
    def _setup_style(self):
        """Setup caption style"""
        self.setStyleSheet(f"""
            QLabel {{
                color: {theme.colors.TEXT_SECONDARY};
                font-family: '{Typography.get_font_family()}';
                font-size: {Typography.CAPTION_SIZE}px;
                font-weight: {Typography.WEIGHT_NORMAL};
            }}
        """)


class TitleLabel(QLabel):
    """
    Main title label with enhanced styling
    """
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_style()
        
    def _setup_style(self):
        """Setup title style with enhanced appearance"""
        self.setStyleSheet(f"""
            QLabel {{
                color: {theme.colors.PRIMARY};
                font-family: '{Typography.get_font_family()}';
                font-size: {Typography.H1_SIZE}px;
                font-weight: {Typography.WEIGHT_BOLD};
                text-align: center;
                margin: {theme.spacing.LG}px 0;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)