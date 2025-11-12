import logging
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.theme import theme, Typography, Spacing
from ui.game_image_manager import GameImageManager
from utils.image_cache import ImageCacheManager

logger = logging.getLogger(__name__)

class GameImageDisplay(QObject):
    """
    Component to display game header image and info during download.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.game_header_image = None
        
        # Initialize enhanced image manager
        self.cache_manager = ImageCacheManager()
        self.image_manager = GameImageManager(self.cache_manager)
        
    def setup_game_image_area(self, main_layout):
        """Create and setup the game image display area."""
        
        # Game header image area (initially hidden)
        self.game_image_container = QFrame()
        self.game_image_container.setVisible(False)
        self.game_image_container.setStyleSheet(f"""
            QFrame {{
                background: {theme.colors.OVERLAY};
                border: 1px solid {theme.colors.PRIMARY};
                margin: {Spacing.SM}px;
                padding: {Spacing.SM}px;
            }}
        """)
        game_image_layout = QHBoxLayout(self.game_image_container)
        game_image_layout.setContentsMargins(10, 10, 10, 10)
        
        self.game_header_label = QLabel()
        self.game_header_label.setMinimumSize(184, 69)  # Steam header image aspect ratio
        self.game_header_label.setMaximumSize(184, 69)
        self.game_header_label.setStyleSheet(f"""
            QLabel {{
                border: 1px solid {theme.colors.PRIMARY};
                background: {theme.colors.BACKGROUND};
            }}
        """)
        game_image_layout.addWidget(self.game_header_label)
        
        # Game info next to image
        game_info_layout = QVBoxLayout()
        game_info_layout.setSpacing(Spacing.XS)
        
        self.game_title_label = QLabel("Game Title")
        self.game_title_label.setStyleSheet(f"""
            QLabel {{
                {Typography.get_font_style(Typography.H3_SIZE, Typography.WEIGHT_BOLD)};
                color: {theme.colors.PRIMARY};
                border: none;
            }}
        """)
        game_info_layout.addWidget(self.game_title_label)
        
        self.game_status_label = QLabel("Downloading...")
        self.game_status_label.setStyleSheet(f"""
            QLabel {{
                {Typography.get_font_style(Typography.BODY_SIZE)};
                color: {theme.colors.TEXT_SECONDARY};
                border: none;
            }}
        """)
        game_info_layout.addWidget(self.game_status_label)
        
        game_info_layout.addStretch()
        game_image_layout.addLayout(game_info_layout)
        
        main_layout.addWidget(self.game_image_container)
        
        return self.game_image_container
        
    def show_game_info(self, game_data):
        """Show game information area with header image."""
        if game_data:
            # Set game title
            game_name = game_data.get('game_name', 'Unknown Game')
            self.game_title_label.setText(game_name)
            
            # Show the game image container
            self.game_image_container.setVisible(True)
            
            # Fetch header image
            app_id = game_data.get('appid')
            if app_id:
                self._fetch_game_header_image(app_id)
                
    def hide_game_info(self):
        """Hide game information area."""
        self.game_image_container.setVisible(False)
        self.game_header_image = None
        
    def update_download_status(self, status):
        """Update the download status text."""
        self.game_status_label.setText(status)
        
    def _fetch_game_header_image(self, app_id):
        """Fetch game header image for display during download using enhanced manager."""
        # Use enhanced image manager with multiple fallbacks
        self.image_thread = self.image_manager.get_game_image(app_id, preferred_format="header")
        self.image_thread.image_ready.connect(self._on_enhanced_image_ready)
        self.image_thread.image_failed.connect(self._on_enhanced_image_error)

    def _on_enhanced_image_ready(self, app_id, pixmap, source_info):
        """Handle successfully fetched game image from enhanced manager."""
        if pixmap and not pixmap.isNull():
            self.game_header_image = pixmap
            self.game_header_label.setPixmap(pixmap.scaled(
                184, 69, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
            logger.debug(f"Loaded game image for app {app_id} from {source_info}")
        else:
            self.game_header_label.setText("[IMAGE]\nNo Image")
    
    def _on_enhanced_image_error(self, app_id, error_message):
        """Handle game image fetch error from enhanced manager."""
        logger.warning(f"Failed to fetch image for app {app_id}: {error_message}")
        self.game_header_label.setText("[IMAGE]\nNo Image")
    
    def on_game_image_fetched(self, image_data):
        """Handle fetched game header image (legacy method)."""
        if image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.game_header_image = pixmap
            self.game_header_label.setPixmap(pixmap.scaled(
                184, 69, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.game_header_label.setText("[IMAGE]\nNo Image")

class ImageFetcher(QObject):
    """Legacy ImageFetcher - kept for backward compatibility"""
    finished = pyqtSignal(bytes)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            import urllib.request
            with urllib.request.urlopen(self.url) as response:
                data = response.read()
                self.finished.emit(data)
        except Exception as e:
            logger.warning(f"Failed to fetch header image from {self.url}: {e}")
            self.finished.emit(b'')