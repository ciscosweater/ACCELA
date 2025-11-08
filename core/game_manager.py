import logging
import os
import re
import shutil
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from . import steam_helpers

logger = logging.getLogger(__name__)

class GameManager:
    """
    Gerencia operações com jogos baixados pelo ACCELA.
    Responsável por escanear, parsear e deletar jogos com segurança.
    """
    
    @staticmethod
    def scan_accela_games() -> List[Dict]:
        """
        Escaneia todas as bibliotecas Steam em busca de jogos ACCELA.
        
        Returns:
            Lista de dicionários com informações dos jogos encontrados
        """
        games = []
        libraries = steam_helpers.get_steam_libraries()
        
        for library_path in libraries:
            steamapps_path = os.path.join(library_path, 'steamapps')
            if not os.path.isdir(steamapps_path):
                continue
                
            acf_files = GameManager._find_acf_files(steamapps_path)
            for acf_file in acf_files:
                game_info = GameManager._parse_acf_file(acf_file, library_path)
                if game_info and GameManager._is_accela_game(game_info, library_path):
                    games.append(game_info)
                    
        logger.info(f"Found {len(games)} ACCELA games across {len(libraries)} libraries")
        return games
    
    @staticmethod
    def _find_acf_files(steamapps_path: str) -> List[str]:
        """Encontra todos os arquivos appmanifest_*.acf no diretório steamapps."""
        acf_files = []
        try:
            for file in os.listdir(steamapps_path):
                if file.startswith('appmanifest_') and file.endswith('.acf'):
                    acf_files.append(os.path.join(steamapps_path, file))
        except Exception as e:
            logger.error(f"Error scanning directory {steamapps_path}: {e}")
        return acf_files
    
    @staticmethod
    def _parse_acf_file(acf_path: str, library_path: str) -> Optional[Dict]:
        """
        Parseia um arquivo .acf e extrai informações do jogo.
        
        Args:
            acf_path: Caminho do arquivo .acf
            library_path: Caminho da biblioteca Steam
            
        Returns:
            Dicionário com informações do jogo ou None se falhar
        """
        try:
            with open(acf_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrair informações usando regex
            appid_match = re.search(r'"appid"\s*"(\d+)"', content)
            name_match = re.search(r'"name"\s*"([^"]+)"', content)
            installdir_match = re.search(r'"installdir"\s*"([^"]+)"', content)
            
            if not all([appid_match, name_match, installdir_match]):
                logger.warning(f"Invalid ACF file format: {acf_path}")
                return None
            
            appid = appid_match.group(1)
            name = name_match.group(1)
            installdir = installdir_match.group(1)
            
            # Calcular tamanho da pasta do jogo
            game_path = os.path.join(library_path, 'steamapps', 'common', installdir)
            size_bytes = GameManager._calculate_directory_size(game_path) if os.path.exists(game_path) else 0
            
            # Use installdir as fallback for name when name looks like App_XXXXX
            display_name = name
            if name.startswith('App_'):  # Always use installdir for App_ pattern
                display_name = installdir
            
            return {
                'appid': appid,
                'name': name,  # Keep original name
                'display_name': display_name,  # Use this for UI
                'installdir': installdir,
                'acf_path': acf_path,
                'game_path': game_path,
                'library_path': library_path,
                'size_bytes': size_bytes,
                'size_formatted': GameManager._format_size(size_bytes)
            }
            
        except Exception as e:
            logger.error(f"Error parsing ACF file {acf_path}: {e}")
            return None
    
    @staticmethod
    def _is_accela_game(game_info: Dict, library_path: str) -> bool:
        """
        Verifica se o jogo foi baixado pelo ACCELA.
        
        Args:
            game_info: Informações do jogo parseadas do .acf
            library_path: Caminho da biblioteca Steam
            
        Returns:
            True se for jogo ACCELA, False caso contrário
        """
        # Verificar se existe pasta .DepotDownloader na pasta do jogo
        game_path = game_info['game_path']
        if os.path.exists(game_path):
            depotdownloader_path = os.path.join(game_path, '.DepotDownloader')
            if os.path.isdir(depotdownloader_path):
                return True
    
    @staticmethod
    def _validate_compatdata_deletion_safety(compatdata_path: str, appid: str) -> bool:
        """
        Validações de segurança específicas para deleção de compatdata.
        
        Args:
            compatdata_path: Caminho da pasta compatdata
            appid: APPID do jogo
            
        Returns:
            True se seguro para deletar, False caso contrário
        """
        # 1. Verificar se o path termina com o APPID correto
        expected_path_suffix = os.path.join('compatdata', appid)
        if not compatdata_path.endswith(expected_path_suffix):
            logger.error(f"SAFETY: Compatdata path mismatch. Expected to end with: {expected_path_suffix}, Got: {compatdata_path}")
            return False
        
        # 2. Verificar se contém estrutura típica de compatdata
        expected_files = ['pfx', 'version', 'config_info']
        found_expected_items = 0
        try:
            for item in os.listdir(compatdata_path):
                if item in expected_files:
                    found_expected_items += 1
        except Exception as e:
            logger.error(f"SAFETY: Cannot list compatdata directory {compatdata_path}: {e}")
            return False
        
        # Se não encontrar nenhum item esperado, pode não ser compatdata válido
        if found_expected_items == 0:
            logger.warning(f"SAFETY: Compatdata folder {compatdata_path} doesn't contain expected structure")
            # Não bloqueia deleção, mas avisa
        
        # 3. Verificar se não está tentando deletar pasta system
        dangerous_paths = ['windows', 'system32', 'program files', 'programdata', 'root', 'etc', 'var']
        # Verificar apenas o nome da pasta base, não o caminho completo
        folder_name = os.path.basename(compatdata_path).lower()
        for dangerous in dangerous_paths:
            if folder_name == dangerous:
                logger.error(f"SAFETY: Dangerous compatdata folder name detected: {folder_name}")
                return False
        
        # 4. Verificar se o APPID é numérico
        if not appid.isdigit():
            logger.error(f"SAFETY: Invalid APPID format: {appid}")
            return False
        
        return True
        
        # Verificar se o .acf foi criado pelo ACCELA (formato específico)
        try:
            with open(game_info['acf_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ACCELA cria .acf com formato específico (sem campos como buildid, LastUpdated, etc.)
            # Se tiver campos completos, provavelmente é jogo original Steam
            if 'buildid' in content and 'LastUpdated' in content:
                return False
                
            return True
        except:
            return False
    
    @staticmethod
    def _calculate_directory_size(path: str) -> int:
        """Calcula o tamanho total de um diretório em bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, IOError):
                        continue
        except Exception:
            pass
        return total_size
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Formata tamanho em bytes para formato legível."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def delete_game(game_info: Dict, delete_compatdata: bool = False) -> Tuple[bool, str]:
        """
        Deleta um jogo ACCELA com segurança máxima.
        
        Args:
            game_info: Informações do jogo a ser deletado
            delete_compatdata: Se True, também deleta a pasta compatdata (saves)
            
        Returns:
            Tuple (sucesso, mensagem)
        """
        appid = game_info['appid']
        name = game_info['name']
        installdir = game_info['installdir']
        acf_path = game_info['acf_path']
        game_path = game_info['game_path']
        library_path = game_info['library_path']
        
        logger.info(f"Starting deletion of game {name} (APPID: {appid}), delete_compatdata={delete_compatdata}")
        
        # Validações de segurança
        if not GameManager._validate_deletion_safety(game_info):
            error_msg = f"Safety validation failed for game {name}"
            logger.error(error_msg)
            return False, error_msg
        
        deleted_items = []
        errors = []
        
        # 1. Deletar arquivo .acf
        try:
            if os.path.exists(acf_path):
                os.remove(acf_path)
                deleted_items.append(f"ACF file: {acf_path}")
                logger.info(f"Deleted ACF file: {acf_path}")
        except Exception as e:
            error_msg = f"Failed to delete ACF file: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        # 2. Deletar pasta do jogo em steamapps/common
        try:
            if os.path.exists(game_path) and os.path.isdir(game_path):
                shutil.rmtree(game_path)
                deleted_items.append(f"Game folder: {game_path}")
                logger.info(f"Deleted game folder: {game_path}")
        except Exception as e:
            error_msg = f"Failed to delete game folder: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        # 3. Deletar compatdata (saves) se solicitado
        if delete_compatdata:
            compatdata_path = os.path.join(library_path, 'steamapps', 'compatdata', appid)
            try:
                if os.path.exists(compatdata_path) and os.path.isdir(compatdata_path):
                    # Validação adicional de segurança para compatdata
                    if GameManager._validate_compatdata_deletion_safety(compatdata_path, appid):
                        shutil.rmtree(compatdata_path)
                        deleted_items.append(f"Compatdata folder: {compatdata_path}")
                        logger.info(f"Deleted compatdata folder: {compatdata_path}")
                    else:
                        error_msg = f"Safety validation failed for compatdata: {compatdata_path}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                else:
                    logger.info(f"Compatdata folder not found, skipping: {compatdata_path}")
            except Exception as e:
                error_msg = f"Failed to delete compatdata folder: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        else:
            logger.info(f"Compatdata preservation requested - skipping compatdata deletion")
        
        # Resultado
        if errors:
            error_summary = "; ".join(errors)
            logger.error(f"Partial deletion of {name}: {error_summary}")
            return False, f"Partial deletion: {error_summary}"
        else:
            compatdata_note = " (including save data)" if delete_compatdata else " (save data preserved)"
            success_msg = f"Successfully deleted {name}{compatdata_note}. Items removed: {'; '.join(deleted_items)}"
            logger.info(success_msg)
            return True, success_msg
    
    @staticmethod
    def _validate_deletion_safety(game_info: Dict) -> bool:
        """
        Validações de segurança para evitar deleção acidental.
        
        Args:
            game_info: Informações do jogo
            
        Returns:
            True se seguro para deletar, False caso contrário
        """
        appid = game_info['appid']
        name = game_info['name']
        installdir = game_info['installdir']
        acf_path = game_info['acf_path']
        game_path = game_info['game_path']
        
        # 1. Verificar se é realmente jogo ACCELA
        if not GameManager._is_accela_game(game_info, game_info['library_path']):
            logger.error(f"SAFETY: Game {name} is not an ACCELA game")
            return False
        
        # 2. Verificar se paths são válidos e seguros
        if not acf_path or not acf_path.endswith('.acf'):
            logger.error(f"SAFETY: Invalid ACF path: {acf_path}")
            return False
        
        if not game_path or 'common' not in game_path:
            logger.error(f"SAFETY: Invalid game path: {game_path}")
            return False
        
        # 3. Verificar se ACF filename corresponde ao APPID
        expected_acf_name = f"appmanifest_{appid}.acf"
        if not acf_path.endswith(expected_acf_name):
            logger.error(f"SAFETY: ACF filename mismatch. Expected: {expected_acf_name}, Got: {os.path.basename(acf_path)}")
            return False
        
        # 4. Verificar se pasta do jogo corresponde ao installdir
        expected_game_path = os.path.join(game_info['library_path'], 'steamapps', 'common', installdir)
        if os.path.normpath(game_path) != os.path.normpath(expected_game_path):
            logger.error(f"SAFETY: Game path mismatch. Expected: {expected_game_path}, Got: {game_path}")
            return False
        
        # 5. Verificar se não está tentando deletar pasta system
        dangerous_paths = ['windows', 'system32', 'program files', 'programdata', 'root']
        # Verificar apenas o nome da pasta base, não o caminho completo
        folder_name = os.path.basename(game_path).lower()
        for dangerous in dangerous_paths:
            if folder_name == dangerous:
                logger.error(f"SAFETY: Dangerous folder name detected: {folder_name}")
                return False
        
        return True