# coding:utf-8
import os
import sys
import json
import zipfile
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QMessageBox

from .logger import Logger

logger = Logger.get_logger('updater')

class UpdateChecker(QThread):
    """版本检查线程"""
    updateAvailable = Signal(dict)  # 有更新可用
    noUpdateAvailable = Signal()    # 无更新
    checkFailed = Signal(str)       # 检查失败
    
    def __init__(self, current_version: str):
        super().__init__()
        self.current_version = current_version
        self.repo_url = "https://api.github.com/repos/LowValueTarget777/B4B-Assistant"
        
    def run(self):
        """检查更新"""
        try:
            logger.info(f"Checking for updates, current version: {self.current_version}")
            
            # 获取最新发布信息
            response = requests.get(f"{self.repo_url}/releases/latest", timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data["tag_name"]
            
            # 移除 'v' 前缀进行比较
            latest_version_clean = latest_version.lstrip('v')
            current_version_clean = self.current_version.lstrip('v')
            
            logger.info(f"Latest version: {latest_version}, Current version: {self.current_version}")
            
            if self._is_newer_version(latest_version_clean, current_version_clean):
                update_info = {
                    'version': latest_version,
                    'description': release_data.get('body', ''),
                    'download_url': self._get_download_url(release_data),
                    'size': self._get_asset_size(release_data),
                    'published_at': release_data.get('published_at', '')
                }
                self.updateAvailable.emit(update_info)
            else:
                self.noUpdateAvailable.emit()
                
        except requests.RequestException as e:
            logger.error(f"Network error during update check: {e}")
            self.checkFailed.emit(f"网络错误: {str(e)}")
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            self.checkFailed.emit(f"检查更新失败: {str(e)}")
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """比较版本号"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # 补齐长度
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
        except ValueError:
            logger.warning(f"Could not parse versions: {latest} vs {current}")
            return latest != current
    
    def _get_download_url(self, release_data: dict) -> Optional[str]:
        """获取下载链接"""
        assets = release_data.get('assets', [])
        for asset in assets:
            if asset['name'].endswith('.zip'):
                return asset['browser_download_url']
        return None
    
    def _get_asset_size(self, release_data: dict) -> int:
        """获取文件大小"""
        assets = release_data.get('assets', [])
        for asset in assets:
            if asset['name'].endswith('.zip'):
                return asset.get('size', 0)
        return 0


class UpdateDownloader(QThread):
    """更新下载线程"""
    downloadProgress = Signal(int, int)  # 已下载, 总大小
    downloadFinished = Signal(str)       # 下载完成, 文件路径
    downloadFailed = Signal(str)         # 下载失败
    
    def __init__(self, download_url: str, save_path: str):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
        self._cancelled = False
        
    def run(self):
        """下载更新文件"""
        try:
            logger.info(f"Downloading update from: {self.download_url}")
            
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._cancelled:
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        self.downloadProgress.emit(downloaded_size, total_size)
            
            logger.info(f"Download completed: {self.save_path}")
            self.downloadFinished.emit(self.save_path)
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            self.downloadFailed.emit(str(e))
    
    def cancel(self):
        """取消下载"""
        self._cancelled = True


class UpdateInstaller:
    """更新安装器"""
    
    def __init__(self):
        self.app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path.cwd()
        
    def install_update(self, zip_path: str) -> bool:
        """安装更新"""
        try:
            logger.info(f"Installing update from: {zip_path}")
            
            # 创建备份目录
            backup_dir = self.app_dir / "backup"
            backup_dir.mkdir(exist_ok=True)
            
            # 解压更新文件到临时目录
            temp_dir = self.app_dir / "temp_update"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 查找解压后的应用目录
            update_source = self._find_app_directory(temp_dir)
            if not update_source:
                raise Exception("无法找到更新文件中的应用程序目录")
            
            # 备份当前应用
            self._backup_current_app(backup_dir)
            
            # 复制新文件
            self._copy_update_files(update_source, self.app_dir)
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            os.remove(zip_path)
            
            logger.info("Update installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install update: {e}")
            # 尝试恢复备份
            self._restore_backup(backup_dir)
            return False
    
    def _find_app_directory(self, temp_dir: Path) -> Optional[Path]:
        """查找应用程序目录"""
        # 查找包含 main.py 的目录
        for root, dirs, files in os.walk(temp_dir):
            if 'main.py' in files:
                return Path(root)
        return None
    
    def _backup_current_app(self, backup_dir: Path):
        """备份当前应用"""
        important_files = ['main.py', 'app', 'requirements.txt']
        
        for item in important_files:
            source = self.app_dir / item
            if source.exists():
                dest = backup_dir / item
                if source.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)
    
    def _copy_update_files(self, source: Path, dest: Path):
        """复制更新文件"""
        for item in source.iterdir():
            dest_item = dest / item.name
            
            # 跳过某些文件和目录
            if item.name in ['AppData', 'logs', '.venv', '__pycache__', '.git']:
                continue
                
            if item.is_dir():
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)
    
    def _restore_backup(self, backup_dir: Path):
        """恢复备份"""
        try:
            if backup_dir.exists():
                for item in backup_dir.iterdir():
                    dest = self.app_dir / item.name
                    if item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
                logger.info("Backup restored successfully")
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")


class UpdateManager(QObject):
    """更新管理器"""
    
    def __init__(self, current_version: str, parent=None):
        super().__init__(parent)
        self.current_version = current_version
        self.checker = None
        self.downloader = None
        self.installer = UpdateInstaller()
        
    def check_for_updates(self):
        """检查更新"""
        if self.checker and self.checker.isRunning():
            return
            
        self.checker = UpdateChecker(self.current_version)
        self.checker.start()
        return self.checker
    
    def download_update(self, download_url: str) -> UpdateDownloader:
        """下载更新"""
        if self.downloader and self.downloader.isRunning():
            self.downloader.cancel()
            self.downloader.wait()
        
        save_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), 
                                "temp", "update.zip")
        
        self.downloader = UpdateDownloader(download_url, save_path)
        self.downloader.start()
        return self.downloader
    
    def install_update(self, zip_path: str) -> bool:
        """安装更新"""
        return self.installer.install_update(zip_path)
    
    def restart_app(self):
        """重启应用程序"""
        try:
            if getattr(sys, 'frozen', False):
                # 如果是打包的exe
                subprocess.Popen([sys.executable])
            else:
                # 如果是Python脚本
                subprocess.Popen([sys.executable, 'main.py'])
            
            # 退出当前应用
            sys.exit(0)
        except Exception as e:
            logger.error(f"Failed to restart application: {e}")
