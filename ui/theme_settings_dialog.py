"""
ACCELA Theme Settings Dialog - Complete Theme Customization Interface
Provides comprehensive theme management with live preview and customization options
"""

import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QTabWidget, QWidget, QGroupBox, QColorDialog,
    QFontComboBox, QSpinBox, QCheckBox, QSlider, QFrame,
    QScrollArea, QMessageBox, QGridLayout, QFormLayout,
    QLineEdit, QTextEdit, QSplitter, QSizePolicy, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

try:
    from ui.theme_manager import theme_manager
except ImportError:
    theme_manager = None

try:
    from ui.enhanced_widgets import ModernFrame
except ImportError:
    ModernFrame = QFrame
from utils.settings import get_available_themes, should_auto_restart_on_theme_change

logger = logging.getLogger(__name__)

class ColorPickerButton(QPushButton):
    """Custom button that shows current color and opens color picker"""
    
    color_changed = pyqtSignal(str)
    
    def __init__(self, color: str = "#000000", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(60, 30)
        self.clicked.connect(self._pick_color)
        self._update_style()
    
    def _update_style(self):
        """Update button style to show current color"""
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self._color};
                border: 2px solid #555555;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #777777;
            }}
        """)
    
    def _pick_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor(QColor(self._color), self, "Select Color")
        if color.isValid():
            self.set_color(color.name())
    
    def set_color(self, color: str):
        """Set button color"""
        self._color = color
        self._update_style()
        self.color_changed.emit(color)
    
    def get_color(self) -> str:
        """Get current color"""
        return self._color

class ThemePreviewWidget(QWidget):
    """Widget showing live preview of theme changes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 200)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Preview elements
        self.title_label = QLabel("Theme Preview")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        
        self.button = QPushButton("Sample Button")
        self.text_input = QLineEdit("Sample text input")
        self.progress = QProgressBar()
        self.progress.setValue(65)
        
        self.checkbox = QCheckBox("Sample checkbox")
        self.checkbox.setChecked(True)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.button)
        layout.addWidget(self.text_input)
        layout.addWidget(self.progress)
        layout.addWidget(self.checkbox)
        layout.addStretch()
    
    def update_preview(self):
        """Update preview with current theme"""
        # The preview will automatically update when the global stylesheet changes
        pass

