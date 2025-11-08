import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

logger = logging.getLogger(__name__)

class CheckBoxWidget(QWidget):
    """Internal widget for drawing the checkbox"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self.setFixedSize(18, 18)  # Tamanho reduzido
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def isChecked(self):
        return self._checked
    
    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw border
        pen = QPen(QColor('#C06C84'), 2)
        painter.setPen(pen)
        
        # Draw background
        if self._checked:
            brush = QBrush(QColor('#C06C84'))
            painter.setBrush(brush)
        else:
            brush = QBrush(QColor('#1E1E1E'))
            painter.setBrush(brush)
        
        # Draw rounded rectangle (ajustado para 18x18)
        painter.drawRoundedRect(2, 2, 14, 14, 3, 3)
        
        # Draw checkmark if checked (ajustado para 18x18)
        if self._checked:
            painter.setPen(QPen(QColor('white'), 2))
            painter.drawLine(5, 9, 7, 11)
            painter.drawLine(7, 11, 12, 6)
        
        painter.end()

class CustomCheckBox(QWidget):
    """Custom checkbox with guaranteed visible checkmark"""
    
    stateChanged = pyqtSignal(int)
    
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        
        # Setup layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Checkbox
        self.checkbox_widget = CheckBoxWidget()
        layout.addWidget(self.checkbox_widget)
        
        # Label
        if text:
            self.label = QLabel(text)
            self.label.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(self.label)
        else:
            self.label = None
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Garantir tamanho mínimo para evitar corte
        if text:
            # Se tem texto, não limitar tamanho
            self.setMinimumHeight(20)
        else:
            # Se não tem texto, tamanho fixo para tabela
            self.setMinimumSize(20, 20)
            self.setMaximumSize(20, 20)
    
    def isChecked(self):
        return self.checkbox_widget.isChecked()
    
    def setChecked(self, checked):
        old_checked = self.checkbox_widget.isChecked()
        self.checkbox_widget.setChecked(checked)
        if old_checked != checked:
            self.stateChanged.emit(1 if checked else 0)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self.isChecked())
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def setText(self, text):
        """Update checkbox text"""
        if self.label:
            self.label.setText(text)
        else:
            # Create label if it doesn't exist
            self.label = QLabel(text)
            self.label.setCursor(Qt.CursorShape.PointingHandCursor)
            layout = self.layout()
            layout.insertWidget(1, self.label)
        self._text = text
    
    def text(self):
        """Get checkbox text"""
        return self._text