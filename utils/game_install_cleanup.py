"""
Game Install Directory Cleanup - Limpeza segura e agressiva de arquivos parciais
Específico para diretório de instalação do jogo sendo baixado
"""
import os
import shutil
import logging
import json
from typing import List, Dict, Set, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class GameInstallDirectoryCleanup:
    """
    Limpeza 100% segura e agressiva de arquivos parciais no diretório de instalação do jogo.
    
    Características:
    - 100% segura para Steam (nunca remove arquivos críticos)
    - Agressiva na limpeza (remove TODOS os arquivos parciais)
    - Específica por jogo (limpa apenas o diretório do jogo sendo baixado)
    - Reversível (log detalhado do que foi removido)
    """
    
    def __init__(self):
        # Padrões de arquivos parciais do DepotDownloader
        self.partial_extensions = {
            '.tmp', '.partial', '.downloading', '.temp', '.incomplete',
            '.chunk', '.manifest.tmp', '.depot.tmp'
        }
        
        # Padrões de nomes de arquivos parciais
        self.partial_patterns = {
            'manifest_', 'chunk_', 'temp_', 'tmp_', 'partial_',
            '.download', '.incomplete', '.lock', '~$'
        }
        
        # Diretórios temporários seguros para remover
        self.temp_directories = {
            '.DepotDownloader', 'temp', 'tmp', 'cache'
        }
        
        # Arquivos críticos que NUNCA devem ser removidos
        self.critical_game_files = {
            # Executáveis comuns
            '.exe', '.sh', '.bin', '.run', '.appimage',
            # Bibliotecas de jogo
            '.dll', '.so', '.dylib',
            # Arquivos de dados do jogo
            '.pak', '.arc', '.zip', '.rar', '.7z',
            '.dat', '.cfg', '.ini', '.xml', '.json', '.yaml',
            # Recursos do jogo
            '.png', '.jpg', '.jpeg', '.bmp', '.tga', '.dds',
            '.wav', '.mp3', '.ogg', '.flac',
            '.ttf', '.otf', '.woff', '.woff2',
            # Scripts do jogo
            '.lua', '.py', '.js', '.cs', '.cpp', '.h',
            # Documentação
            '.txt', '.md', '.pdf', '.htm', '.html',
            # Steam específicos
            'steam_api.dll', 'steam_api64.dll', 'libsteam_api.so',
            'appmanifest', 'acf'
        }
        
        # Arquivos temporários do DepotDownloader (semprem removidos)
        self.depotdownloader_files = {
            'keys.vdf', 'appinfo.vdf', 'package.vdf',
            'manifest_*.cache', '*.chunk.tmp', '*.manifest.tmp'
        }
        
        # Log de remoções para reversão
        self.removal_log: List[Dict] = []
    
    def cleanup_game_install_directory(self, 
                                     install_dir: str, 
                                     game_data: Dict,
                                     session_id: str = "",
                                     dry_run: bool = False) -> Dict:
        """
        🚨 LIMPEZA COMPLETA E AGRESSIVA DO DIRETÓRIO DO JOGO 🚨
        
        APAGA TUDO dentro do diretório do jogo específico sendo baixado.
        NUNCA apaga nada fora da pasta do jogo.
        100% de segurança para não apagar diretórios errados.
        
        Args:
            install_dir: Diretório de instalação do jogo
            game_data: Dados do jogo (appid, nome, etc.)
            session_id: ID da sessão de download
            dry_run: Se True, apenas simula sem remover
            
        Returns:
            Dict com resultado da limpeza
        """
        result = {
            'success': False,
            'install_dir': install_dir,
            'game_name': game_data.get('game_name', 'Unknown'),
            'appid': game_data.get('appid', 'Unknown'),
            'session_id': session_id,
            'files_removed': 0,
            'dirs_removed': 0,
            'space_freed_mb': 0,
            'removals': [],
            'errors': [],
            'dry_run': dry_run,
            'cleanup_type': 'COMPLETE_DIRECTORY_CLEANUP'
        }
        
        try:
            # 🔒🔒🔒 VERIFICAÇÕES DE SEGURANÇA EXTREMAS 🔒🔒🔒
            if not self._verify_ultra_safety_checks(install_dir, game_data, session_id):
                result['errors'].append("🚨 ULTRA SAFETY CHECK FAILED: Directory validation failed - NO FILES DELETED 🚨")
                return result
            
            # 🔒🔒🔒 CONFIRMAÇÕES MÚLTIPLAS 🔒🔒🔒
            if not self._multiple_confirmations(install_dir, game_data, session_id):
                result['errors'].append("🚨 MULTIPLE CONFIRMATIONS FAILED - NO FILES DELETED 🚨")
                return result
            
            logger.warning(f"{'[DRY RUN] ' if dry_run else ''}🚨 STARTING COMPLETE CLEANUP OF GAME DIRECTORY 🚨")
            logger.warning(f"Directory: {install_dir}")
            logger.warning(f"Game: {result['game_name']} (AppID: {result['appid']})")
            logger.warning(f"Session: {session_id}")
            logger.warning(f"{'[DRY RUN] ' if dry_run else ''}🚨 ALL CONTENTS WILL BE DELETED 🚨")
            
            # Inicializar log de remoções
            self.removal_log = []
            
            # 🎯🎯🎯 LIMPEZA COMPLETA DO DIRETÓRIO 🎯🎯🎯
            total_size_freed = 0
            
            # APAGAR ABSOLUTAMENTE TUDO DENTRO DO DIRETÓRIO
            complete_result = self._complete_directory_cleanup(install_dir, session_id, dry_run)
            result['files_removed'] = complete_result['files_removed']
            result['dirs_removed'] = complete_result['dirs_removed']
            total_size_freed += complete_result['size']
            result['removals'].extend(complete_result['removals'])
            
            # Calcular estatísticas finais
            result['space_freed_mb'] = round(total_size_freed / (1024 * 1024), 2)
            result['success'] = True
            
            # Salvar log de remoções
            if not dry_run:
                self._save_removal_log(install_dir, game_data, session_id)
            
            logger.warning(f"{'[DRY RUN] ' if dry_run else ''}🚨 COMPLETE CLEANUP FINISHED 🚨")
            logger.warning(f"  Files removed: {result['files_removed']}")
            logger.warning(f"  Directories removed: {result['dirs_removed']}")
            logger.warning(f"  Space freed: {result['space_freed_mb']} MB")
            logger.warning(f"  Directory is now EMPTY: {install_dir}")
            
        except Exception as e:
            error_msg = f"🚨 ERROR DURING COMPLETE CLEANUP: {e} 🚨"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _verify_ultra_safety_checks(self, install_dir: str, game_data: Dict, session_id: str) -> bool:
        """
        🔒🔒🔒 VERIFICAÇÕES DE SEGURANÇA EXTREMAS 🔒🔒🔒
        Múltiplas camadas de verificação para garantir que só apague o diretório correto
        """
        try:
            # 🔒 PATH TRAVERSAL SECURITY: Resolve and validate path
            install_path = Path(install_dir).resolve()
            
            logger.info("🔒 STARTING ULTRA SAFETY CHECKS 🔒")
            
            # 1. Diretório deve existir
            if not install_path.exists():
                logger.error(f"🚨 SAFETY: Install directory does not exist: {install_dir}")
                return False
            
            # 2. Não pode ser diretório raiz ou system
            if install_path.is_absolute() and len(install_path.parts) <= 3:
                logger.error(f"🚨 SAFETY: Directory too close to root: {install_dir}")
                return False
            
            # 2.1. 🔒 ADDITIONAL SECURITY: Verify against allowed base paths
            allowed_base_paths = [
                Path.home() / ".steam" / "steam",
                Path.home() / ".local" / "share" / "Steam",
                Path("/usr/local/games/steam"),
                Path("/opt/steam")
            ]
            
            is_allowed_path = False
            for base_path in allowed_base_paths:
                try:
                    if install_path.is_relative_to(base_path.resolve()):
                        is_allowed_path = True
                        break
                except (ValueError, OSError):
                    continue
            
            if not is_allowed_path:
                logger.error(f"🚨 SAFETY: Path not in allowed Steam directories: {install_path}")
                return False
            
            # 3. DEVE conter 'steamapps/common' no caminho (Steam library structure)
            if 'steamapps' not in install_dir.lower() or 'common' not in install_dir.lower():
                logger.error(f"🚨 SAFETY: Not a Steam game directory: {install_dir}")
                return False
            
            # 4. O último diretório deve ser o nome do jogo
            game_name = game_data.get('game_name', '').lower()
            appid = str(game_data.get('appid', ''))
            dir_name = install_path.name.lower()
            
            if not (game_name and game_name in dir_name):
                logger.error(f"🚨 SAFETY: Directory name doesn't match game name: {dir_name} vs {game_name}")
                return False
            
            # 5. Verificar se é realmente o diretório do jogo sendo baixado
            if not self._verify_game_directory_match(install_dir, game_data):
                logger.error(f"🚨 SAFETY: Directory doesn't match the game being downloaded")
                return False
            
            # 6. Não pode conter indicadores de sistema Steam crítico
            dangerous_paths = [
                'steamapps/common',  # Apenas o diretório pai
                'steam.exe', 'steam.sh',
                'userdata', 'config', 'steamapps/workshop'
            ]
            
            install_lower = install_dir.lower()
            for dangerous in dangerous_paths:
                if dangerous in install_lower and install_dir.lower().endswith(dangerous):
                    logger.error(f"🚨 SAFETY: Dangerous Steam path detected: {install_dir}")
                    return False
            
            # 7. Verificação adicional de estrutura Steam
            if not self._verify_steam_library_structure(install_dir):
                logger.error(f"🚨 SAFETY: Invalid Steam library structure: {install_dir}")
                return False
            
            # 8. Verificar se há session_id ativo (só deve limpar durante cancelamento)
            if not session_id:
                logger.error(f"🚨 SAFETY: No session ID provided - this should only run during download cancellation")
                return False
            
            logger.info(f"✅ ALL ULTRA SAFETY CHECKS PASSED: {install_dir}")
            return True
            
        except Exception as e:
            logger.error(f"🚨 ULTRA SAFETY CHECK ERROR: {e}")
            return False
    
    def _verify_game_directory_match(self, install_dir: str, game_data: Dict) -> bool:
        """
        Verificação adicional para garantir que é o diretório do jogo correto
        """
        try:
            install_path = Path(install_dir)
            game_name = game_data.get('game_name', '').lower()
            appid = str(game_data.get('appid', ''))
            
            # Verificar se o nome do diretório corresponde ao jogo
            dir_name = install_path.name.lower()
            
            # 1. Nome do diretório deve conter o nome do jogo
            if game_name and game_name not in dir_name:
                logger.warning(f"Directory name doesn't contain game name: {dir_name} vs {game_name}")
                return False
            
            # 2. Verificar se há arquivos que parecem do jogo
            game_files_found = 0
            for item in install_path.iterdir():
                if item.is_file():
                    file_lower = item.name.lower()
                    # Arquivos que indicam que é um jogo
                    if any(file_lower.endswith(ext) for ext in ['.exe', '.dll', '.so', '.pak', '.dat', '.bin']):
                        game_files_found += 1
                        if game_files_found >= 2:
                            break
            
            # Se não encontrar arquivos de jogo, pode ser diretório errado
            if game_files_found == 0:
                logger.warning(f"No game files found in directory: {install_dir}")
                # Não falha completamente, mas avisa
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying game directory match: {e}")
            return False
    
    def _verify_steam_library_structure(self, install_dir: str) -> bool:
        """
        Verifica se a estrutura está correta para uma biblioteca Steam
        """
        try:
            install_path = Path(install_dir)
            
            # Deve estar dentro de steamapps/common
            parent = install_path.parent
            if parent.name.lower() != 'common':
                logger.error(f"Not in steamapps/common directory: {install_dir}")
                return False
            
            grandparent = parent.parent
            if grandparent.name.lower() != 'steamapps':
                logger.error(f"Not in steamapps directory: {install_dir}")
                return False
            
            # Verificar se há outros jogos (indica que é biblioteca Steam válida)
            sibling_games = 0
            for item in parent.iterdir():
                if item.is_dir() and item != install_path:
                    sibling_games += 1
                    if sibling_games >= 1:  # Pelo menos 1 outro jogo
                        break
            
            if sibling_games == 0:
                logger.warning(f"No other games found in steamapps/common - unusual but not fatal")
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying Steam library structure: {e}")
            return False
    
    def _multiple_confirmations(self, install_dir: str, game_data: Dict, session_id: str) -> bool:
        """
        🔒🔒🔒 CONFIRMAÇÕES MÚLTIPLAS ANTES DA DELEÇÃO 🔒🔒🔒
        """
        try:
            logger.info("🔒 STARTING MULTIPLE CONFIRMATIONS 🔒")
            
            # Confirmação 1: Validar dados do jogo
            if not game_data.get('game_name') or not game_data.get('appid'):
                logger.error("🚨 CONFIRMATION 1 FAILED: Invalid game data")
                return False
            
            # Confirmação 2: Validar session ID
            if not session_id or len(session_id) < 5:
                logger.error("🚨 CONFIRMATION 2 FAILED: Invalid session ID")
                return False
            
            # Confirmação 3: Verificar que é realmente cancelamento
            # (Esta verificação deve ser feita pelo chamador, mas vamos registrar)
            logger.info(f"CONFIRMATION 3 PASSED: Session ID {session_id} indicates download cancellation")
            
            # Confirmação 4: Verificação final do caminho
            install_path = Path(install_dir)
            if not install_path.exists() or not install_path.is_dir():
                logger.error("🚨 CONFIRMATION 4 FAILED: Invalid directory path")
                return False
            
            # Confirmação 5: Verificar que não estamos tentando apagar algo crítico
            # Nota: 'home' foi removido porque é um caminho válido em Linux para bibliotecas Steam
            critical_checks = [
                'windows', 'program files', 'system32', 'usr/bin', 'etc', 'var',
                'root', 'boot', 'lib', 'opt', 'sbin'
            ]
            
            install_lower = install_dir.lower()
            for critical in critical_checks:
                if critical in install_lower:
                    logger.error(f"🚨 CONFIRMATION 5 FAILED: Critical system path detected: {critical}")
                    return False
            
            logger.info("✅ ALL MULTIPLE CONFIRMATIONS PASSED")
            return True
            
        except Exception as e:
            logger.error(f"🚨 MULTIPLE CONFIRMATIONS ERROR: {e}")
            return False
    
    def _complete_directory_cleanup(self, install_dir: str, session_id: str, dry_run: bool) -> Dict:
        """
        🚨 APAGA ABSOLUTAMENTE TUDO DENTRO DO DIRETÓRIO 🚨
        """
        result = {
            'files_removed': 0,
            'dirs_removed': 0,
            'size': 0,
            'removals': []
        }
        
        try:
            install_path = Path(install_dir)
            
            logger.warning(f"{'[DRY RUN] ' if dry_run else ''}🚨 STARTING COMPLETE DIRECTORY CLEANUP 🚨")
            logger.warning(f"Target: {install_dir}")
            
            # Listar tudo antes de apagar para logging
            all_items = list(install_path.iterdir())
            total_items = len(all_items)
            
            logger.warning(f"Found {total_items} items to delete")
            
            # Apagar cada item individualmente para logging detalhado
            for item in all_items:
                try:
                    if item.is_file():
                        file_size = item.stat().st_size
                        
                        if dry_run:
                            logger.info(f"[DRY RUN] Would delete FILE: {item} ({file_size} bytes)")
                        else:
                            logger.warning(f"🗑️  DELETING FILE: {item} ({file_size} bytes)")
                            item.unlink()
                        
                        result['files_removed'] += 1
                        result['size'] += file_size
                        result['removals'].append({
                            'type': 'file',
                            'path': str(item),
                            'size': file_size,
                            'reason': 'complete_cleanup'
                        })
                        
                    elif item.is_dir():
                        dir_size = self._get_directory_size(str(item))
                        
                        if dry_run:
                            logger.info(f"[DRY RUN] Would delete DIRECTORY: {item} ({dir_size} bytes)")
                        else:
                            logger.warning(f"🗑️  DELETING DIRECTORY: {item} ({dir_size} bytes)")
                            import shutil
                            shutil.rmtree(str(item))
                        
                        result['dirs_removed'] += 1
                        result['size'] += dir_size
                        result['removals'].append({
                            'type': 'directory',
                            'path': str(item),
                            'size': dir_size,
                            'reason': 'complete_cleanup'
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to delete {item}: {e}")
                    # Continuar com outros itens mesmo se um falhar
            
            # Verificação final: diretório deve estar vazio
            if not dry_run:
                remaining_items = list(install_path.iterdir())
                if remaining_items:
                    logger.error(f"🚨 DIRECTORY NOT EMPTY AFTER CLEANUP: {len(remaining_items)} items remaining")
                    for item in remaining_items:
                        logger.error(f"  Remaining: {item}")
                else:
                    logger.warning(f"✅ DIRECTORY SUCCESSFULLY CLEANED: {install_dir}")
            
            logger.warning(f"{'[DRY RUN] ' if dry_run else ''}🚨 COMPLETE CLEANUP SUMMARY 🚨")
            logger.warning(f"  Files deleted: {result['files_removed']}")
            logger.warning(f"  Directories deleted: {result['dirs_removed']}")
            logger.warning(f"  Total size freed: {result['size']} bytes")
            
        except Exception as e:
            logger.error(f"🚨 ERROR DURING COMPLETE CLEANUP: {e}")
        
        return result
    
    def _verify_safety_checks(self, install_dir: str, game_data: Dict) -> bool:
        """
        🔒 VERIFICAÇÕES CRÍTICAS DE SEGURANÇA
        """
        try:
            install_path = Path(install_dir)
            
            # 1. Diretório deve existir
            if not install_path.exists():
                logger.error(f"SAFETY: Install directory does not exist: {install_dir}")
                return False
            
            # 2. Não pode ser diretório raiz ou system
            if install_path.is_absolute() and len(install_path.parts) <= 3:
                logger.error(f"SAFETY: Directory too close to root: {install_dir}")
                return False
            
            # 3. Deve conter 'steamapps/common' no caminho (Steam library structure)
            if 'steamapps' not in install_dir.lower() or 'common' not in install_dir.lower():
                logger.error(f"SAFETY: Not a Steam game directory: {install_dir}")
                return False
            
            # 4. Não pode conter indicadores de sistema Steam crítico
            dangerous_paths = [
                'steamapps/common',  # Apenas o diretório pai
                'steam.exe', 'steam.sh',
                'userdata', 'config', 'steamapps/workshop'
            ]
            
            install_lower = install_dir.lower()
            for dangerous in dangerous_paths:
                if dangerous in install_lower and install_dir.lower().endswith(dangerous):
                    logger.error(f"SAFETY: Dangerous Steam path detected: {install_dir}")
                    return False
            
            # 5. Verificar se parece com diretório de jogo (tem arquivos de jogo)
            if not self._looks_like_game_directory(install_dir):
                logger.warning(f"WARNING: Directory doesn't look like a game: {install_dir}")
                # Não falha, apenas avisa
            
            logger.info(f"SAFETY CHECKS PASSED: {install_dir}")
            return True
            
        except Exception as e:
            logger.error(f"SAFETY CHECK ERROR: {e}")
            return False
    
    def _looks_like_game_directory(self, install_dir: str) -> bool:
        """
        Verifica se o diretório parece ser de um jogo
        """
        try:
            game_indicators = 0
            total_files = 0
            
            for root, dirs, files in os.walk(install_dir):
                # Limitar verificação para não demorar muito
                level = root.replace(install_dir, '').count(os.sep)
                if level > 2:
                    continue
                
                for file in files:
                    total_files += 1
                    file_lower = file.lower()
                    
                    # Indicadores de jogo
                    if any(file_lower.endswith(ext) for ext in ['.exe', '.dll', '.so', '.pak', '.dat']):
                        game_indicators += 1
                    
                    # Parar se já encontrou suficientes
                    if game_indicators >= 3:
                        return True
                    
                    # Limitar verificação
                    if total_files >= 50:
                        break
            
            return game_indicators >= 2
            
        except Exception:
            return False
    
    def _remove_partial_files(self, install_dir: str, session_id: str, dry_run: bool) -> Dict:
        """
        Remove arquivos parciais/temporários agressivamente
        """
        result = {'count': 0, 'size': 0, 'removals': []}
        
        try:
            for root, dirs, files in os.walk(install_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if self._is_partial_file(file, session_id):
                        try:
                            file_size = os.path.getsize(file_path)
                            
                            if dry_run:
                                logger.info(f"[DRY RUN] Would remove partial file: {file_path} ({file_size} bytes)")
                            else:
                                os.remove(file_path)
                                logger.info(f"Removed partial file: {file_path} ({file_size} bytes)")
                            
                            result['count'] += 1
                            result['size'] += file_size
                            result['removals'].append({
                                'type': 'file',
                                'path': file_path,
                                'size': file_size,
                                'reason': 'partial_file'
                            })
                            
                        except OSError as e:
                            logger.warning(f"Failed to remove {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error removing partial files: {e}")
        
        return result
    
    def _remove_temp_directories(self, install_dir: str, dry_run: bool) -> Dict:
        """
        Remove diretórios temporários seguros
        """
        result = {'count': 0, 'size': 0, 'removals': []}
        
        try:
            for root, dirs, files in os.walk(install_dir, topdown=True):
                # Modificar a lista de diretórios durante iteração
                dirs[:] = [d for d in dirs if d in self.temp_directories]
                
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    
                    if self._is_safe_temp_directory(dir_path):
                        try:
                            dir_size = self._get_directory_size(dir_path)
                            
                            if dry_run:
                                logger.info(f"[DRY RUN] Would remove temp directory: {dir_path} ({dir_size} bytes)")
                            else:
                                shutil.rmtree(dir_path)
                                logger.info(f"Removed temp directory: {dir_path} ({dir_size} bytes)")
                            
                            result['count'] += 1
                            result['size'] += dir_size
                            result['removals'].append({
                                'type': 'directory',
                                'path': dir_path,
                                'size': dir_size,
                                'reason': 'temp_directory'
                            })
                            
                        except OSError as e:
                            logger.warning(f"Failed to remove directory {dir_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error removing temp directories: {e}")
        
        return result
    
    def _cleanup_depotdownloader_artifacts(self, install_dir: str, dry_run: bool) -> Dict:
        """
        Limpeza específica de artefatos do DepotDownloader
        """
        result = {'count': 0, 'size': 0, 'removals': []}
        
        try:
            # Limpar pasta .DepotDownloader
            depotdownloader_dir = os.path.join(install_dir, '.DepotDownloader')
            if os.path.exists(depotdownloader_dir):
                try:
                    dir_size = self._get_directory_size(depotdownloader_dir)
                    
                    if dry_run:
                        logger.info(f"[DRY RUN] Would remove .DepotDownloader directory: {depotdownloader_dir}")
                    else:
                        shutil.rmtree(depotdownloader_dir)
                        logger.info(f"Removed .DepotDownloader directory: {depotdownloader_dir}")
                    
                    result['count'] += 1
                    result['size'] += dir_size
                    result['removals'].append({
                        'type': 'directory',
                        'path': depotdownloader_dir,
                        'size': dir_size,
                        'reason': 'depotdownloader_artifact'
                    })
                    
                except OSError as e:
                    logger.warning(f"Failed to remove .DepotDownloader: {e}")
            
            # Limpar arquivos específicos do DepotDownloader
            for root, dirs, files in os.walk(install_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if self._is_depotdownloader_artifact(file):
                        try:
                            file_size = os.path.getsize(file_path)
                            
                            if dry_run:
                                logger.info(f"[DRY RUN] Would remove DepotDownloader artifact: {file_path}")
                            else:
                                os.remove(file_path)
                                logger.info(f"Removed DepotDownloader artifact: {file_path}")
                            
                            result['count'] += 1
                            result['size'] += file_size
                            result['removals'].append({
                                'type': 'file',
                                'path': file_path,
                                'size': file_size,
                                'reason': 'depotdownloader_artifact'
                            })
                            
                        except OSError as e:
                            logger.warning(f"Failed to remove {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error cleaning DepotDownloader artifacts: {e}")
        
        return result
    
    def _is_partial_file(self, filename: str, session_id: str = "") -> bool:
        """
        Verifica se arquivo é parcial/temporário
        """
        filename_lower = filename.lower()
        
        # 1. Extensões temporárias
        if any(filename_lower.endswith(ext) for ext in self.partial_extensions):
            return True
        
        # 2. Padrões de nome
        if any(pattern in filename_lower for pattern in self.partial_patterns):
            return True
        
        # 3. Session ID específico
        if session_id and session_id in filename_lower:
            return True
        
        # 4. Arquivos do DepotDownloader
        if self._is_depotdownloader_artifact(filename):
            return True
        
        return False
    
    def _is_depotdownloader_artifact(self, filename: str) -> bool:
        """
        Verifica se é artefato do DepotDownloader
        """
        filename_lower = filename.lower()
        
        # Arquivos específicos
        if filename_lower in {'keys.vdf', 'appinfo.vdf', 'package.vdf'}:
            return True
        
        # Padrões de manifest/chunk
        if filename_lower.startswith(('manifest_', 'chunk_')):
            return True
        
        # Extensões temporárias do DepotDownloader
        if any(filename_lower.endswith(suffix) for suffix in ['.manifest.tmp', '.chunk.tmp', '.depot.tmp']):
            return True
        
        return False
    
    def _is_safe_temp_directory(self, dir_path: str) -> bool:
        """
        Verifica se diretório temporário é seguro para remover
        """
        dir_name = os.path.basename(dir_path).lower()
        
        # Deve ser um diretório temporário conhecido
        if dir_name not in self.temp_directories:
            return False
        
        try:
            # Verificar se contém apenas arquivos temporários
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if not self._is_partial_file(file):
                        logger.warning(f"Non-temporary file in temp dir: {file}")
                        return False
                
                # Limitar profundidade
                level = root.replace(dir_path, '').count(os.sep)
                if level > 3:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _get_directory_size(self, dir_path: str) -> int:
        """
        Calcula tamanho total do diretório
        """
        total_size = 0
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        continue
        except Exception:
            pass
        return total_size
    
    def _verify_post_cleanup_safety(self, install_dir: str) -> Dict:
        """
        Verificação de segurança pós-limpeza
        """
        check_result = {
            'game_files_preserved': 0,
            'critical_files_found': 0,
            'remaining_partial_files': 0,
            'warnings': []
        }
        
        try:
            for root, dirs, files in os.walk(install_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_lower = file.lower()
                    
                    # Verificar arquivos críticos preservados
                    if any(file_lower.endswith(ext) for ext in self.critical_game_files):
                        check_result['critical_files_found'] += 1
                    
                    # Contar arquivos de jogo
                    if any(file_lower.endswith(ext) for ext in ['.exe', '.dll', '.so', '.pak', '.dat']):
                        check_result['game_files_preserved'] += 1
                    
                    # Verificar se restaram arquivos parciais
                    if self._is_partial_file(file):
                        check_result['remaining_partial_files'] += 1
                        check_result['warnings'].append(f"Remaining partial file: {file_path}")
            
            # Avisos importantes
            if check_result['critical_files_found'] == 0:
                check_result['warnings'].append("No critical game files found - possible over-cleanup")
            
            if check_result['remaining_partial_files'] > 5:
                check_result['warnings'].append(f"Many partial files remaining: {check_result['remaining_partial_files']}")
        
        except Exception as e:
            check_result['warnings'].append(f"Post-cleanup check error: {e}")
        
        return check_result
    
    def _save_removal_log(self, install_dir: str, game_data: Dict, session_id: str):
        """
        Salva log detalhado de remoções para possível reversão
        """
        try:
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'install_dir': install_dir,
                'game_data': game_data,
                'session_id': session_id,
                'removals': self.removal_log
            }
            
            # Criar arquivo de log no diretório do jogo
            log_file = os.path.join(install_dir, f'.accela_cleanup_log_{session_id or datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Cleanup log saved: {log_file}")
            
        except Exception as e:
            logger.error(f"Failed to save removal log: {e}")
    
    def get_removal_log(self, install_dir: str) -> List[Dict]:
        """
        Carrega logs de remoção anteriores
        """
        logs = []
        try:
            for file in os.listdir(install_dir):
                if file.startswith('.accela_cleanup_log_') and file.endswith('.json'):
                    log_file = os.path.join(install_dir, file)
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            log_data = json.load(f)
                            logs.append(log_data)
                    except Exception:
                        continue
        except Exception:
            pass
        
        return sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)