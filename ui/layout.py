"""
Layout system for ACCELA application
Provides consistent spacing and layout utilities
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from .theme import theme, Spacing


class SpacingMixin:
    """
    Mixin class to provide spacing utilities to widgets
    """
    
    def set_margins(self, top=None, right=None, bottom=None, left=None):
        """Set widget margins with consistent spacing"""
        if all(v is None for v in [top, right, bottom, left]):
            self.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        else:
            t = top if top is not None else Spacing.MD
            r = right if right is not None else Spacing.MD
            b = bottom if bottom is not None else Spacing.MD
            l = left if left is not None else Spacing.MD
            self.setContentsMargins(t, r, b, l)
    
    def set_padding(self, size):
        """Set padding using content margins"""
        self.setContentsMargins(size, size, size, size)


class ModernVBoxLayout(QVBoxLayout):
    """
    Vertical layout with consistent spacing
    """
    
    def __init__(self, spacing=Spacing.MD, parent=None):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.setContentsMargins(0, 0, 0, 0)
    
    def add_spacing(self, size=Spacing.MD):
        """Add spacing item"""
        self.addSpacing(size)
    
    def add_stretch(self, stretch=1):
        """Add stretchable space"""
        self.addStretch(stretch)


class ModernHBoxLayout(QHBoxLayout):
    """
    Horizontal layout with consistent spacing
    """
    
    def __init__(self, spacing=Spacing.MD, parent=None):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.setContentsMargins(0, 0, 0, 0)
    
    def add_spacing(self, size=Spacing.MD):
        """Add spacing item"""
        self.addSpacing(size)
    
    def add_stretch(self, stretch=1):
        """Add stretchable space"""
        self.addStretch(stretch)


class ModernGridLayout(QGridLayout):
    """
    Grid layout with consistent spacing
    """
    
    def __init__(self, spacing=Spacing.MD, parent=None):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.setContentsMargins(0, 0, 0, 0)


class ModernContainer(QWidget, SpacingMixin):
    """
    Container widget with consistent spacing and styling
    """
    
    def __init__(self, layout_type="vertical", spacing=Spacing.MD, parent=None):
        super().__init__(parent)
        self._setup_layout(layout_type, spacing)
        self.set_margins()
        
    def _setup_layout(self, layout_type, spacing):
        """Setup layout based on type"""
        if layout_type == "vertical":
            self.layout = ModernVBoxLayout(spacing)
        elif layout_type == "horizontal":
            self.layout = ModernHBoxLayout(spacing)
        elif layout_type == "grid":
            self.layout = ModernGridLayout(spacing)
        else:
            self.layout = ModernVBoxLayout(spacing)
        
        self.setLayout(self.layout)


class CardContainer(ModernContainer):
    """
    Card container with modern styling
    """
    
    def __init__(self, layout_type="vertical", spacing=Spacing.MD, parent=None):
        super().__init__(layout_type, spacing, parent)
        self._setup_card_style()
        
    def _setup_card_style(self):
        """Apply card styling"""
        self.setStyleSheet(theme.components.CARD)


class SectionContainer(ModernContainer):
    """
    Section container with larger margins
    """
    
    def __init__(self, layout_type="vertical", spacing=Spacing.LG, parent=None):
        super().__init__(layout_type, spacing, parent)
        self.set_margins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)


class FormContainer(ModernContainer):
    """
    Form container with form-specific spacing
    """
    
    def __init__(self, spacing=Spacing.SM, parent=None):
        super().__init__("vertical", spacing, parent)
        self.set_margins(Spacing.LG, Spacing.XL, Spacing.LG, Spacing.XL)


class ButtonContainer(ModernContainer):
    """
    Container for buttons with consistent alignment
    """
    
    def __init__(self, alignment="right", spacing=Spacing.SM, parent=None):
        super().__init__("horizontal", spacing, parent)
        self._setup_button_alignment(alignment)
        
    def _setup_button_alignment(self, alignment):
        """Setup button alignment"""
        if alignment == "right":
            self.layout.addStretch()
            self.setAlignment(Qt.AlignmentFlag.AlignRight)
        elif alignment == "center":
            self.layout.addStretch()
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif alignment == "left":
            self.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.layout.addStretch()


class ContentContainer(ModernContainer):
    """
    Main content container with page-level spacing
    """
    
    def __init__(self, layout_type="vertical", spacing=Spacing.LG, parent=None):
        super().__init__(layout_type, spacing, parent)
        self.set_margins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)


class SpacerWidget(QWidget):
    """
    Widget that provides flexible spacing
    """
    
    def __init__(self, width=0, height=0, policy="expanding"):
        super().__init__()
        
        if policy == "expanding":
            size_policy = QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        elif policy == "fixed":
            size_policy = QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        elif policy == "preferred":
            size_policy = QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        else:
            size_policy = QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            
        self.setSizePolicy(QSizePolicy(*size_policy))
        
        if width > 0 or height > 0:
            self.setFixedSize(width, height)


class LayoutHelper:
    """
    Helper class for common layout patterns
    """
    
    @staticmethod
    def create_form_row(label_widget, input_widget, spacing=Spacing.SM):
        """Create a form row with label and input"""
        container = ModernContainer("horizontal", spacing)
        container.layout.addWidget(label_widget)
        container.layout.addWidget(input_widget)
        container.layout.addStretch()
        return container
    
    @staticmethod
    def create_button_row(buttons, alignment="right", spacing=Spacing.SM):
        """Create a row of buttons"""
        container = ButtonContainer(alignment, spacing)
        for button in buttons:
            container.layout.addWidget(button)
        return container
    
    @staticmethod
    def create_section(title_widget, content_widget, spacing=Spacing.MD):
        """Create a section with title and content"""
        container = SectionContainer("vertical", spacing)
        container.layout.addWidget(title_widget)
        container.layout.addWidget(content_widget)
        return container
    
    @staticmethod
    def create_card(content_widgets, layout_type="vertical", spacing=Spacing.MD):
        """Create a card with content widgets"""
        container = CardContainer(layout_type, spacing)
        for widget in content_widgets:
            if layout_type == "vertical":
                container.layout.addWidget(widget)
            elif layout_type == "horizontal":
                container.layout.addWidget(widget)
        return container