import logging
import os
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QMessageBox, QWidget, QFrame, QCheckBox, QTextEdit,
    QSplitter, QGroupBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ui.enhanced_widgets import EnhancedProgressBar
from ui.interactions import HoverButton, ModernFrame
from ui.theme import theme
from core.game_manager import GameManager
from ui.custom_checkbox import CustomCheckBox

logger = logging.getLogger(__name__)

class GameDeletionWorker(QThread):
    """Worker thread para deletar jogos sem bloquear a UI."""
    progress = pyqtSignal(int, str)  # progress, message
    game_deleted = pyqtSignal(str, bool, str)  # game_name, success, message
    finished = pyqtSignal()
    
    def __init__(self, games_to_delete: List[Dict], delete_compatdata: bool = False):
        super().__init__()
        self.games_to_delete = games_to_delete
        self.delete_compatdata = delete_compatdata
        self._is_running = True
    
    def run(self):
        """Executa a deleção dos jogos em background."""
        total_games = len(self.games_to_delete)
        
        for i, game_info in enumerate(self.games_to_delete):
            if not self._is_running:
                break
                
            game_name = game_info['name']
            self.progress.emit(
                int((i / total_games) * 100), 
                f"Deleting {game_name}..."
            )
            
            # Deletar jogo
            success, message = GameManager.delete_game(game_info, self.delete_compatdata)
            self.game_deleted.emit(game_name, success, message)
        
        self.progress.emit(100, "Deletion process completed!")
        self.finished.emit()
    
    def stop(self):
        """Para a execução do worker."""
        self._is_running = False

