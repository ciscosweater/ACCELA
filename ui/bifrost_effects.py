"""
Bifrost Theme Special Effects
Magical particles, portal transitions, and enhanced visual effects
"""

import logging
import random
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtSignal, QObject, QEasingCurve
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QPixmap

logger = logging.getLogger(__name__)


class MagicParticle(QWidget):
    """A single magical particle with floating animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(6, 6)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Random particle properties
        self.color = QColor(
            random.randint(100, 255),
            random.randint(100, 255), 
            random.randint(150, 255),
            random.randint(100, 200)
        )
        self.float_offset = random.uniform(0, 360)
        self.float_speed = random.uniform(1, 3)
        self.particle_size = random.uniform(3, 6)
        
        # Animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_position)
        self.animation_timer.start(50)
        
        self.time = 0
        
    def _update_position(self):
        """Update particle position with floating effect"""
        self.time += 0.1
        
        # Calculate floating position
        x_offset = 20 * (self.time + self.float_offset)
        y_offset = 15 * (self.time * self.float_speed + self.float_offset)
        
        # Simple floating animation without parent dependency
        new_x = 50 + 30 * (self.time + self.float_offset) % 100
        new_y = 30 + 20 * (self.time * self.float_speed + self.float_offset) % 80
        
        self.move(int(new_x), int(new_y))
        self.update()
        
    def paintEvent(self, a0):
        """Draw the particle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create solid effect
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, int(self.particle_size), int(self.particle_size))


