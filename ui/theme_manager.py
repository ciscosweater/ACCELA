"""
ACCELA Theme Manager - Dynamic Theme System
Provides comprehensive theme management with live switching and customization
"""

import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QFontDatabase

from utils.settings import (
    get_current_theme_config,
    set_theme_colors,
    set_theme_fonts,
    reset_theme_customizations,
    get_available_themes,
    apply_theme as apply_theme_settings,
    should_auto_restart_on_theme_change,
    get_theme_setting,
    set_theme_setting
)

logger = logging.getLogger(__name__)

class ThemeManager(QObject):
    """Central theme management system with dynamic switching capabilities"""
    
    # Signals
    theme_changed = pyqtSignal(str)  # theme_id
    colors_updated = pyqtSignal(dict)  # color_overrides
    fonts_updated = pyqtSignal(dict)  # font_overrides
    restart_requested = pyqtSignal()  # when theme change requires restart
    
    def __init__(self):
        super().__init__()
        self._current_theme_id = None
        self._current_config = None
        self._app = None
        self._loaded_fonts = {}
        
        # Load initial theme
        self._load_current_theme()
    
    def initialize(self, app: QApplication):
        """
        Initialize theme manager with QApplication instance.
        
        Args:
            app: QApplication instance to apply themes to
        """
        self._app = app
        self._load_custom_fonts()
        self._apply_current_theme()
        logger.info(f"Theme manager initialized with theme: {self._current_theme_id}")
    
    def _load_custom_fonts(self):
        """Load custom fonts from assets directory"""
        try:
            font_db = QFontDatabase()
            
            # Load Trixie font
            trixie_path = "assets/fonts/TrixieCyrG-Plain Regular.otf"
            font_id = font_db.addApplicationFont(trixie_path)
            if font_id != -1:
                font_families = font_db.applicationFontFamilies(font_id)
                if font_families:
                    self._loaded_fonts["trixie"] = font_families[0]
                    logger.info(f"Loaded Trixie font: {font_families[0]}")
            
            # Load Motiva Sans font
            motiva_path = "assets/fonts/MotivaSansRegular.woff.ttf"
            font_id = font_db.addApplicationFont(motiva_path)
            if font_id != -1:
                font_families = font_db.applicationFontFamilies(font_id)
                if font_families:
                    self._loaded_fonts["motiva"] = font_families[0]
                    logger.info(f"Loaded Motiva Sans font: {font_families[0]}")
                    
        except Exception as e:
            logger.warning(f"Failed to load custom fonts: {e}")
    
    def _load_current_theme(self):
        """Load current theme configuration from settings"""
        self._current_config = get_current_theme_config()
        
        # Determine current theme ID by comparing with available themes
        from utils.settings import AVAILABLE_THEMES
        for theme_id, theme_config in AVAILABLE_THEMES.items():
            if (theme_config["name"] == self._current_config["name"] and
                theme_config["description"] == self._current_config["description"]):
                self._current_theme_id = theme_id
                break
        
        if not self._current_theme_id:
            self._current_theme_id = "default_dark"
    
    def _apply_current_theme(self):
        """Apply the current theme to the application"""
        if not self._app or not self._current_config:
            return
        
        # Generate and apply stylesheet
        stylesheet = self._generate_stylesheet()
        self._app.setStyleSheet(stylesheet)
        
        # Apply application font
        self._apply_application_font()
    
    def _apply_application_font(self):
        """Apply the theme's font to the application"""
        if not self._app or not self._current_config:
            return
        
        font_config = self._current_config.get("fonts", {})
        font_name = font_config.get("primary", "Arial")
        
        # Map font names to loaded fonts
        if font_name == "TrixieCyrG-Plain Regular" and "trixie" in self._loaded_fonts:
            font_name = self._loaded_fonts["trixie"]
        elif font_name == "MotivaSansRegular" and "motiva" in self._loaded_fonts:
            font_name = self._loaded_fonts["motiva"]
        
        app_font = QFont(font_name)
        app_font.setPointSize(font_config.get("body_size", 12))
        self._app.setFont(app_font)
    
    def _generate_stylesheet(self) -> str:
        """Generate complete stylesheet from current theme configuration"""
        if not self._current_config:
            return ""
        
        colors = self._current_config.get("colors", {})
        fonts = self._current_config.get("fonts", {})
        
        stylesheet = f"""
        /* Global Styles */
        QMainWindow {{
            background: {colors.get('background', '#1A1A1A')};
            color: {colors.get('text_primary', '#E8E8E8')};
        }}
        
        QWidget {{
            background: transparent;
            color: {colors.get('text_primary', '#E8E8E8')};
        }}
        
        QLabel {{
            color: {colors.get('text_primary', '#E8E8E8')};
            font-size: {fonts.get('body_size', 12)}px;
            font-weight: 400;
        }}
        
        QLineEdit, QTextEdit {{
            background: {colors.get('surface', '#252525')};
            border: 1px solid {colors.get('border', '#353535')};
            color: {colors.get('text_primary', '#E8E8E8')};
            border-radius: 6px;
            padding: 8px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border: 1px solid {colors.get('primary', '#C06C84')};
        }}
        
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('primary', '#C06C84')}, stop:1 {colors.get('primary_dark', '#A05C74')});
            border: 1px solid {colors.get('primary_dark', '#A05C74')};
            color: {colors.get('text_on_primary', '#FFFFFF')};
            font-size: {fonts.get('body_size', 12)}px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 6px;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('primary_light', '#D08C9C')}, stop:1 {colors.get('primary', '#C06C84')});
            border: 1px solid {colors.get('primary', '#C06C84')};
        }}
        
        QPushButton:pressed {{
            background: {colors.get('primary_dark', '#A05C74')};
            border: 1px solid {colors.get('primary_dark', '#A05C74')};
        }}
        
        QPushButton:disabled {{
            background: {colors.get('surface', '#252525')};
            color: {colors.get('text_disabled', '#606060')};
            border: 1px solid {colors.get('border', '#353535')};
        }}
        
        QFrame {{
            background: {colors.get('surface', '#252525')};
            border: 1px solid {colors.get('border', '#353535')};
            border-radius: 8px;
        }}
        
        QProgressBar {{
            max-height: 18px;
            border: 1px solid {colors.get('border', '#353535')};
            text-align: center;
            color: {colors.get('text_primary', '#E8E8E8')};
            font-size: {fonts.get('caption_size', 10)}px;
            font-weight: bold;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('surface', '#252525')}, stop:1 {colors.get('background', '#1A1A1A')});
            border-radius: 4px;
            padding: 1px;
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {colors.get('primary', '#C06C84')}, stop:0.5 {colors.get('primary_light', '#D08C9C')}, stop:1 {colors.get('primary', '#C06C84')});
            border-radius: 4px;
        }}
        
        QStatusBar {{
            border: 0px;
            background: {colors.get('background', '#1A1A1A')};
            height: 8px;
        }}
        
        QScrollBar:vertical {{
            background: {colors.get('surface', '#252525')};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors.get('border', '#353535')};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {colors.get('primary', '#C06C84')};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QComboBox {{
            background: {colors.get('surface', '#252525')};
            border: 1px solid {colors.get('border', '#353535')};
            color: {colors.get('text_primary', '#E8E8E8')};
            padding: 6px 12px;
            border-radius: 6px;
            min-width: 80px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {colors.get('primary', '#C06C84')};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {colors.get('text_secondary', '#B0B0B0')};
        }}
        
        QComboBox QAbstractItemView {{
            background: {colors.get('surface', '#252525')};
            border: 1px solid {colors.get('border', '#353535')};
            color: {colors.get('text_primary', '#E8E8E8')};
            selection-background-color: {colors.get('primary', '#C06C84')};
            selection-color: {colors.get('text_on_primary', '#FFFFFF')};
            border-radius: 6px;
        }}
        
        QCheckBox {{
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {colors.get('border', '#353535')};
            border-radius: 3px;
            background: {colors.get('surface', '#252525')};
        }}
        
        QCheckBox::indicator:hover {{
            border: 1px solid {colors.get('primary', '#C06C84')};
        }}
        
        QCheckBox::indicator:checked {{
            background: {colors.get('primary', '#C06C84')};
            border: 1px solid {colors.get('primary', '#C06C84')};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {colors.get('border', '#353535')};
            background: {colors.get('surface', '#252525')};
            border-radius: 6px;
        }}
        
        QTabBar::tab {{
            background: {colors.get('surface_dark', '#151515')};
            color: {colors.get('text_secondary', '#B0B0B0')};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}
        
        QTabBar::tab:selected {{
            background: {colors.get('surface', '#252525')};
            color: {colors.get('text_primary', '#E8E8E8')};
            border: 1px solid {colors.get('border', '#353535')};
            border-bottom: 1px solid {colors.get('surface', '#252525')};
        }}
        
        QTabBar::tab:hover {{
            background: {colors.get('surface_light', '#303030')};
            color: {colors.get('text_primary', '#E8E8E8')};
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {colors.get('border', '#353535')};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        
        QSlider::groove:horizontal {{
            border: 1px solid {colors.get('border', '#353535')};
            height: 6px;
            background: {colors.get('surface', '#252525')};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {colors.get('primary', '#C06C84')};
            border: 1px solid {colors.get('primary_dark', '#A05C74')};
            width: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {colors.get('primary_light', '#D08C9C')};
        }}
        """
        
        return stylesheet
    
    def get_current_theme_id(self) -> str:
        """Get current theme ID"""
        return self._current_theme_id or "default_dark"
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current theme configuration"""
        return self._current_config.copy() if self._current_config else {}
    
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        return get_available_themes()
    
    def apply_theme(self, theme_id: str, prompt_restart: bool = True) -> bool:
        """
        Apply a new theme.
        
        Args:
            theme_id: ID of theme to apply
            prompt_restart: Whether to prompt for restart if needed
            
        Returns:
            bool: True if theme was applied successfully
        """
        if not apply_theme_settings(theme_id):
            logger.error(f"Failed to apply theme: {theme_id}")
            return False
        
        self._load_current_theme()
        self._apply_current_theme()
        
        self.theme_changed.emit(theme_id)
        
        # Check if restart is needed and auto-restart is enabled
        if prompt_restart and should_auto_restart_on_theme_change():
            self._prompt_restart()
        
        logger.info(f"Applied theme: {theme_id}")
        return True
    
    def update_colors(self, color_overrides: Dict[str, str], prompt_restart: bool = True):
        """
        Update theme colors with custom overrides.
        
        Args:
            color_overrides: Dictionary of color overrides
            prompt_restart: Whether to prompt for restart if needed
        """
        set_theme_colors(color_overrides)
        self._load_current_theme()
        self._apply_current_theme()
        
        self.colors_updated.emit(color_overrides)
        
        if prompt_restart and should_auto_restart_on_theme_change():
            self._prompt_restart()
        
        logger.info(f"Updated theme colors: {color_overrides}")
    
    def update_fonts(self, font_overrides: Dict[str, Any], prompt_restart: bool = True):
        """
        Update theme fonts with custom overrides.
        
        Args:
            font_overrides: Dictionary of font overrides
            prompt_restart: Whether to prompt for restart if needed
        """
        set_theme_fonts(font_overrides)
        self._load_current_theme()
        self._apply_current_theme()
        
        self.fonts_updated.emit(font_overrides)
        
        if prompt_restart and should_auto_restart_on_theme_change():
            self._prompt_restart()
        
        logger.info(f"Updated theme fonts: {font_overrides}")
    
    def reset_customizations(self, prompt_restart: bool = True):
        """
        Reset all custom theme overrides.
        
        Args:
            prompt_restart: Whether to prompt for restart if needed
        """
        reset_theme_customizations()
        self._load_current_theme()
        self._apply_current_theme()
        
        if prompt_restart and should_auto_restart_on_theme_change():
            self._prompt_restart()
        
        logger.info("Reset all theme customizations")
    
    def _prompt_restart(self):
        """Prompt user to restart application for theme changes to take full effect"""
        reply = QMessageBox.question(
            None,
            "Restart Required",
            "Theme changes have been applied. Some changes may require a restart to take full effect.\n\nWould you like to restart now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.restart_requested.emit()
    
    def refresh_theme(self):
        """Refresh the current theme (reapply to application)"""
        self._load_current_theme()
        self._apply_current_theme()
        logger.info("Theme refreshed")
    
    def get_color(self, color_name: str) -> str:
        """
        Get a specific color from the current theme.
        
        Args:
            color_name: Name of the color
            
        Returns:
            str: Color hex value
        """
        if not self._current_config:
            return "#000000"
        
        colors = self._current_config.get("colors", {})
        return colors.get(color_name, "#000000")
    
    def get_font_config(self) -> Dict[str, Any]:
        """Get current font configuration"""
        if not self._current_config:
            return {}
        
        return self._current_config.get("fonts", {}).copy()
    
    def create_font(self, size: Optional[int] = None, weight: str = "normal") -> QFont:
        """
        Create a QFont with current theme settings.
        
        Args:
            size: Font size (uses theme default if None)
            weight: Font weight ("normal", "bold", "light")
            
        Returns:
            QFont: Configured font
        """
        if not self._current_config:
            return QFont()
        
        font_config = self._current_config.get("fonts", {})
        font_name = font_config.get("primary", "Arial")
        
        # Map font names to loaded fonts
        if font_name == "TrixieCyrG-Plain Regular" and "trixie" in self._loaded_fonts:
            font_name = self._loaded_fonts["trixie"]
        elif font_name == "MotivaSansRegular" and "motiva" in self._loaded_fonts:
            font_name = self._loaded_fonts["motiva"]
        
        font_size = size if size is not None else font_config.get("body_size", 12)
        
        font = QFont(font_name, font_size)
        
        # Set weight
        if weight == "bold":
            font.setBold(True)
        elif weight == "light":
            font.setWeight(QFont.Weight.Light)
        
        return font

# Global theme manager instance
theme_manager = ThemeManager()