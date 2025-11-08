"""
Image Cache Manager - Cache system for game header images
"""
import os
import hashlib
import logging
import requests
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)

class ImageCacheManager(QObject):
    """Manages caching of game header images"""
    
    # Signals
    image_cached = pyqtSignal(str, str)  # app_id, cache_path
    cache_error = pyqtSignal(str, str)   # app_id, error_message
    
    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__()
        
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "accela", "images")
        
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache settings
        self.max_cache_size_mb = 100  # Maximum cache size in MB
        self.max_age_days = 30        # Maximum age of cached images
        
        logger.info(f"Image cache initialized at: {self.cache_dir}")
    
    def get_cache_path(self, app_id: str, url: str) -> str:
        """Generate cache file path for an app"""
        # Create hash from URL to handle URL changes
        url_hash = hashlib.md5(url.encode()).hexdigest()
        filename = f"{app_id}_{url_hash}.jpg"
        return os.path.join(self.cache_dir, filename)
    
    def is_cached(self, app_id: str, url: str) -> bool:
        """Check if image is cached and valid"""
        cache_path = self.get_cache_path(app_id, url)
        
        if not os.path.exists(cache_path):
            return False
        
        # Check file age
        import time
        file_age = time.time() - os.path.getmtime(cache_path)
        max_age_seconds = self.max_age_days * 24 * 3600
        
        if file_age > max_age_seconds:
            logger.debug(f"Cached image expired for app {app_id}")
            os.remove(cache_path)
            return False
        
        # Check file size (should be greater than 0)
        if os.path.getsize(cache_path) == 0:
            logger.debug(f"Cached image is empty for app {app_id}")
            os.remove(cache_path)
            return False
        
        return True
    
    def get_cached_image(self, app_id: str, url: str) -> Optional[QPixmap]:
        """Get cached image if available"""
        if not self.is_cached(app_id, url):
            return None
        
        cache_path = self.get_cache_path(app_id, url)
        
        try:
            pixmap = QPixmap(cache_path)
            if not pixmap.isNull():
                logger.debug(f"Loaded cached image for app {app_id}")
                return pixmap
            else:
                logger.warning(f"Cached image is corrupted for app {app_id}")
                os.remove(cache_path)
                return None
        except Exception as e:
            logger.error(f"Error loading cached image for app {app_id}: {e}")
            return None
    
    def cache_image(self, app_id: str, url: str, image_data: bytes) -> bool:
        """Cache image data"""
        try:
            cache_path = self.get_cache_path(app_id, url)
            
            with open(cache_path, 'wb') as f:
                f.write(image_data)
            
            logger.debug(f"Cached image for app {app_id}: {len(image_data)} bytes")
            self.image_cached.emit(app_id, cache_path)
            
            # Clean up old cache if needed
            self._cleanup_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Error caching image for app {app_id}: {e}")
            self.cache_error.emit(app_id, str(e))
            return False
    
    def download_and_cache(self, app_id: str, url: str, timeout: int = 10) -> Optional[QPixmap]:
        """Download image and cache it"""
        try:
            logger.debug(f"Downloading image for app {app_id}: {url}")
            
            headers = {
                'User-Agent': 'ACCELA/1.0 (Steam Game Manager)'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Create pixmap from downloaded data first
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            # Cache the image
            if self.cache_image(app_id, url, response.content):
                return pixmap
            
            if not pixmap.isNull():
                logger.debug(f"Successfully downloaded image for app {app_id}")
                return pixmap
            else:
                logger.warning(f"Downloaded image is invalid for app {app_id}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error downloading image for app {app_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading image for app {app_id}: {e}")
            return None
    
    def _cleanup_cache(self):
        """Clean up old cache files if cache is too large"""
        try:
            # Calculate current cache size
            total_size = 0
            cache_files = []
            
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    mtime = os.path.getmtime(filepath)
                    cache_files.append((filepath, size, mtime))
                    total_size += size
            
            # Convert to MB
            total_size_mb = total_size / (1024 * 1024)
            
            if total_size_mb <= self.max_cache_size_mb:
                return
            
            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda x: x[2])
            
            # Remove oldest files until under limit
            target_size = self.max_cache_size_mb * 0.8 * 1024 * 1024  # 80% of max
            current_size = total_size
            
            removed_count = 0
            for filepath, size, mtime in cache_files:
                if current_size <= target_size:
                    break
                
                try:
                    os.remove(filepath)
                    current_size -= size
                    removed_count += 1
                    logger.debug(f"Removed old cache file: {filepath}")
                except Exception as e:
                    logger.warning(f"Error removing cache file {filepath}: {e}")
            
            if removed_count > 0:
                logger.info(f"Cache cleanup: removed {removed_count} files, freed {(total_size - current_size) / (1024 * 1024):.1f} MB")
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
    
    def clear_cache(self):
        """Clear all cached images"""
        try:
            removed_count = 0
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    removed_count += 1
            
            logger.info(f"Cleared image cache: removed {removed_count} files")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_size = 0
            file_count = 0
            
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
                    file_count += 1
            
            return {
                'file_count': file_count,
                'total_size_mb': total_size / (1024 * 1024),
                'cache_dir': self.cache_dir
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}


class ImageFetcher(QThread):
    """Thread for fetching game images with caching"""
    
    image_ready = pyqtSignal(str, object)  # app_id, QPixmap or None
    error_occurred = pyqtSignal(str, str)  # app_id, error_message
    
    def __init__(self, app_id: str, url: str, cache_manager: ImageCacheManager):
        super().__init__()
        self.app_id = app_id
        self.url = url
        self.cache_manager = cache_manager
    
    def run(self):
        """Fetch image with caching"""
        try:
            # Try cache first
            cached_image = self.cache_manager.get_cached_image(self.app_id, self.url)
            if cached_image:
                self.image_ready.emit(self.app_id, cached_image)
                return
            
            # Download and cache
            pixmap = self.cache_manager.download_and_cache(self.app_id, self.url)
            self.image_ready.emit(self.app_id, pixmap)
            
        except Exception as e:
            logger.error(f"Error in ImageFetcher for app {self.app_id}: {e}")
            self.error_occurred.emit(self.app_id, str(e))