class ParticleEffect(QWidget):
    """Container for multiple magical particles"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.particles = []
        self._create_particles()
        
    def _create_particles(self):
        """Create magical particles"""
        for _ in range(8):
            particle = MagicParticle(self)
            particle.show()
            self.particles.append(particle)
            
    def resizeEvent(self, a0):
        """Handle resize events"""
        super().resizeEvent(a0)
        # Redistribute particles on resize
        for particle in self.particles:
            particle.move(
                random.randint(0, max(1, self.width() - 10)),
                random.randint(0, max(1, self.height() - 10))
            )


class PortalTransition(QObject):
    """Portal-like transition effect for widgets"""
    
    finished = pyqtSignal()
    
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.animation = QPropertyAnimation(widget, b"geometry")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.finished.connect(self.finished.emit)
        
    def start_portal_in(self):
        """Start portal entrance animation"""
        if not self.widget:
            return
            
        # Get final geometry
        final_geometry = self.widget.geometry()
        center_x = final_geometry.x() + final_geometry.width() // 2
        center_y = final_geometry.y() + final_geometry.height() // 2
        
        # Start from center point (portal effect)
        start_geometry = QRect(center_x, center_y, 1, 1)
        
        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(final_geometry)
        self.animation.start()
        
    def start_portal_out(self):
        """Start portal exit animation"""
        if not self.widget:
            return
            
        # Get current geometry
        current_geometry = self.widget.geometry()
        center_x = current_geometry.x() + current_geometry.width() // 2
        center_y = current_geometry.y() + current_geometry.height() // 2
        
        # End at center point (portal effect)
        end_geometry = QRect(center_x, center_y, 1, 1)
        
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(end_geometry)
        self.animation.start()


class BifrostProgressBar(QWidget):
    """Enhanced progress bar with solid color and magical effects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setMinimumWidth(200)
        
        self.value = 0
        self.maximum = 100
        self.text_visible = True
        
        # Particle effect
        self.particle_effect = ParticleEffect(self)
        self.particle_effect.hide()
    
    def _get_current_theme(self):
        """Get current theme instance"""
        try:
            from ui.theme import get_current_theme
            return get_current_theme()
        except ImportError:
            # Fallback to basic theme if import fails
            class FallbackTheme:
                class colors:
                    SURFACE_DARK = QColor(26, 26, 27)
                    ERROR = QColor(255, 107, 107)
                    SUCCESS = QColor(78, 205, 196)
                    PRIMARY = QColor(69, 183, 209)
                    SUCCESS_LIGHT = QColor(150, 206, 180)
                    WARNING = QColor(255, 234, 167)
                    TEXT_PRIMARY = QColor(232, 232, 232)
            return FallbackTheme()
        
    def setValue(self, value):
        """Set progress value"""
        self.value = max(0, min(value, self.maximum))
        self.update()
        
    def setMaximum(self, maximum):
        """Set maximum value"""
        self.maximum = maximum
        self.update()
        
    def setTextVisible(self, visible):
        """Set text visibility"""
        self.text_visible = visible
        self.update()
        
    def show_particles(self, show=True):
        """Show/hide particle effect"""
        if show:
            self.particle_effect.setGeometry(self.rect())
            self.particle_effect.show()
        else:
            self.particle_effect.hide()
            
    def paintEvent(self, a0):
        """Draw the progress bar with solid color"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get current theme
        current_theme = self._get_current_theme()
        
        # Background
        painter.fillRect(self.rect(), QColor(current_theme.colors.SURFACE_DARK))
        
        # Calculate progress
        if self.maximum > 0:
            progress_ratio = self.value / self.maximum
        else:
            progress_ratio = 0
            
        progress_width = int(self.width() * progress_ratio)
        
        if progress_width > 0:
            # Solid color for progress
            painter.fillRect(0, 0, progress_width, self.height(), QColor(current_theme.colors.PRIMARY))
            
        # Border
        painter.setPen(QPen(QColor(current_theme.colors.PRIMARY), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 4, 4)
        
        # Text
        if self.text_visible:
            painter.setPen(QPen(QColor(current_theme.colors.TEXT_PRIMARY)))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            
            percentage = int(progress_ratio * 100)
            text = f"{percentage}%"
            
            text_rect = self.rect()
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)


class BifrostGlowEffect(QWidget):
    """Glowing effect for interactive elements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.glow_intensity = 0
        self.target_intensity = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_glow)
        self.animation_timer.start(30)
    
    def _get_current_theme(self):
        """Get current theme instance"""
        try:
            from ui.theme import get_current_theme
            return get_current_theme()
        except ImportError:
            # Fallback to basic theme if import fails
            class FallbackTheme:
                class colors:
                    PRIMARY = QColor(74, 144, 226)
            return FallbackTheme()
        
    def set_glow(self, intensity):
        """Set glow intensity (0-100)"""
        self.target_intensity = max(0, min(intensity, 100))
        
    def _update_glow(self):
        """Update glow animation"""
        if abs(self.glow_intensity - self.target_intensity) > 1:
            self.glow_intensity += (self.target_intensity - self.glow_intensity) * 0.1
            self.update()
        else:
            self.glow_intensity = self.target_intensity
            
    def paintEvent(self, a0):
        """Draw glow effect"""
        if self.glow_intensity <= 0:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get current theme
        current_theme = self._get_current_theme()
        
        # Create glow color with alpha based on intensity
        alpha = int(self.glow_intensity * 0.3)
        glow_color = QColor(current_theme.colors.PRIMARY)
        glow_color.setAlpha(alpha)
        
        painter.setPen(QPen(glow_color, 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 6, 6)


class BifrostEffectsManager:
    """Manager for Bifrost theme special effects"""
    
    @staticmethod
    def apply_portal_transition(widget, direction="in"):
        """Apply portal transition to widget"""
        transition = PortalTransition(widget)
        
        if direction == "in":
            transition.start_portal_in()
        else:
            transition.start_portal_out()
            
        return transition
        
    @staticmethod
    def create_magical_progress_bar(parent=None):
        """Create a magical progress bar with rainbow effects"""
        return BifrostProgressBar(parent)
        
    @staticmethod
    def add_glow_effect(widget):
        """Add glow effect to widget"""
        glow = BifrostGlowEffect(widget)
        glow.setGeometry(widget.rect())
        glow.show()
        return glow
        
    @staticmethod
    def add_particle_effect(parent):
        """Add particle effect to parent widget"""
        particles = ParticleEffect(parent)
        particles.setGeometry(parent.rect())
        particles.show()
        return particles