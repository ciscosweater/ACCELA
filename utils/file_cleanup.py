"""
File Cleanup Manager - Limpeza de arquivos parciais e temporários
"""
import os
import shutil
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class FileCleanupManager:
    """Gerencia limpeza de arquivos temporários e parciais"""
    
    def __init__(self):
        self.temp_extensions = ['.tmp', '.partial', '.downloading', '.temp', '.incomplete']
        self.temp_files = ['keys.vdf', 'manifest', 'appinfo.vdf']
        self.temp_directories = ['temp', 'cache', 'tmp']
        # Padrões adicionais para arquivos do DepotDownloaderMod
        self.depotdownloader_patterns = [
            # Arquivos que podem ser criados durante o download
            '*.tmp', '*.partial', '*.downloading',
            # Manifest files temporários
            'manifest_*.depot', '*.manifest.tmp',
            # Arquivos de chunk do Steam
            '*.chunk', '*.chunk.tmp',
            # Padrões de bloqueio
            '*.lock', '*.download', '~$*'
        ]
        
    def cleanup_partial_download(self, download_dir: str, session_id: str = ""):
        """Limpa arquivos parciais de download cancelado"""
        try:
            logger.info(f"Starting cleanup for session {session_id or 'unknown'}")
            
            # Remover arquivos temporários no diretório atual
            self._cleanup_current_directory()
            
            # Remover arquivos parciais no diretório de download
            if download_dir and os.path.exists(download_dir):
                self._cleanup_download_directory(download_dir, session_id)
            
            # Limpar diretórios temporários conhecidos
            self._cleanup_temp_directories()
            
            logger.info("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _cleanup_current_directory(self):
        """Remove arquivos temporários no diretório atual"""
        try:
            current_dir = os.getcwd()
            
            for temp_file in self.temp_files:
                temp_path = os.path.join(current_dir, temp_file)
                if os.path.exists(temp_path):
                    try:
                        if os.path.isdir(temp_path):
                            shutil.rmtree(temp_path)
                            logger.info(f"Removed temporary directory: {temp_path}")
                        else:
                            os.remove(temp_path)
                            logger.info(f"Removed temporary file: {temp_path}")
                    except OSError as e:
                        logger.warning(f"Failed to remove {temp_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Error cleaning current directory: {e}")
    
    def _cleanup_download_directory(self, download_dir: str, session_id: str):
        """Remove arquivos parciais no diretório de download"""
        try:
            for root, dirs, files in os.walk(download_dir):
                # Remover arquivos parciais
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if self._is_partial_file(file, session_id):
                        try:
                            os.remove(file_path)
                            logger.info(f"Removed partial file: {file_path}")
                        except OSError as e:
                            logger.warning(f"Failed to remove {file_path}: {e}")
                
                # Remover diretórios vazios
                for dir_name in dirs[:]:  # Copiar lista para modificar durante iteração
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if os.path.isdir(dir_path) and not os.listdir(dir_path):
                            os.rmdir(dir_path)
                            logger.info(f"Removed empty directory: {dir_path}")
                            dirs.remove(dir_name)  # Remover da lista para não processar novamente
                    except OSError:
                        pass  # Diretório não está vazio ou não pode ser removido
                        
        except Exception as e:
            logger.error(f"Error cleaning download directory {download_dir}: {e}")
    
    def _cleanup_temp_directories(self):
        """Limpa diretórios temporários conhecidos"""
        try:
            base_dirs = [
                os.getcwd(),
                os.path.expanduser("~/.cache"),
                "/tmp" if os.name != "nt" else os.environ.get("TEMP", "")
            ]
            
            for base_dir in base_dirs:
                if not base_dir or not os.path.exists(base_dir):
                    continue
                    
                for temp_dir in self.temp_directories:
                    temp_path = os.path.join(base_dir, temp_dir)
                    if os.path.exists(temp_path):
                        try:
                            # Verificar se é seguro remover (contém apenas arquivos temp)
                            if self._is_safe_to_remove_temp_dir(temp_path):
                                shutil.rmtree(temp_path)
                                logger.info(f"Removed temporary directory: {temp_path}")
                        except OSError as e:
                            logger.warning(f"Failed to remove temp dir {temp_path}: {e}")
                            
        except Exception as e:
            logger.error(f"Error cleaning temporary directories: {e}")
    
    def _is_partial_file(self, filename: str, session_id: str = "") -> bool:
        """Verifica se arquivo é parcial/temporário"""
        # Verificar extensões temporárias
        if any(filename.lower().endswith(ext) for ext in self.temp_extensions):
            return True
        
        # Verificar padrões de nome de arquivo
        temp_patterns = [
            f"_{session_id}_" if session_id else "",
            "temp_", "tmp_", "partial_",
            ".download", ".incomplete",
            "~$", ".lock"
        ]
        
        filename_lower = filename.lower()
        return any(pattern and pattern in filename_lower for pattern in temp_patterns)
    
    def _is_safe_to_remove_temp_dir(self, dir_path: str) -> bool:
        """Verifica se é seguro remover diretório temporário"""
        try:
            # Verificar se diretório contém apenas arquivos temporários
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if not self._is_partial_file(file):
                        logger.warning(f"Non-temporary file found in temp dir: {file}")
                        return False
                
                # Limitar profundidade para evitar acidentes
                level = root.replace(dir_path, '').count(os.sep)
                if level > 3:
                    logger.warning(f"Temp directory too deep: {root}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking temp directory safety: {e}")
            return False
    
    def cleanup_old_logs(self, days: int = 7):
        """Remove logs antigos"""
        try:
            import time
            
            log_files = []
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 3600)
            
            # Procurar arquivos de log
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith('.log') or file.startswith('app'):
                        file_path = os.path.join(root, file)
                        try:
                            file_time = os.path.getmtime(file_path)
                            if file_time < cutoff_time:
                                log_files.append(file_path)
                        except OSError:
                            continue
            
            # Remover logs antigos
            for log_file in log_files:
                try:
                    os.remove(log_file)
                    logger.info(f"Removed old log: {log_file}")
                except OSError as e:
                    logger.warning(f"Failed to remove old log {log_file}: {e}")
            
            if log_files:
                logger.info(f"Cleaned up {len(log_files)} old log files")
                
        except Exception as e:
            logger.error(f"Error cleaning old logs: {e}")
    
    def get_disk_usage_info(self, path: str = ".") -> dict:
        """Retorna informações de uso de disco"""
        try:
            usage = shutil.disk_usage(path)
            return {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "usage_percent": round((usage.used / usage.total) * 100, 2)
            }
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {}
    
    def cleanup_cache_files(self):
        """Limpa arquivos de cache conhecidos"""
        try:
            cache_patterns = [
                "*.cache",
                "*.tmp",
                "__pycache__",
                ".pytest_cache",
                "*.pyc",
                "*.pyo"
            ]
            
            import glob
            
            cleaned_count = 0
            for pattern in cache_patterns:
                files = glob.glob(pattern, recursive=True)
                for file_path in files:
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                        cleaned_count += 1
                    except OSError as e:
                        logger.warning(f"Failed to remove cache {file_path}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} cache files")
                
        except Exception as e:
            logger.error(f"Error cleaning cache files: {e}")
    
    def verify_download_integrity(self, download_dir: str) -> List[str]:
        """Verifica integridade de arquivos baixados"""
        try:
            issues = []
            
            if not os.path.exists(download_dir):
                return ["Download directory does not exist"]
            
            # Verificar arquivos vazios
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.getsize(file_path) == 0:
                            issues.append(f"Empty file found: {file_path}")
                    except OSError:
                        issues.append(f"Cannot access file: {file_path}")
            
            # Verificar espaço em disco
            disk_info = self.get_disk_usage_info(download_dir)
            if disk_info.get("free_gb", 0) < 1.0:  # Menos de 1GB
                issues.append(f"Low disk space: {disk_info.get('free_gb', 0):.2f}GB free")
            
            return issues
            
        except Exception as e:
            logger.error(f"Error verifying download integrity: {e}")
            return [f"Error during verification: {e}"]