class ThemeSettingsDialog(QDialog):
    """Complete theme settings dialog with live preview and customization"""
    
    theme_applied = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Settings")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        self._color_pickers = {}
        self._font_controls = {}
        self._current_theme_id = theme_manager.get_current_theme_id() if theme_manager else "default_dark"
        
        self._setup_ui()
        self._load_current_settings()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("🎨 Theme Settings")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side - Settings
        settings_widget = self._create_settings_widget()
        splitter.addWidget(settings_widget)
        
        # Right side - Preview
        preview_widget = self._create_preview_widget()
        splitter.addWidget(preview_widget)
        
        splitter.setSizes([600, 300])
        
        # Bottom buttons
        buttons_layout = self._create_buttons_layout()
        main_layout.addLayout(buttons_layout)
    
    def _create_settings_widget(self) -> QWidget:
        """Create the main settings widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tab widget for different settings sections
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Themes tab
        themes_tab = self._create_themes_tab()
        self.tab_widget.addTab(themes_tab, "🎭 Themes")
        
        # Colors tab
        colors_tab = self._create_colors_tab()
        self.tab_widget.addTab(colors_tab, "🎨 Colors")
        
        # Fonts tab
        fonts_tab = self._create_fonts_tab()
        self.tab_widget.addTab(fonts_tab, "🔤 Fonts")
        
        # Advanced tab
        advanced_tab = self._create_advanced_tab()
        self.tab_widget.addTab(advanced_tab, "⚙️ Advanced")
        
        return widget
    
    def _create_themes_tab(self) -> QWidget:
        """Create themes selection tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme selection
        theme_group = QGroupBox("Select Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme combo
        theme_select_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setMinimumWidth(80)
        theme_select_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        themes = get_available_themes()
        for theme in themes:
            self.theme_combo.addItem(theme["name"], theme["id"])
        
        theme_select_layout.addWidget(self.theme_combo)
        theme_select_layout.addStretch()
        theme_layout.addLayout(theme_select_layout)
        
        # Theme description
        self.theme_description = QLabel()
        self.theme_description.setWordWrap(True)
        self.theme_description.setStyleSheet("color: #888888; font-style: italic; margin: 10px 0;")
        theme_layout.addWidget(self.theme_description)
        
        layout.addWidget(theme_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.reset_colors_btn = QPushButton("Reset Color Customizations")
        self.reset_fonts_btn = QPushButton("Reset Font Customizations")
        self.reset_all_btn = QPushButton("Reset All Customizations")
        
        actions_layout.addWidget(self.reset_colors_btn)
        actions_layout.addWidget(self.reset_fonts_btn)
        actions_layout.addWidget(self.reset_all_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return widget
    
    def _create_colors_tab(self) -> QWidget:
        """Create color customization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area for color pickers
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        colors_container = QWidget()
        colors_layout = QGridLayout(colors_container)
        
        # Color pickers for main theme colors
        colors = [
            ("Primary", "primary"),
            ("Primary Light", "primary_light"),
            ("Primary Dark", "primary_dark"),
            ("Secondary", "secondary"),
            ("Success", "success"),
            ("Warning", "warning"),
            ("Error", "error"),
            ("Background", "background"),
            ("Surface", "surface"),
            ("Border", "border"),
            ("Text Primary", "text_primary"),
            ("Text Secondary", "text_secondary"),
            ("Text Disabled", "text_disabled")
        ]
        
        for i, (label, key) in enumerate(colors):
            row = i // 2
            col = (i % 2) * 2
            
            # Label
            color_label = QLabel(f"{label}:")
            color_label.setMinimumWidth(120)
            colors_layout.addWidget(color_label, row, col)
            
            # Color picker
            picker = ColorPickerButton()
            self._color_pickers[key] = picker
            colors_layout.addWidget(picker, row, col + 1)
        
        scroll.setWidget(colors_container)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_fonts_tab(self) -> QWidget:
        """Create font customization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font family
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout(font_group)
        
        self.font_family_combo = QFontComboBox()
        font_layout.addRow("Font Family:", self.font_family_combo)
        
        # Font sizes
        self.h1_size_spin = QSpinBox()
        self.h1_size_spin.setRange(10, 48)
        font_layout.addRow("H1 Size:", self.h1_size_spin)
        
        self.h2_size_spin = QSpinBox()
        self.h2_size_spin.setRange(8, 36)
        font_layout.addRow("H2 Size:", self.h2_size_spin)
        
        self.body_size_spin = QSpinBox()
        self.body_size_spin.setRange(8, 24)
        font_layout.addRow("Body Size:", self.body_size_spin)
        
        self.caption_size_spin = QSpinBox()
        self.caption_size_spin.setRange(6, 18)
        font_layout.addRow("Caption Size:", self.caption_size_spin)
        
        layout.addWidget(font_group)
        layout.addStretch()
        
        return widget
    
    def _create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Restart settings
        restart_group = QGroupBox("Application Restart")
        restart_layout = QVBoxLayout(restart_group)
        
        self.auto_restart_checkbox = QCheckBox("Automatically restart when theme changes")
        restart_layout.addWidget(self.auto_restart_checkbox)
        
        restart_info = QLabel(
            "When enabled, the application will prompt for restart after theme changes "
            "to ensure all components are properly styled."
        )
        restart_info.setWordWrap(True)
        restart_info.setStyleSheet("color: #888888; font-style: italic; margin: 10px 0;")
        restart_layout.addWidget(restart_info)
        
        layout.addWidget(restart_group)
        
        # Debug info
        debug_group = QGroupBox("Debug Information")
        debug_layout = QVBoxLayout(debug_group)
        
        self.current_theme_label = QLabel()
        self.theme_config_text = QTextEdit()
        self.theme_config_text.setMaximumHeight(150)
        self.theme_config_text.setReadOnly(True)
        
        debug_layout.addWidget(self.current_theme_label)
        debug_layout.addWidget(self.theme_config_text)
        
        layout.addWidget(debug_group)
        layout.addStretch()
        
        return widget
    
    def _create_preview_widget(self) -> QWidget:
        """Create preview widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Preview title
        preview_title = QLabel("Live Preview")
        preview_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preview_title)
        
        # Preview area
        self.preview_widget = ThemePreviewWidget()
        preview_frame = ModernFrame()
        preview_frame_layout = QVBoxLayout(preview_frame)
        preview_frame_layout.addWidget(self.preview_widget)
        layout.addWidget(preview_frame)
        
        return widget
    
    def _create_buttons_layout(self) -> QHBoxLayout:
        """Create bottom buttons layout"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        # Apply button
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.setMinimumWidth(120)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6CC084, stop:1 #5CB074);
                border: 1px solid #5CB074;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7CD094, stop:1 #6CC084);
            }
        """)
        layout.addWidget(self.apply_btn)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setMinimumWidth(120)
        layout.addWidget(self.close_btn)
        
        return layout
    
    def _connect_signals(self):
        """Connect all signals"""
        # Theme selection
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        
        # Color pickers
        for key, picker in self._color_pickers.items():
            picker.color_changed.connect(lambda color, k=key: self._on_color_changed(k, color))
        
        # Font controls
        self.font_family_combo.currentFontChanged.connect(self._on_font_changed)
        self.h1_size_spin.valueChanged.connect(self._on_font_changed)
        self.h2_size_spin.valueChanged.connect(self._on_font_changed)
        self.body_size_spin.valueChanged.connect(self._on_font_changed)
        self.caption_size_spin.valueChanged.connect(self._on_font_changed)
        
        # Buttons
        self.apply_btn.clicked.connect(self._apply_changes)
        self.close_btn.clicked.connect(self.close)
        
        # Reset buttons
        self.reset_colors_btn.clicked.connect(self._reset_colors)
        self.reset_fonts_btn.clicked.connect(self._reset_fonts)
        self.reset_all_btn.clicked.connect(self._reset_all)
        
        # Auto restart checkbox
        self.auto_restart_checkbox.toggled.connect(self._on_auto_restart_changed)
        
        # Theme manager signals
        theme_manager.theme_changed.connect(self._on_theme_manager_changed)
    
    def _load_current_settings(self):
        """Load current theme settings into UI"""
        if not theme_manager:
            return
            
        # Load current theme
        current_theme_id = theme_manager.get_current_theme_id()
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme_id:
                self.theme_combo.setCurrentIndex(i)
                break
        
        self._update_theme_description()
        
        # Load current colors
        current_config = theme_manager.get_current_config()
        colors = current_config.get("colors", {})
        for key, picker in self._color_pickers.items():
            if key in colors:
                picker.set_color(colors[key])
        
        # Load current fonts
        fonts = current_config.get("fonts", {})
        if "primary" in fonts:
            font = QFont()
            font.setFamily(fonts["primary"])
            self.font_family_combo.setCurrentFont(font)
        
        self.h1_size_spin.setValue(fonts.get("h1_size", 24))
        self.h2_size_spin.setValue(fonts.get("h2_size", 18))
        self.body_size_spin.setValue(fonts.get("body_size", 12))
        self.caption_size_spin.setValue(fonts.get("caption_size", 10))
        
        # Load auto restart setting
        auto_restart = should_auto_restart_on_theme_change()
        self.auto_restart_checkbox.setChecked(bool(auto_restart))
        
        # Update debug info
        self._update_debug_info()
    
    def _on_theme_changed(self, index: int):
        """Handle theme selection change"""
        theme_id = self.theme_combo.itemData(index)
        if theme_id != self._current_theme_id:
            self._update_theme_description()
            # Preview theme change without applying
            self._preview_theme(theme_id)
    
    def _update_theme_description(self):
        """Update theme description label"""
        current_data = self.theme_combo.currentData()
        themes = get_available_themes()
        for theme in themes:
            if theme["id"] == current_data:
                self.theme_description.setText(theme["description"])
                break
    
    def _preview_theme(self, theme_id: str):
        """Preview theme without applying permanently"""
        # Temporarily apply theme for preview
        theme_manager.apply_theme(theme_id, prompt_restart=False)
        self.preview_widget.update_preview()
    
    def _on_color_changed(self, color_key: str, color: str):
        """Handle color change"""
        # Apply color change immediately for preview
        color_overrides = {color_key: color}
        theme_manager.update_colors(color_overrides, prompt_restart=False)
        self.preview_widget.update_preview()
    
    def _on_font_changed(self):
        """Handle font change"""
        # Apply font change immediately for preview
        font_overrides = {
            "primary": self.font_family_combo.currentFont().family(),
            "h1_size": self.h1_size_spin.value(),
            "h2_size": self.h2_size_spin.value(),
            "body_size": self.body_size_spin.value(),
            "caption_size": self.caption_size_spin.value()
        }
        theme_manager.update_fonts(font_overrides, prompt_restart=False)
        self.preview_widget.update_preview()
    
    def _on_auto_restart_changed(self, checked: bool):
        """Handle auto restart setting change"""
        from utils.settings import set_theme_setting
        set_theme_setting("auto_restart_on_theme_change", checked)
    
    def _on_theme_manager_changed(self, theme_id: str):
        """Handle external theme change"""
        self._current_theme_id = theme_id
        self._load_current_settings()
    
    def _apply_changes(self):
        """Apply all changes permanently"""
        # Apply selected theme
        theme_id = self.theme_combo.currentData()
        if theme_id != self._current_theme_id:
            theme_manager.apply_theme(theme_id)
            self._current_theme_id = theme_id
        
        # Apply color customizations
        color_overrides = {}
        for key, picker in self._color_pickers.items():
            current_color = theme_manager.get_color(key)
            if picker.get_color() != current_color:
                color_overrides[key] = picker.get_color()
        
        if color_overrides:
            theme_manager.update_colors(color_overrides)
        
        # Apply font customizations
        font_overrides = {
            "primary": self.font_family_combo.currentFont().family(),
            "h1_size": self.h1_size_spin.value(),
            "h2_size": self.h2_size_spin.value(),
            "body_size": self.body_size_spin.value(),
            "caption_size": self.caption_size_spin.value()
        }
        theme_manager.update_fonts(font_overrides)
        
        self.theme_applied.emit(theme_id)
        
        # Show success message
        QMessageBox.information(
            self,
            "Theme Applied",
            "Theme has been applied successfully!"
        )
    
    def _reset_colors(self):
        """Reset color customizations"""
        reply = QMessageBox.question(
            self,
            "Reset Colors",
            "Are you sure you want to reset all color customizations?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            theme_manager.reset_customizations(prompt_restart=False)
            self._load_current_settings()
            self.preview_widget.update_preview()
    
    def _reset_fonts(self):
        """Reset font customizations"""
        reply = QMessageBox.question(
            self,
            "Reset Fonts",
            "Are you sure you want to reset all font customizations?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            theme_manager.reset_customizations(prompt_restart=False)
            self._load_current_settings()
            self.preview_widget.update_preview()
    
    def _reset_all(self):
        """Reset all customizations"""
        reply = QMessageBox.question(
            self,
            "Reset All",
            "Are you sure you want to reset all theme customizations?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            theme_manager.reset_customizations(prompt_restart=False)
            self._load_current_settings()
            self.preview_widget.update_preview()
    
    def _update_debug_info(self):
        """Update debug information display"""
        current_config = theme_manager.get_current_config()
        current_theme_id = theme_manager.get_current_theme_id()
        
        self.current_theme_label.setText(f"Current Theme: {current_theme_id}")
        
        # Format config for display
        config_text = f"Theme Configuration:\n\n"
        config_text += f"Name: {current_config.get('name', 'Unknown')}\n"
        config_text += f"Description: {current_config.get('description', 'No description')}\n\n"
        
        colors = current_config.get('colors', {})
        config_text += "Colors:\n"
        for key, value in list(colors.items())[:5]:  # Show first 5 colors
            config_text += f"  {key}: {value}\n"
        config_text += "  ...\n\n"
        
        fonts = current_config.get('fonts', {})
        config_text += "Fonts:\n"
        for key, value in fonts.items():
            config_text += f"  {key}: {value}\n"
        
        self.theme_config_text.setPlainText(config_text)