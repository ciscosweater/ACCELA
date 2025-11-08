import logging
import re
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSizeGrip, QLabel, QSpacerItem, QSizePolicy, QWidget
from PyQt6.QtGui import QIcon, QPainter, QPixmap, QMouseEvent, QColor, QMovie
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtSvg import QSvgRenderer
from .assets import GEAR_SVG, POWER_SVG

logger = logging.getLogger(__name__)

class CustomTitleBar(QFrame):
    """
    A custom, frameless title bar with SVG buttons for settings and closing.
    This is placed at the bottom of the main window as requested.
    It also handles window dragging and resizing.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.drag_pos = None
        self.setFixedHeight(22)
        self.setStyleSheet("background-color: #000000;")
        logger.debug("CustomTitleBar initialized.")

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 2, 0)
        layout.setSpacing(5)

        # Create containers for left and right elements to properly balance them.
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        
        self.navi_label = QLabel()
        self.navi_movie = QMovie("assets/gifs/navi.gif")
        if self.navi_movie.isValid():
            self.navi_label.setMovie(self.navi_movie)
            self.navi_movie.start()
            
            original_size = self.navi_movie.currentPixmap().size()
            target_height = 20
            
            if original_size.height() > 0:
                aspect_ratio = original_size.width() / original_size.height()
                target_width = int(target_height * aspect_ratio)
                scaled_size = QSize(target_width, target_height)
                
                self.navi_movie.setScaledSize(scaled_size)
                self.navi_label.setMinimumWidth(target_width)
        else:
            logger.warning("Could not load navi.gif.")
        left_layout.addWidget(self.navi_label)
        
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(2)
        
        # Add select file button
        self.select_file_button = self._create_text_button("ZIP", parent._select_zip_file, "Select ZIP File")
        right_layout.addWidget(self.select_file_button)
        
        # Add game manager button
        self.game_manager_button = self._create_text_button("UN", parent._open_game_manager, "Uninstall Games")
        right_layout.addWidget(self.game_manager_button)
        
        self.settings_button = self._create_svg_button(GEAR_SVG, parent.open_settings, "Open Settings")
        right_layout.addWidget(self.settings_button)

        self.close_button = self._create_svg_button(POWER_SVG, parent.close, "Close Application")
        right_layout.addWidget(self.close_button)

        # Main layout assembly
        layout.addWidget(left_widget)
        layout.addStretch(1)
        self.title_label = QLabel("ACCELA")
        self.title_label.setStyleSheet("color: #C06C84; font-size: 14pt;")
        layout.addWidget(self.title_label)
        layout.addStretch(1)
        layout.addWidget(right_widget)
        
        # Balance the layout by setting the containers to equal width
        left_width = left_widget.sizeHint().width()
        right_width = right_widget.sizeHint().width()
        if left_width > right_width:
            right_widget.setMinimumWidth(left_width)
        else:
            left_widget.setMinimumWidth(right_width)

        self.setLayout(layout)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Captures the initial mouse press event to start dragging the window.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Moves the window as the mouse is dragged.
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.parent.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Resets the drag position when the mouse button is released.
        """
        self.drag_pos = None
        event.accept()

    def _create_svg_button(self, svg_data, on_click, tooltip):
        """
        Helper method to create a button from SVG data, recoloring the icon without distortion.
        """
        try:
            button = QPushButton()
            button.setToolTip(tooltip)
            
            renderer = QSvgRenderer(svg_data.encode('utf-8'))
            icon_size = QSize(16, 16)

            pixmap = QPixmap(icon_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            renderer.render(painter)
            
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            
            painter.fillRect(pixmap.rect(), QColor("#C06C84"))
            
            painter.end()

            icon = QIcon(pixmap)
            
            button.setIcon(icon)
            button.setIconSize(icon_size)
            button.setFixedSize(18, 18)
            button.setStyleSheet("QPushButton { border: none; } QPushButton:hover { background-color: #282828; }")
            button.clicked.connect(on_click)
            return button
        except Exception as e:
            logger.error(f"Failed to create SVG button: {e}", exc_info=True)
            fallback_button = QPushButton("X")
            fallback_button.setFixedSize(18, 18)
            fallback_button.clicked.connect(on_click)
            return fallback_button
    
    def _create_text_button(self, text, on_click, tooltip):
        """
        Helper method to create a simple text button.
        """
        try:
            button = QPushButton(text)
            button.setToolTip(tooltip)
            button.setFixedSize(18, 18)
            button.setStyleSheet("""
                QPushButton { 
                    border: none; 
                    color: #C06C84; 
                    font-size: 10px; 
                    font-weight: bold;
                } 
                QPushButton:hover { 
                    background-color: #282828; 
                }
            """)
            button.clicked.connect(on_click)
            return button
        except Exception as e:
            logger.error(f"Failed to create text button: {e}", exc_info=True)
            fallback_button = QPushButton("?")
            fallback_button.setFixedSize(18, 18)
            fallback_button.clicked.connect(on_click)
            return fallback_button
