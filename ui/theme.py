"""
ACCELA Design System - Centralized styling and design constants
Provides unified color palette, typography, spacing, and component styles
"""

from PyQt6.QtGui import QColor

class Colors:
    """Centralized color palette for ACCELA application"""
    
    # Primary colors (existing theme)
    PRIMARY = "#C06C84"           # Main accent color
    PRIMARY_LIGHT = "#D07C94"     # Hover states
    PRIMARY_DARK = "#A05C74"      # Pressed states
    PRIMARY_VARIANT = "#B05C74"   # Alternative primary
    
    # Secondary colors
    SECONDARY = "#6C84C0"         # Information accents
    SECONDARY_LIGHT = "#7C94D0"   # Secondary hover
    SECONDARY_DARK = "#5C74B0"    # Secondary pressed
    
    # Status colors
    SUCCESS = "#6CC084"           # Success states
    SUCCESS_LIGHT = "#7CD094"     # Success hover
    SUCCESS_DARK = "#5CB074"      # Success pressed
    
    WARNING = "#C0A06C"           # Warning states
    WARNING_LIGHT = "#D0B07C"     # Warning hover
    WARNING_DARK = "#B0905C"      # Warning pressed
    
    ERROR = "#C06C84"             # Error states (reuse primary)
    ERROR_LIGHT = "#D07C94"       # Error hover
    ERROR_DARK = "#A05C74"        # Error pressed
    
    # Neutral colors
    BACKGROUND = "#1E1E1E"        # Main background
    SURFACE = "#282828"           # Card surfaces
    SURFACE_LIGHT = "#333333"     # Hover surfaces
    SURFACE_DARK = "#1A1A1A"      # Dark surfaces
    
    BORDER = "#404040"            # Subtle borders
    BORDER_LIGHT = "#505050"      # Light borders
    BORDER_DARK = "#303030"       # Dark borders
    
    # Text colors
    TEXT_PRIMARY = "#C06C84"      # Main text
    TEXT_SECONDARY = "#808080"    # Secondary text
    TEXT_DISABLED = "#505050"     # Disabled text
    TEXT_ON_PRIMARY = "#FFFFFF"   # Text on primary backgrounds
    
    # Overlay colors
    OVERLAY = "rgba(30, 30, 30, 0.8)"      # Modal overlay
    OVERLAY_LIGHT = "rgba(30, 30, 30, 0.6)" # Light overlay
    
    # Glassmorphism colors (simplified for PyQt6 compatibility)
    GLASS_SURFACE = "#282828"
    GLASS_BORDER = "#404040"
    
    @staticmethod
    def get_qcolor(color_hex: str) -> QColor:
        """Convert hex color to QColor"""
        return QColor(color_hex)


class Typography:
    """Unified typography system"""
    
    # Font sizes
    H1_SIZE = 24       # Main titles
    H2_SIZE = 18       # Section headers
    H3_SIZE = 14       # Sub-headers
    BODY_SIZE = 12     # Body text
    CAPTION_SIZE = 10  # Small text/captions
    
    # Font weights
    WEIGHT_LIGHT = "light"
    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD = "bold"
    
    # Font family
    PRIMARY_FONT = "TrixieCyrG-Plain Regular"
    FALLBACK_FONT = "Arial"
    
    @staticmethod
    def get_font_style(size: int, weight: str = "normal") -> str:
        """Generate font style string"""
        return f"font-size: {size}px; font-weight: {weight};"
    
    @staticmethod
    def get_font_family() -> str:
        """Get font family string with fallback"""
        # Return empty string to use application font
        return ""


