"""
Theme Asset Manager
Gerencia assets dinâmicos baseados no tema selecionado (GIFs para ACCELA, SVGs para Bifrost)
"""

import os
import logging
from typing import Optional, Dict, Any
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QSize

logger = logging.getLogger(__name__)


class ThemeAssetManager:
    """Gerenciador de assets que muda baseado no tema ativo"""
    
    def __init__(self):
        self.current_theme = "ACCELA Identity"
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Mapeamento de assets por tema
        self.asset_mapping = {
            "main_logo": {
                "ACCELA Identity": "assets/gifs/main.gif",
                "Bifrost": "assets/bifrost/BIFROST.png"
            },
            "downloading": {
                "ACCELA Identity": "assets/gifs/main.gif",
                "Bifrost": "assets/bifrost/bifrost-downloading.svg"
            },
            "navigation": {
                "ACCELA Identity": "assets/gifs/navi.gif",
                "Bifrost": "assets/bifrost/bifrost-downloading.svg"  # Temporário
            }
        }
        
    def set_theme(self, theme_name: str):
        """Define o tema atual"""
        self.current_theme = theme_name
        logger.debug(f"Theme asset manager set to: {theme_name}")
        
    def get_asset_path(self, asset_key: str) -> Optional[str]:
        """Retorna o caminho do asset baseado no tema atual"""
        if asset_key not in self.asset_mapping:
            logger.warning(f"Asset key '{asset_key}' not found in mapping")
            return None
            
        theme_assets = self.asset_mapping[asset_key]
        asset_path = theme_assets.get(self.current_theme)
        
        if not asset_path:
            # Fallback para tema ACCELA se não encontrar no tema atual
            asset_path = theme_assets.get("ACCELA Identity")
            logger.warning(f"Asset '{asset_key}' not found for theme '{self.current_theme}', using ACCELA fallback")
            
        if asset_path:
            full_path = os.path.join(self.base_path, asset_path)
            if os.path.exists(full_path):
                return full_path
            else:
                logger.error(f"Asset file not found: {full_path}")
                return None
        else:
            logger.error(f"No asset path found for '{asset_key}' in theme '{self.current_theme}'")
            return None
            
    def create_logo_label(self, size: Optional[QSize] = None) -> QLabel:
        """Cria QLabel com o logo do tema atual"""
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        asset_path = self.get_asset_path("main_logo")
        if not asset_path:
            logger.error("Could not load main logo")
            return label
            
        try:
            if asset_path.endswith('.svg'):
                # Para SVG, usar QPixmap
                pixmap = QPixmap(asset_path)
                if size is not None:
                    # Scale SVG while maintaining aspect ratio and centering
                    scaled_pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    label.setPixmap(scaled_pixmap)
                else:
                    label.setPixmap(pixmap)
            else:
                # Para GIF/PNG, usar QPixmap
                pixmap = QPixmap(asset_path)
                if size is not None:
                    scaled_pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    label.setPixmap(scaled_pixmap)
                else:
                    label.setPixmap(pixmap)
        except Exception as e:
            logger.error(f"Error loading asset {asset_path}: {e}")
            # Create fallback colored rectangle
            from PyQt6.QtGui import QPainter, QColor
            fallback_size = size if size is not None else QSize(100, 100)
            fallback_pixmap = QPixmap(fallback_size)
            from ui.theme import get_current_theme
            theme = get_current_theme()
            fallback_pixmap.fill(QColor(theme.colors.PRIMARY))
            label.setPixmap(fallback_pixmap)
            
        if size is not None:
            label.setFixedSize(size)
            
        return label
        
    def create_downloading_animation(self, parent=None) -> QLabel:
        """Cria QLabel com animação de download do tema atual"""
        label = QLabel(parent)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        asset_path = self.get_asset_path("downloading")
        if not asset_path:
            logger.error("Could not load downloading animation")
            return label
            
        if asset_path.endswith('.gif'):
            # Para GIF, usar QMovie
            movie = QMovie(asset_path)
            label.setMovie(movie)
            movie.start()
        elif asset_path.endswith('.svg'):
            # Para SVG, usar QPixmap (estático por enquanto)
            pixmap = QPixmap(asset_path)
            label.setPixmap(pixmap)
        else:
            # Para outros formatos
            pixmap = QPixmap(asset_path)
            label.setPixmap(pixmap)
            
        return label
        
    def create_navigation_animation(self, parent=None) -> QLabel:
        """Cria QLabel com animação de navegação do tema atual"""
        label = QLabel(parent)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        asset_path = self.get_asset_path("navigation")
        if not asset_path:
            logger.error("Could not load navigation animation")
            return label
            
        if asset_path.endswith('.gif'):
            # Para GIF, usar QMovie
            movie = QMovie(asset_path)
            label.setMovie(movie)
            movie.start()
        elif asset_path.endswith('.svg'):
            # Para SVG, usar QPixmap (estático por enquanto)
            pixmap = QPixmap(asset_path)
            label.setPixmap(pixmap)
        else:
            # Para outros formatos
            pixmap = QPixmap(asset_path)
            label.setPixmap(pixmap)
            
        return label
        
    def get_theme_stylesheet(self) -> str:
        """Retorna stylesheet específico do tema atual"""
        from .theme import get_current_theme
        theme = get_current_theme()
        return theme.get_dialog_stylesheet()
            
    def apply_theme_to_widget(self, widget):
        """Aplica o tema atual a um widget específico"""
        from .theme import get_current_theme
        theme = get_current_theme()
        widget.setStyleSheet(theme.get_dialog_stylesheet())


# Instância global do gerenciador de assets
asset_manager = ThemeAssetManager()


def get_asset_manager() -> ThemeAssetManager:
    """Retorna a instância global do gerenciador de assets"""
    return asset_manager


def set_current_theme(theme_name: str):
    """Define o tema atual no gerenciador de assets"""
    asset_manager.set_theme(theme_name)


def get_theme_asset_path(asset_key: str) -> Optional[str]:
    """Retorna o caminho do asset baseado no tema atual"""
    return asset_manager.get_asset_path(asset_key)


def create_theme_logo(size: Optional[QSize] = None) -> QLabel:
    """Cria QLabel com o logo do tema atual"""
    return asset_manager.create_logo_label(size)


def create_theme_downloading_animation(parent=None) -> QLabel:
    """Cria QLabel com animação de download do tema atual"""
    return asset_manager.create_downloading_animation(parent)


def create_theme_navigation_animation(parent=None) -> QLabel:
    """Cria QLabel com animação de navegação do tema atual"""
    return asset_manager.create_navigation_animation(parent)