class GameDeletionDialog(QDialog):
    """Dialog principal para deleção de jogos ACCELA."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.games_list = []
        self.selected_games = []
        self.deletion_worker = None
        
        self.setWindowTitle("Uninstall ACCELA Games")
        self.setModal(True)
        self.setMinimumSize(800, 500)
        self.resize(850, 600)
        
        # Aplicar tema
        self.setStyleSheet(theme.get_dialog_stylesheet())
        
        self._setup_ui()
        self._load_games()
    
    def _setup_ui(self):
        """Configura a interface do dialog."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)  # Reduzir margins principais
        layout.setSpacing(6)  # Reduzir spacing principal
        
        # Header
        header_frame = self._create_header()
        layout.addWidget(header_frame)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Games table (left)
        table_frame = self._create_games_table()
        splitter.addWidget(table_frame)
        
        # Details panel (right)
        details_frame = self._create_details_panel()
        splitter.addWidget(details_frame)
        
        splitter.setSizes([500, 300])
        
        # Action buttons
        buttons_frame = self._create_action_buttons()
        layout.addWidget(buttons_frame)
        
        # Progress bar (initially hidden)
        self.progress_frame = self._create_progress_frame()
        self.progress_frame.setVisible(False)
        layout.addWidget(self.progress_frame)
    
    def _create_header(self) -> QFrame:
        """Cria o header do dialog."""
        frame = ModernFrame()
        frame.setMaximumHeight(50)  # Limitar altura do header
        # Remover borda do header
        frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.95);
                border: none;
                backdrop-filter: blur(10px);
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)  # Reduzir margins
        layout.setSpacing(2)  # Reduzir spacing
        
        title = QLabel("ACCELA Game Manager")
        title.setFont(QFont("TrixieCyrG-Plain Regular", 12, QFont.Weight.Bold))  # Reduzir fonte
        title.setStyleSheet(f"color: {theme.colors.PRIMARY}; margin: 0; border: none; background: transparent;")
        layout.addWidget(title)
        
        subtitle = QLabel("Select and delete games downloaded by ACCELA")
        subtitle.setStyleSheet(f"color: {theme.colors.TEXT_SECONDARY}; font-size: 10px; margin: 0; border: none; background: transparent;")
        layout.addWidget(subtitle)
        
        return frame
    
    def _create_games_table(self) -> QFrame:
        """Cria a tabela de jogos."""
        frame = ModernFrame()
        # Remover borda desnecessária
        frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.95);
                border: none;
                backdrop-filter: blur(10px);
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)  # Reduzir margins
        layout.setSpacing(3)  # Reduzir spacing
        
        # Table header
        header_label = QLabel("Installed Games")
        header_label.setFont(QFont("TrixieCyrG-Plain Regular", 10, QFont.Weight.Bold))  # Reduzir fonte
        header_label.setStyleSheet(f"color: {theme.colors.TEXT_PRIMARY}; margin: 0; margin-bottom: 3px; border: none; background: transparent;")
        layout.addWidget(header_label)
        
        # Games table
        self.games_table = QTableWidget()
        self.games_table.setColumnCount(5)
        self.games_table.setHorizontalHeaderLabels([
            "Select", "Game Name", "Size", "APPID", "Location"
        ])
        
        # Configurar tabela
        self.games_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.games_table.setAlternatingRowColors(True)
        self.games_table.verticalHeader().setVisible(False)
        self.games_table.setShowGrid(False)
        self.games_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.games_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.games_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.games_table.verticalHeader().setDefaultSectionSize(60)  # Altura das linhas para checkbox completo
        self.games_table.verticalHeader().setMinimumSectionSize(60)  # Forçar altura mínima
        self.games_table.setMinimumHeight(200)  # Altura mínima da tabela
        
        # Ajustar colunas
        header = self.games_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Select
        self.games_table.setColumnWidth(0, 60)  # Largura fixa para checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Game Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # APPID
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Location
        
        # Configurar altura das linhas para acomodar checkboxes
        self.games_table.verticalHeader().setDefaultSectionSize(36)  # Altura suficiente para checkboxes
        self.games_table.verticalHeader().setMinimumSectionSize(36)
        
        # Estilo da tabela
        self.games_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme.colors.BACKGROUND};
                color: {theme.colors.TEXT_PRIMARY};
                border: 1px solid {theme.colors.BORDER};
                gridline-color: {theme.colors.BORDER};
                selection-background-color: {theme.colors.PRIMARY};
                alternate-background-color: {theme.colors.SURFACE};
                font-size: 11px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 10px 4px;
                border-bottom: 1px solid {theme.colors.BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {theme.colors.PRIMARY};
                color: white;
            }}
            QTableWidget::item:hover {{
                background-color: {theme.colors.SURFACE_LIGHT};
            }}
            QTableWidget::item:selected:hover {{
                background-color: {theme.colors.PRIMARY_LIGHT};
            }}
            QHeaderView::section {{
                background-color: {theme.colors.SURFACE};
                color: {theme.colors.TEXT_PRIMARY};
                padding: 8px 6px;
                border: 1px solid {theme.colors.BORDER};
                font-weight: bold;
                font-size: 10px;
            }}
        """)
        
        layout.addWidget(self.games_table)
        
        # Select all/none buttons
        select_layout = QHBoxLayout()
        select_layout.setContentsMargins(0, 2, 0, 0)  # Reduzir margins
        select_layout.setSpacing(5)
        
        self.select_all_btn = HoverButton("Select All")
        self.select_all_btn.clicked.connect(self._select_all_games)
        self.select_all_btn.setMinimumHeight(28)  # Ensure minimum height for text
        self.select_all_btn.setMaximumHeight(32)  # Allow proper text display
        select_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = HoverButton("Select None")
        self.select_none_btn.clicked.connect(self._select_none_games)
        self.select_none_btn.setMinimumHeight(28)  # Ensure minimum height for text
        self.select_none_btn.setMaximumHeight(32)  # Allow proper text display
        select_layout.addWidget(self.select_none_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        return frame
    
    def _create_details_panel(self) -> QFrame:
        """Cria o painel de detalhes do jogo selecionado."""
        frame = ModernFrame()
        # Remover borda desnecessária
        frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.95);
                border: none;
                backdrop-filter: blur(10px);
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)  # Reduzir margins
        layout.setSpacing(3)  # Reduzir spacing
        
        # Details title
        details_title = QLabel("Game Details")
        details_title.setFont(QFont("TrixieCyrG-Plain Regular", 10, QFont.Weight.Bold))  # Reduzir fonte
        details_title.setStyleSheet(f"color: {theme.colors.TEXT_PRIMARY}; margin: 0; margin-bottom: 3px; border: none; background: transparent;")
        layout.addWidget(details_title)
        
        # Game info
        self.game_info_text = QTextEdit()
        self.game_info_text.setReadOnly(True)
        self.game_info_text.setMaximumHeight(120)  # Reduzir altura
        self.game_info_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme.colors.SURFACE};
                color: {theme.colors.TEXT_PRIMARY};
                border: none;
                padding: 8px;
                font-family: 'TrixieCyrG-Plain Regular';
                font-size: 10px;
            }}
        """)
        layout.addWidget(self.game_info_text)
        
        # Compatdata option
        compatdata_group = QGroupBox("💾 Save Data Options")
        compatdata_group.setStyleSheet(f"""
            QGroupBox {{
                color: {theme.colors.PRIMARY};
                border: 1px solid {theme.colors.PRIMARY};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: {theme.colors.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        compatdata_layout = QVBoxLayout(compatdata_group)
        
        self.delete_compatdata_checkbox = CustomCheckBox("Delete save data (compatdata folder)")
        self.delete_compatdata_checkbox.setChecked(False)  # Default: preserve saves
        self.delete_compatdata_checkbox.setStyleSheet(f"""
    CustomCheckBox {{
        color: {theme.colors.TEXT_PRIMARY};
        font-size: 10px;
        background-color: transparent;
        border: none;
        padding: 5px;
    }}
""")
        self.delete_compatdata_checkbox.setToolTip(
            "Check this box to delete the game's save data and configuration files.\n"
            "The compatdata folder contains:\n"
            "• Game saves and progress\n"
            "• Configuration files\n"
            "• Steam compatibility data\n"
            "\nIf unchecked, this data will be preserved for future use."
        )
        compatdata_layout.addWidget(self.delete_compatdata_checkbox)
        
        # Compatdata info label
        compatdata_info = QLabel("💡 Uncheck to preserve save games in compatdata/APPID/")
        compatdata_info.setStyleSheet(f"color: {theme.colors.TEXT_SECONDARY}; font-style: italic; font-size: 9px; padding: 2px;")
        compatdata_layout.addWidget(compatdata_info)
        
        layout.addWidget(compatdata_group)
        
        # Warning box
        warning_group = QGroupBox("⚠️ Deletion Warning")
        warning_group.setStyleSheet(f"""
            QGroupBox {{
                color: {theme.colors.PRIMARY};
                border: 1px solid {theme.colors.PRIMARY};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: {theme.colors.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        warning_layout = QVBoxLayout(warning_group)
        
        warning_text = QLabel(
            "• This will permanently delete the game and all its files\n"
            "• Save games handling depends on your choice above\n"
            "• This action cannot be undone\n"
            "• Only ACCELA-downloaded games will be shown"
        )
        warning_text.setStyleSheet(f"color: {theme.colors.TEXT_PRIMARY}; padding: 3px; font-size: 10px;")
        warning_layout.addWidget(warning_text)
        
        layout.addWidget(warning_group)
        layout.addStretch()
        
        return frame
    
    def _create_action_buttons(self) -> QFrame:
        """Cria os botões de ação."""
        frame = QFrame()
        frame.setStyleSheet("background-color: transparent;")
        frame.setMaximumHeight(40)  # Limitar altura do footer
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 2, 15, 2)  # Adicionar margem lateral de 15px
        layout.setSpacing(10)
        
        # Refresh button
        self.refresh_btn = HoverButton("Refresh List")
        self.refresh_btn.clicked.connect(self._load_games)
        self.refresh_btn.setMaximumHeight(28)  # Reduzir altura dos botões
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.colors.SURFACE};
                color: {theme.colors.TEXT_PRIMARY};
                padding: 4px 15px;  # Adicionar padding lateral
                border: 1px solid {theme.colors.BORDER};
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {theme.colors.SURFACE_LIGHT};
                border-color: {theme.colors.PRIMARY};
            }}
        """)
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
        
        # Delete button
        self.delete_btn = HoverButton("Delete Selected Games")
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.colors.PRIMARY};
                color: white;
                padding: 4px 15px;  # Adicionar padding lateral
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;  # Reduzir fonte
            }}
            QPushButton:hover {{
                background-color: {theme.colors.PRIMARY_LIGHT};
            }}
            QPushButton:disabled {{
                background-color: {theme.colors.SURFACE};
                color: {theme.colors.TEXT_DISABLED};
            }}
        """)
        self.delete_btn.clicked.connect(self._start_deletion)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setMaximumHeight(28)  # Reduzir altura
        layout.addWidget(self.delete_btn)
        
        # Close button
        self.close_btn = HoverButton("Close")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setMaximumHeight(28)  # Reduzir altura
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.colors.SURFACE};
                color: {theme.colors.TEXT_PRIMARY};
                padding: 4px 15px;  # Adicionar padding lateral
                border: 1px solid {theme.colors.BORDER};
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {theme.colors.SURFACE_LIGHT};
                border-color: {theme.colors.PRIMARY};
            }}
        """)
        layout.addWidget(self.close_btn)
        
        return frame
    
    def _create_progress_frame(self) -> QFrame:
        """Cria o frame de progresso da deleção."""
        frame = ModernFrame()
        frame.setMaximumHeight(60)  # Limitar altura do progress frame
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)  # Reduzir margins
        layout.setSpacing(3)  # Reduzir spacing
        
        # Progress label
        self.progress_label = QLabel("Preparing deletion...")
        self.progress_label.setStyleSheet(f"color: {theme.colors.TEXT_PRIMARY}; font-size: 10px;")
        layout.addWidget(self.progress_label)
        
        # Progress bar
        self.progress_bar = EnhancedProgressBar()
        self.progress_bar.setMaximumHeight(15)  # Reduzir altura
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        self.cancel_btn = HoverButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_deletion)
        self.cancel_btn.setMaximumHeight(20)  # Reduzir altura
        layout.addWidget(self.cancel_btn)
        
        return frame
    
    def _load_games(self):
        """Carrega a lista de jogos ACCELA."""
        self.games_list = GameManager.scan_accela_games()
        self._populate_games_table()
        self._update_details_panel()
        
        logger.info(f"Loaded {len(self.games_list)} ACCELA games")
    
    def _populate_games_table(self):
        """Popula a tabela com os jogos encontrados."""
        self.games_table.setRowCount(len(self.games_list))
        
        for row, game in enumerate(self.games_list):
            # Custom checkbox with guaranteed visible checkmark
            checkbox = CustomCheckBox()
            checkbox.stateChanged.connect(self._on_selection_changed)
            
            # Criar container para centralizar o checkbox
            checkbox_container = QWidget()
            checkbox_container.setMinimumHeight(25)  # Forçar altura mínima
            container_layout = QHBoxLayout(checkbox_container)
            container_layout.setContentsMargins(0, 2, 0, 0)  # Mover um pouco para cima
            container_layout.addWidget(checkbox)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.games_table.setCellWidget(row, 0, checkbox_container)
            
            # Game name (use display_name)
            name_item = QTableWidgetItem(game['display_name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setToolTip(game['name'])  # Show original name in tooltip
            self.games_table.setItem(row, 1, name_item)
            
            # Size
            size_item = QTableWidgetItem(game['size_formatted'])
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.games_table.setItem(row, 2, size_item)
            
            # APPID
            appid_item = QTableWidgetItem(game['appid'])
            appid_item.setFlags(appid_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.games_table.setItem(row, 3, appid_item)
            
            # Location
            location_item = QTableWidgetItem(os.path.basename(game['library_path']))
            location_item.setFlags(location_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.games_table.setItem(row, 4, location_item)
        
        # Conectar seleção de linha
        self.games_table.cellClicked.connect(self._on_cell_clicked)
        self.games_table.itemSelectionChanged.connect(self._on_table_selection_changed)
    
    def _on_cell_clicked(self, row: int, column: int):
        """Handle cell clicks - toggle checkbox and update details."""
        if 0 <= row < len(self.games_list):
            # Toggle checkbox if not clicking on checkbox column
            if column != 0:
                checkbox_container = self.games_table.cellWidget(row, 0)
                if checkbox_container:
                    checkbox = checkbox_container.findChild(CustomCheckBox)
                    if checkbox:
                        checkbox.setChecked(not checkbox.isChecked())
            
            # Update details panel
            self._update_details_panel(self.games_list[row])
    
    def _on_table_selection_changed(self):
        """Handle table selection changes."""
        current_row = self.games_table.currentRow()
        if 0 <= current_row < len(self.games_list):
            self._update_details_panel(self.games_list[current_row])
    
    def _update_details_panel(self, game: Optional[Dict] = None):
        """Atualiza o painel de detalhes com informações do jogo."""
        if not game:
            self.game_info_text.setText("Select a game to view details...")
            return
        
        # Check for compatdata existence
        compatdata_path = os.path.join(game['library_path'], 'steamapps', 'compatdata', game['appid'])
        compatdata_exists = os.path.exists(compatdata_path)
        compatdata_size = GameManager._calculate_directory_size(compatdata_path) if compatdata_exists else 0
        
        details = f"""<b>Display Name:</b> {game['display_name']}<br>