class Spacing:
    """Consistent spacing system"""
    
    XS = 4    # Icon padding, tiny gaps
    SM = 8    # Button padding, small gaps
    MD = 16   # Component spacing
    LG = 24   # Section spacing
    XL = 32   # Page margins
    XXL = 48  # Large section breaks
    
    @staticmethod
    def get_margin(size: int) -> str:
        """Generate margin string"""
        return f"margin: {size}px;"
    
    @staticmethod
    def get_padding(size: int, horizontal: int = None) -> str:
        """Generate padding string"""
        if horizontal is not None:
            return f"padding: {size}px {horizontal}px;"
        return f"padding: {size}px;"
    
    @staticmethod
    def get_spacing_all(size: int) -> str:
        """Generate margin and padding string"""
        return f"margin: {size}px; padding: {size}px;"


class BorderRadius:
    """Consistent border radius system"""
    
    NONE = 0
    SMALL = 4
    MEDIUM = 6
    LARGE = 8
    XLARGE = 12
    ROUND = 50
    
    @staticmethod
    def get_border_radius(radius: int) -> str:
        """Generate border radius string"""
        return f"border-radius: {radius}px;"


class Shadows:
    """Shadow system for depth"""
    
    NONE = "none"
    SUBTLE = "0 1px 3px rgba(0, 0, 0, 0.2)"
    MEDIUM = "0 4px 6px rgba(0, 0, 0, 0.3)"
    LARGE = "0 8px 16px rgba(0, 0, 0, 0.4)"
    GLOW = f"0 0 20px {Colors.PRIMARY}40"
    
    @staticmethod
    def get_shadow(shadow: str) -> str:
        """Generate box-shadow string"""
        return f"box-shadow: {shadow};"


class Animations:
    """Animation constants"""
    
    DURATION_FAST = "0.15s"
    DURATION_NORMAL = "0.2s"
    DURATION_SLOW = "0.3s"
    
    EASING_EASE = "ease"
    EASING_EASE_IN = "ease-in"
    EASING_EASE_OUT = "ease-out"
    EASING_EASE_IN_OUT = "ease-in-out"
    
    @staticmethod
    def get_transition(property: str, duration: str = None, easing: str = None) -> str:
        """Generate transition string"""
        dur = duration or Animations.DURATION_NORMAL
        eas = easing or Animations.EASING_EASE_OUT
        return f"transition: {property} {dur} {eas};"


