import logging
import os
import sys
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QProgressBar, QTextEdit,
    QFrame, QMessageBox, QSplitter, QWidget, QGroupBox,
    QScrollArea, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.interactions import ModernFrame, HoverButton, AnimatedLabel
from ui.theme import theme, BorderRadius, Spacing, Typography

# Import BackupManager after path setup  
import importlib.util
backup_manager_path = os.path.join(project_root, "core", "backup_manager.py")
spec = importlib.util.spec_from_file_location("backup_manager", backup_manager_path)
if spec and spec.loader:
    backup_manager_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backup_manager_module)
    BackupManager = backup_manager_module.BackupManager
else:
    raise ImportError("Could not load BackupManager")

logger = logging.getLogger(__name__)


class BackupWorker(QThread):
    """Worker thread for backup operations to avoid UI freezing."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, operation: str, backup_manager, **kwargs):
        super().__init__()
        self.operation = operation
        self.backup_manager = backup_manager
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "create":
                self.progress.emit("Creating backup...")
                backup_path = self.backup_manager.create_backup(self.kwargs.get('backup_name'))
                if backup_path:
                    self.finished.emit(True, f"Backup created: {os.path.basename(backup_path)}")
                else:
                    self.finished.emit(False, "Failed to create backup")
                    
            elif self.operation == "restore":
                self.progress.emit("Restoring backup...")
                success = self.backup_manager.restore_backup(self.kwargs['backup_path'])
                if success:
                    self.finished.emit(True, "Backup restored successfully")
                else:
                    self.finished.emit(False, "Failed to restore backup")
                    
            elif self.operation == "delete":
                self.progress.emit("Deleting backup...")
                success = self.backup_manager.delete_backup(self.kwargs['backup_path'])
                if success:
                    self.finished.emit(True, "Backup deleted successfully")
                else:
                    self.finished.emit(False, "Failed to delete backup")
                    
        except Exception as e:
            logger.error(f"Backup worker error: {e}")
            self.finished.emit(False, f"Error: {str(e)}")


class BackupDialog(QDialog):
    """
    Dialog for managing Steam stats backups.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        if BackupManager is None:
            raise ImportError("BackupManager not available")
        self.backup_manager = BackupManager()
        self.worker = None
        self.setup_ui()
        self.refresh_backup_list()
        
    def setup_ui(self):
        self.setWindowTitle("Backup/Restore Stats")
        self.setFixedSize(800, 600)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        main_layout.setSpacing(Spacing.MD)
        
        # Title
        title_label = QLabel("Steam Stats Backup Manager")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.colors.TEXT_ACCENT};
                {Typography.get_font_style(Typography.H2_SIZE)};
                font-weight: bold;
                padding: {Spacing.SM}px 0;
            }}
        """)
        main_layout.addWidget(title_label)
        
        # Status section
        self.setup_status_section(main_layout)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Backup list
        left_panel = QWidget()
        self.setup_backup_list_panel(left_panel.layout() if left_panel.layout() else QVBoxLayout(left_panel))
        splitter.addWidget(left_panel)
        
        # Right panel - Actions and info
        right_panel = self.setup_actions_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        
        # Progress section
        self.setup_progress_section(main_layout)
        
        # Buttons
        self.setup_buttons(main_layout)
        
        self.setLayout(main_layout)
        
        # Apply theme
        self.setStyleSheet(f"""
            QDialog {{
                background: {theme.colors.BACKGROUND};
                border: 2px solid {theme.colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.MEDIUM)};
            }}
        """)
    
    def setup_status_section(self, parent_layout):
        """Setup status information section."""
        status_frame = ModernFrame()
        status_layout = QVBoxLayout(status_frame)
        
        # Steam stats path
        stats_path = self.backup_manager.get_steam_stats_path()
        if stats_path:
            path_label = QLabel(f"Stats Path: {stats_path}")
            path_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme.colors.TEXT_SECONDARY};
                    {Typography.get_font_style(Typography.BODY_SIZE)};
                    padding: {Spacing.XS}px;
                }}
            """)
            status_layout.addWidget(path_label)
            
            # Count files
            files_count = len(self.backup_manager.list_stats_files())
            count_label = QLabel(f"Stats Files: {files_count}")
            count_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme.colors.TEXT_SECONDARY};
                    {Typography.get_font_style(Typography.BODY_SIZE)};
                    padding: {Spacing.XS}px;
                }}
            """)
            status_layout.addWidget(count_label)
        else:
            error_label = QLabel("❌ Steam installation not found or stats directory missing")
            error_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme.colors.ERROR};
                    {Typography.get_font_style(Typography.BODY_SIZE)};
                    font-weight: bold;
                    padding: {Spacing.XS}px;
                }}
            """)
            status_layout.addWidget(error_label)
        
        parent_layout.addWidget(status_frame)
    
    def setup_backup_list_panel(self, parent_layout=None):
        """Setup backup list panel."""
        if parent_layout is None:
            panel = QFrame()
            layout = QVBoxLayout(panel)
        else:
            layout = parent_layout
            panel = None
        
        # Title
        list_title = QLabel("Available Backups")
        list_title.setStyleSheet(f"""
            QLabel {{
                color: {theme.colors.TEXT_PRIMARY};
                {Typography.get_font_style(Typography.H3_SIZE)};
                font-weight: bold;
                padding: {Spacing.SM}px 0;
            }}
        """)
        layout.addWidget(list_title)
        
        # Backup list
        self.backup_list = QListWidget()
        self.backup_list.setStyleSheet(f"""
            QListWidget {{
                background: {theme.colors.SURFACE};
                border: 1px solid {theme.colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.SMALL)};
                {Typography.get_font_style(Typography.BODY_SIZE)};
                padding: {Spacing.XS}px;
            }}
            QListWidget::item {{
                padding: {Spacing.SM}px;
                border-bottom: 1px solid {theme.colors.BORDER};
                color: {theme.colors.TEXT_PRIMARY};
            }}
            QListWidget::item:selected {{
                background: {theme.colors.PRIMARY};
                color: {theme.colors.TEXT_ON_PRIMARY};
            }}
            QListWidget::item:hover {{
                background: {theme.colors.SURFACE_LIGHT};
            }}
        """)
        self.backup_list.itemSelectionChanged.connect(self.on_backup_selected)
        layout.addWidget(self.backup_list)
        
        # Refresh button
        refresh_btn = HoverButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_backup_list)
        layout.addWidget(refresh_btn)
        
        return panel if panel else layout.parent()
    
    def setup_actions_panel(self):
        """Setup actions panel."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Title
        actions_title = QLabel("Actions")
        actions_title.setStyleSheet(f"""
            QLabel {{
                color: {theme.colors.TEXT_PRIMARY};
                {Typography.get_font_style(Typography.H3_SIZE)};
                font-weight: bold;
                padding: {Spacing.SM}px 0;
            }}
        """)
        layout.addWidget(actions_title)
        
        # Create backup section
        create_group = QGroupBox("Create Backup")
        create_group.setStyleSheet(f"""
            QGroupBox {{
                color: {theme.colors.TEXT_PRIMARY};
                {Typography.get_font_style(Typography.BODY_SIZE)};
                font-weight: bold;
                border: 1px solid {theme.colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.SMALL)};
                margin-top: {Spacing.SM}px;
                padding-top: {Spacing.SM}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Spacing.SM}px;
                padding: 0 {Spacing.XS}px 0 {Spacing.XS}px;
            }}
        """)
        create_layout = QVBoxLayout(create_group)
        
        self.create_backup_btn = HoverButton("Create New Backup")
        self.create_backup_btn.clicked.connect(self.create_backup)
        create_layout.addWidget(self.create_backup_btn)
        
        layout.addWidget(create_group)
        
        # Restore backup section
        restore_group = QGroupBox("Restore Backup")
        restore_group.setStyleSheet(f"""
            QGroupBox {{
                color: {theme.colors.TEXT_PRIMARY};
                {Typography.get_font_style(Typography.BODY_SIZE)};
                font-weight: bold;
                border: 1px solid {theme.colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.SMALL)};
                margin-top: {Spacing.SM}px;
                padding-top: {Spacing.SM}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Spacing.SM}px;
                padding: 0 {Spacing.XS}px 0 {Spacing.XS}px;
            }}
        """)
        restore_layout = QVBoxLayout(restore_group)
        
        self.restore_backup_btn = HoverButton("Restore Selected Backup")
        self.restore_backup_btn.clicked.connect(self.restore_backup)
        self.restore_backup_btn.setEnabled(False)
        restore_layout.addWidget(self.restore_backup_btn)
        
        layout.addWidget(restore_group)
        
        # Delete backup section
        delete_group = QGroupBox("Delete Backup")
        delete_group.setStyleSheet(f"""
            QGroupBox {{
                color: {theme.colors.TEXT_PRIMARY};
                {Typography.get_font_style(Typography.BODY_SIZE)};
                font-weight: bold;
                border: 1px solid {theme.colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.SMALL)};
                margin-top: {Spacing.SM}px;
                padding-top: {Spacing.SM}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Spacing.SM}px;
                padding: 0 {Spacing.XS}px 0 {Spacing.XS}px;
            }}
        """)
        delete_layout = QVBoxLayout(delete_group)
        
        self.delete_backup_btn = HoverButton("Delete Selected Backup")
        self.delete_backup_btn.clicked.connect(self.delete_backup)
        self.delete_backup_btn.setEnabled(False)
        delete_layout.addWidget(self.delete_backup_btn)
        
        layout.addWidget(delete_group)
        
        # Backup info section
        info_group = QGroupBox("Backup Information")
        info_group.setStyleSheet(f"""
            QGroupBox {{
                color: {theme.colors.TEXT_PRIMARY};
                {Typography.get_font_style(Typography.BODY_SIZE)};
                font-weight: bold;
                border: 1px solid {theme.colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.SMALL)};
                margin-top: {Spacing.SM}px;
                padding-top: {Spacing.SM}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Spacing.SM}px;
                padding: 0 {Spacing.XS}px 0 {Spacing.XS}px;
            }}
        """)
        info_layout = QVBoxLayout(info_group)
        
        self.backup_info_text = QTextEdit()
        self.backup_info_text.setReadOnly(True)
        self.backup_info_text.setMaximumHeight(150)
        self.backup_info_text.setStyleSheet(f"""
            QTextEdit {{
                background: {theme.colors.SURFACE};
                border: 1px solid {theme.colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.SMALL)};
                {Typography.get_font_style(Typography.CAPTION_SIZE)};
                color: {theme.colors.TEXT_SECONDARY};
                padding: {Spacing.XS}px;
            }}
        """)
        self.backup_info_text.setText("Select a backup to view details")
        info_layout.addWidget(self.backup_info_text)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        return panel
    
    def setup_progress_section(self, parent_layout):
        """Setup progress section."""
        progress_frame = ModernFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {theme.colors.BORDER};
                {BorderRadius.get_border_radius(BorderRadius.SMALL)};
                text-align: center;
                {Typography.get_font_style(Typography.CAPTION_SIZE)};
                color: {theme.colors.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background: {theme.colors.PRIMARY};
                {BorderRadius.get_border_radius(BorderRadius.SMALL)};
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.colors.TEXT_SECONDARY};
                {Typography.get_font_style(Typography.CAPTION_SIZE)};
                padding: {Spacing.XS}px;
            }}
        """)
        progress_layout.addWidget(self.status_label)
        
        parent_layout.addWidget(progress_frame)
    
    def setup_buttons(self, parent_layout):
        """Setup dialog buttons."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = HoverButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        parent_layout.addLayout(button_layout)
    
    def refresh_backup_list(self):
        """Refresh the backup list."""
        try:
            self.backup_list.clear()
            backups = self.backup_manager.list_backups()
            
            if not backups:
                item = QListWidgetItem("No backups found")
                item.setData(Qt.ItemDataRole.UserRole, None)
                self.backup_list.addItem(item)
                return
            
            for backup in backups:
                display_name = backup['name']
                if backup['created_date']:
                    display_name += f" ({backup['created_date'].strftime('%Y-%m-%d %H:%M')})"
                display_name += f" - {backup['formatted_size']}"
                
                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, backup)
                self.backup_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Error refreshing backup list: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh backup list: {e}")
    
    def on_backup_selected(self):
        """Handle backup selection."""
        selected_items = self.backup_list.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.restore_backup_btn.setEnabled(has_selection)
        self.delete_backup_btn.setEnabled(has_selection)
        
        if has_selection:
            backup = selected_items[0].data(Qt.ItemDataRole.UserRole)
            if backup:
                self.show_backup_info(backup)
            else:
                self.backup_info_text.setText("No backup selected")
        else:
            self.backup_info_text.setText("Select a backup to view details")
    
    def show_backup_info(self, backup: Dict[str, Any]):
        """Show backup information."""
        try:
            info = self.backup_manager.get_backup_info(backup['path'])
            if info:
                info_text = f"Name: {backup['name']}\n"
                info_text += f"Size: {backup['formatted_size']}\n"
                info_text += f"Files: {info['total_files']}\n"
                info_text += f"Total Size: {self.backup_manager._format_file_size(info['total_size'])}\n\n"
                info_text += "Files:\n"
                
                for file_info in info['files']:
                    info_text += f"  • {file_info['name']} ({file_info['type']})\n"
                
                self.backup_info_text.setText(info_text)
            else:
                self.backup_info_text.setText(f"Name: {backup['name']}\nSize: {backup['formatted_size']}\n\nUnable to read detailed information")
                
        except Exception as e:
            logger.error(f"Error showing backup info: {e}")
            self.backup_info_text.setText(f"Error loading backup info: {e}")
    
    def create_backup(self):
        """Create a new backup."""
        if self.worker and self.worker.isRunning():
            return
        
        # Check if Steam stats path exists
        if not self.backup_manager.get_steam_stats_path():
            QMessageBox.critical(self, "Error", "Steam stats directory not found. Please ensure Steam is installed and has been run at least once.")
            return
        
        # Check if there are files to backup
        files = self.backup_manager.list_stats_files()
        if not files:
            QMessageBox.warning(self, "Warning", "No stats files found to backup. This is normal if you haven't played any games yet.")
            return
        
        # Start backup worker
        self.worker = BackupWorker("create", self.backup_manager)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.finished.connect(self.on_worker_finished)
        
        self.set_ui_busy(True, "Creating backup...")
        self.worker.start()
    
    def restore_backup(self):
        """Restore selected backup."""
        if self.worker and self.worker.isRunning():
            return
        
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            return
        
        backup = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if not backup:
            return
        
        # Confirm restore
        reply = QMessageBox.question(
            self, 
            "Confirm Restore",
            f"Are you sure you want to restore backup '{backup['name']}'?\n\n"
            "This will replace your current stats files.\n"
            "A backup will be created automatically before restoring.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Start restore worker
        self.worker = BackupWorker("restore", self.backup_manager, backup_path=backup['path'])
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.finished.connect(self.on_worker_finished)
        
        self.set_ui_busy(True, "Restoring backup...")
        self.worker.start()
    
    def delete_backup(self):
        """Delete selected backup."""
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            return
        
        backup = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if not backup:
            return
        
        # Confirm delete
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete backup '{backup['name']}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Start delete worker
        self.worker = BackupWorker("delete", self.backup_manager, backup_path=backup['path'])
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.finished.connect(self.on_worker_finished)
        
        self.set_ui_busy(True, "Deleting backup...")
        self.worker.start()
    
    def on_worker_progress(self, message: str):
        """Handle worker progress updates."""
        self.status_label.setText(message)
        QApplication.processEvents()
    
    def on_worker_finished(self, success: bool, message: str):
        """Handle worker completion."""
        self.set_ui_busy(False)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.refresh_backup_list()
        else:
            QMessageBox.critical(self, "Error", message)
    
    def set_ui_busy(self, busy: bool, message: str = ""):
        """Set UI busy state."""
        self.progress_bar.setVisible(busy)
        self.status_label.setText(message)
        
        # Enable/disable buttons
        self.create_backup_btn.setEnabled(not busy)
        has_selection = bool(self.backup_list.selectedItems())
        self.restore_backup_btn.setEnabled(not busy and has_selection)
        self.delete_backup_btn.setEnabled(not busy and has_selection)
        
        if busy:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)