<b>Original Name:</b> {game['name']}<br>
<b>APPID:</b> {game['appid']}<br>
<b>Install Directory:</b> {game['installdir']}<br>
<b>Size:</b> {game['size_formatted']}<br>
<b>Library:</b> {os.path.basename(game['library_path'])}<br><br>

<b>Files to be deleted:</b><br>
• {os.path.basename(game['acf_path'])}<br>
• {game['installdir']}/ (entire folder)<br><br>

<b>Save Data (compatdata):</b><br>
• Status: {'🟢 Found' if compatdata_exists else '🔴 Not found'}<br>
• Size: {GameManager._format_size(compatdata_size) if compatdata_exists else 'N/A'}<br>
• Path: compatdata/{game['appid']}/<br>
• Action: {'Will be deleted if checked' if compatdata_exists else 'N/A'}
"""
        
        self.game_info_text.setText(details)
    
    def _on_selection_changed(self):
        """Atualiza o estado dos botões quando a seleção muda."""
        selected_games = []
        
        for row in range(self.games_table.rowCount()):
            checkbox_container = self.games_table.cellWidget(row, 0)
            if checkbox_container:
                # Encontrar o checkbox dentro do container
                checkbox = checkbox_container.findChild(CustomCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_games.append(self.games_list[row])
        
        self.selected_games = selected_games
        self.delete_btn.setEnabled(len(selected_games) > 0)
        self.delete_btn.setText(f"Delete Selected Games ({len(selected_games)})")
    
    def _select_all_games(self):
        """Seleciona todos os jogos."""
        for row in range(self.games_table.rowCount()):
            checkbox_container = self.games_table.cellWidget(row, 0)
            if checkbox_container:
                checkbox = checkbox_container.findChild(CustomCheckBox)
                if checkbox:
                    checkbox.setChecked(True)
    
    def _select_none_games(self):
        """Deseleciona todos os jogos."""
        for row in range(self.games_table.rowCount()):
            checkbox_container = self.games_table.cellWidget(row, 0)
            if checkbox_container:
                checkbox = checkbox_container.findChild(CustomCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
    
    def _start_deletion(self):
        """Inicia o processo de deleção."""
        if not self.selected_games:
            return
        
        # Confirmar deleção
        game_names = [game['name'] for game in self.selected_games]
        total_size = sum(game['size_bytes'] for game in self.selected_games)
        delete_compatdata = self.delete_compatdata_checkbox.isChecked()
        
        # Calcular tamanho do compatdata se aplicável
        compatdata_size = 0
        compatdata_games = []
        if delete_compatdata:
            for game in self.selected_games:
                compatdata_path = os.path.join(game['library_path'], 'steamapps', 'compatdata', game['appid'])
                if os.path.exists(compatdata_path):
                    compatdata_size += GameManager._calculate_directory_size(compatdata_path)
                    compatdata_games.append(game['name'])
        
        confirm_msg = QMessageBox(self)
        confirm_msg.setWindowTitle("Confirm Deletion")
        confirm_msg.setIcon(QMessageBox.Icon.Warning)
        
        # Mensagem principal baseada na opção de compatdata
        if delete_compatdata:
            main_text = f"Are you sure you want to delete {len(self.selected_games)} game(s) INCLUDING SAVE DATA?"
            main_text += f"\n\n⚠️ WARNING: This will permanently delete all save games and progress!"
        else:
            main_text = f"Are you sure you want to delete {len(self.selected_games)} game(s)?"
            main_text += f"\n\n💾 Save games will be preserved."
        
        confirm_msg.setText(main_text)
        
        # Texto detalhado
        detailed_text = f"Games to delete:\n" + "\n".join(f"• {name}" for name in game_names)
        detailed_text += f"\n\nTotal game size: {GameManager._format_size(total_size)}"
        
        if delete_compatdata and compatdata_games:
            detailed_text += f"\nSave data to be deleted:\n" + "\n".join(f"• {name}" for name in compatdata_games)
            detailed_text += f"\nSave data size: {GameManager._format_size(compatdata_size)}"
            detailed_text += f"\n\nTotal space to be freed: {GameManager._format_size(total_size + compatdata_size)}"
        else:
            detailed_text += f"\n\nTotal space to be freed: {GameManager._format_size(total_size)}"
        
        detailed_text += "\n\nThis action cannot be undone!"
        
        confirm_msg.setDetailedText(detailed_text)
        confirm_msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirm_msg.setDefaultButton(QMessageBox.StandardButton.No)
        
        if confirm_msg.exec() != QMessageBox.StandardButton.Yes:
            return
        
        # Iniciar deleção
        self._start_deletion_worker()
    
    def _start_deletion_worker(self):
        """Inicia o worker de deleção em background."""
        # Esconder elementos da UI normal
        self.games_table.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.progress_frame.setVisible(True)
        
        # Obter opção de compatdata
        delete_compatdata = self.delete_compatdata_checkbox.isChecked()
        
        # Criar e iniciar worker
        self.deletion_worker = GameDeletionWorker(self.selected_games, delete_compatdata)
        self.deletion_worker.progress.connect(self._on_deletion_progress)
        self.deletion_worker.game_deleted.connect(self._on_game_deleted)
        self.deletion_worker.finished.connect(self._on_deletion_finished)
        self.deletion_worker.start()
    
    def _on_deletion_progress(self, progress: int, message: str):
        """Atualiza o progresso da deleção."""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
    
    def _on_game_deleted(self, game_name: str, success: bool, message: str):
        """Trata o resultado da deleção de um jogo."""
        if success:
            logger.info(f"Successfully deleted: {game_name}")
        else:
            logger.error(f"Failed to delete {game_name}: {message}")
    
    def _on_deletion_finished(self):
        """Trata o fim do processo de deleção."""
        self.deletion_worker = None
        
        # Mostrar resultado
        QMessageBox.information(
            self, 
            "Deletion Complete", 
            "Game deletion process has completed. Check the logs for details."
        )
        
        # Recarregar lista e resetar UI
        self._load_games()
        self.games_table.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.progress_frame.setVisible(False)
        self.progress_bar.setValue(0)
    
    def _cancel_deletion(self):
        """Cancela o processo de deleção."""
        if self.deletion_worker:
            self.deletion_worker.stop()
            self.deletion_worker.wait()
            self.deletion_worker = None
        
        # Resetar UI
        self.games_table.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.progress_frame.setVisible(False)
        self.progress_bar.setValue(0)
    
    def closeEvent(self, event):
        """Trata o evento de fechar o dialog."""
        if self.deletion_worker:
            self._cancel_deletion()
        event.accept()