class ComponentStyles:
    """Pre-defined component styles"""
    
    # Modern card style
    CARD = f"""
        QFrame {{
            background: {Colors.GLASS_SURFACE};
            border: 1px solid {Colors.GLASS_BORDER};
            {BorderRadius.get_border_radius(BorderRadius.LARGE)};
            {Spacing.get_padding(Spacing.MD)};
        }}
        QFrame:hover {{
            background: {Colors.SURFACE_LIGHT};
            border: 1px solid {Colors.BORDER_LIGHT};
        }}
    """
    
    # Primary button style
    PRIMARY_BUTTON = f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
            border: none;
            color: {Colors.TEXT_ON_PRIMARY};
            {Typography.get_font_style(Typography.BODY_SIZE, Typography.WEIGHT_BOLD)};
            {Spacing.get_padding(Spacing.SM, Spacing.MD)};
            {BorderRadius.get_border_radius(BorderRadius.MEDIUM)};
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Colors.PRIMARY_LIGHT}, stop:1 {Colors.PRIMARY});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Colors.PRIMARY_DARK}, stop:1 {Colors.PRIMARY_DARK});
        }}
        QPushButton:disabled {{
            background: {Colors.BORDER};
            color: {Colors.TEXT_DISABLED};
        }}
    """
    
    # Secondary button style
    SECONDARY_BUTTON = f"""
        QPushButton {{
            background: transparent;
            border: 1px solid {Colors.PRIMARY};
            color: {Colors.PRIMARY};
            {Typography.get_font_style(Typography.BODY_SIZE)};
            {Spacing.get_padding(Spacing.SM, Spacing.MD)};
            {BorderRadius.get_border_radius(BorderRadius.MEDIUM)};
        }}
        QPushButton:hover {{
            background: {Colors.PRIMARY};
            color: {Colors.TEXT_ON_PRIMARY};
        }}
        QPushButton:pressed {{
            background: {Colors.PRIMARY_DARK};
            border-color: {Colors.PRIMARY_DARK};
        }}
    """
    
    # Enhanced progress bar
    PROGRESS_BAR = f"""
        QProgressBar {{ 
            max-height: 16px; 
            border: 1px solid {Colors.PRIMARY}; 
            text-align: center; 
            color: {Colors.TEXT_PRIMARY}; 
            {Typography.get_font_style(Typography.CAPTION_SIZE, Typography.WEIGHT_BOLD)};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 {Colors.BACKGROUND}, stop:1 {Colors.SURFACE});
            {BorderRadius.get_border_radius(BorderRadius.SMALL)};
            {Spacing.get_padding(1)};
        }}
        QProgressBar::chunk {{ 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {Colors.PRIMARY}, stop:0.7 {Colors.PRIMARY_LIGHT}, stop:1 {Colors.PRIMARY}); 
            {BorderRadius.get_border_radius(BorderRadius.SMALL)};
            {Animations.get_transition("width", Animations.DURATION_SLOW)};
        }}
    """
    
    # Status indicator
    STATUS_INDICATOR = {
        'ready': f"background: {Colors.SUCCESS}; color: {Colors.TEXT_ON_PRIMARY};",
        'processing': f"background: {Colors.SECONDARY}; color: {Colors.TEXT_ON_PRIMARY};",
        'error': f"background: {Colors.ERROR}; color: {Colors.TEXT_ON_PRIMARY};",
        'warning': f"background: {Colors.WARNING}; color: {Colors.TEXT_ON_PRIMARY};"
    }
    
    @staticmethod
    def get_status_indicator_style(status: str) -> str:
        """Get status indicator style"""
        status_style = ComponentStyles.STATUS_INDICATOR.get(status, ComponentStyles.STATUS_INDICATOR['ready'])
        base_style = f"""
            QLabel {{
                {status_style};
                {BorderRadius.get_border_radius(BorderRadius.LARGE)};
                {Spacing.get_padding(Spacing.XS, Spacing.SM)};
                {Typography.get_font_style(Typography.CAPTION_SIZE)};
            }}
        """
        return base_style


class Theme:
    """Main theme class that combines all design elements"""
    
    def __init__(self):
        self.colors = Colors()
        self.typography = Typography()
        self.spacing = Spacing()
        self.border_radius = BorderRadius()
        self.shadows = Shadows()
        self.animations = Animations()
        self.components = ComponentStyles()
    
    def apply_theme_to_app(self, app):
        """Apply theme to QApplication"""
        app.setStyleSheet(f"""
            QMainWindow {{
                background: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
            
            QWidget {{
                background: transparent;
                color: {Colors.TEXT_PRIMARY};
            }}
            
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.BODY_SIZE}px;
            }}
            
            QLineEdit, QTextEdit {{
                background: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                color: {Colors.TEXT_PRIMARY};
                {BorderRadius.get_border_radius(BorderRadius.MEDIUM)};
                {Spacing.get_padding(Spacing.SM)};
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {Colors.PRIMARY};
            }}
        """)
    
    def get_dialog_stylesheet(self) -> str:
        """Get stylesheet for dialogs"""
        return f"""
            QDialog {{
                background: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                {BorderRadius.get_border_radius(BorderRadius.LARGE)};
            }}
            
            QFrame {{
                background: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.MEDIUM)};
            }}
            
            QPushButton {{
                background: {Colors.SURFACE};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.MEDIUM)};
                {Spacing.get_padding(Spacing.SM, Spacing.MD)};
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background: {Colors.SURFACE_LIGHT};
                border: 1px solid {Colors.PRIMARY};
            }}
            
            QPushButton:pressed {{
                background: {Colors.SURFACE_DARK};
            }}
            
            QPushButton:disabled {{
                background: {Colors.SURFACE_DARK};
                color: {Colors.TEXT_DISABLED};
                border: 1px solid {Colors.BORDER_DARK};
            }}
        """


# Global theme instance
theme = Theme()