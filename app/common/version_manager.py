# coding: utf-8
"""
版本管理器 - 统一管理软件版本信息
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from .logger import Logger

logger = Logger.get_logger('version_manager')


class VersionManager:
    """版本管理器"""
    
    def __init__(self, version_file_path: Optional[str] = None):
        """
        初始化版本管理器
        
        Args:
            version_file_path: 版本信息文件路径，默认为项目根目录下的version.json
        """
        if version_file_path:
            self.version_file = Path(version_file_path)
        else:
            # 默认版本文件位置
            project_root = Path(__file__).parent.parent.parent
            self.version_file = project_root / "version.json"
            
        self._version_info = self._load_version_info()
        
    def _load_version_info(self) -> Dict[str, Any]:
        """加载版本信息"""
        default_info = {
            "version": "v0.1.0",
            "build_number": 1,
            "release_date": time.strftime("%Y-%m-%d"),
            "release_notes": "",
            "pre_release": False,
            "changelog": [],
            "build_info": {
                "build_time": "",
                "build_environment": "",
                "python_version": "",
                "platform": ""
            }
        }
        
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    loaded_info = json.load(f)
                    # 合并默认信息，确保所有字段都存在
                    for key, value in default_info.items():
                        if key not in loaded_info:
                            loaded_info[key] = value
                    return loaded_info
            except Exception as e:
                logger.error(f"Failed to load version info: {e}")
                
        return default_info
        
    def save_version_info(self):
        """保存版本信息到文件"""
        try:
            # 确保目录存在
            self.version_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(self._version_info, f, indent=2, ensure_ascii=False)
            logger.info(f"Version info saved to: {self.version_file}")
        except Exception as e:
            logger.error(f"Failed to save version info: {e}")
            
    @property
    def version(self) -> str:
        """获取当前版本号"""
        return self._version_info["version"]
        
    @version.setter
    def version(self, value: str):
        """设置版本号"""
        self._version_info["version"] = value
        
    @property
    def build_number(self) -> int:
        """获取构建号"""
        return self._version_info["build_number"]
        
    @build_number.setter
    def build_number(self, value: int):
        """设置构建号"""
        self._version_info["build_number"] = value
        
    @property
    def release_date(self) -> str:
        """获取发布日期"""
        return self._version_info["release_date"]
        
    @release_date.setter
    def release_date(self, value: str):
        """设置发布日期"""
        self._version_info["release_date"] = value
        
    @property
    def release_notes(self) -> str:
        """获取发布说明"""
        return self._version_info["release_notes"]
        
    @release_notes.setter
    def release_notes(self, value: str):
        """设置发布说明"""
        self._version_info["release_notes"] = value
        
    @property
    def pre_release(self) -> bool:
        """是否为预发布版本"""
        return self._version_info["pre_release"]
        
    @pre_release.setter
    def pre_release(self, value: bool):
        """设置是否为预发布版本"""
        self._version_info["pre_release"] = value
        
    @property
    def full_version(self) -> str:
        """获取完整版本信息"""
        version = self.version
        if self.pre_release:
            version += "-pre"
        return f"{version}.{self.build_number}"
        
    def increment_version(self, version_type: str = "patch"):
        """
        递增版本号
        
        Args:
            version_type: 版本类型，可选值: major, minor, patch
        """
        current = self.version.lstrip('v')
        parts = current.split('.')
        
        if len(parts) != 3:
            logger.warning(f"Invalid version format: {current}")
            return
            
        major, minor, patch = map(int, parts)
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        elif version_type == "patch":
            patch += 1
        else:
            logger.error(f"Invalid version type: {version_type}")
            return
            
        self.version = f"v{major}.{minor}.{patch}"
        self.build_number += 1
        self.release_date = time.strftime("%Y-%m-%d")
        
        logger.info(f"Version incremented to: {self.version}")
        
    def add_changelog_entry(self, entry: str, entry_type: str = "feature"):
        """
        添加更新日志条目
        
        Args:
            entry: 更新内容
            entry_type: 更新类型，如 feature, bugfix, improvement, breaking
        """
        changelog_entry = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": self.version,
            "type": entry_type,
            "description": entry
        }
        
        if "changelog" not in self._version_info:
            self._version_info["changelog"] = []
            
        self._version_info["changelog"].insert(0, changelog_entry)  # 最新的在前面
        
        # 限制changelog条目数量，避免文件过大
        if len(self._version_info["changelog"]) > 100:
            self._version_info["changelog"] = self._version_info["changelog"][:100]
            
        logger.info(f"Added changelog entry: {entry}")
        
    def update_build_info(self, build_info: Dict[str, str]):
        """
        更新构建信息
        
        Args:
            build_info: 构建信息字典
        """
        if "build_info" not in self._version_info:
            self._version_info["build_info"] = {}
            
        self._version_info["build_info"].update(build_info)
        logger.info("Build info updated")
        
    def get_version_info(self) -> Dict[str, Any]:
        """获取完整的版本信息"""
        return self._version_info.copy()
        
    def get_display_version(self) -> str:
        """获取用于显示的版本字符串"""
        version = self.version
        if self.pre_release:
            version += " (预发布)"
        return version
        
    def compare_version(self, other_version: str) -> int:
        """
        比较版本号
        
        Args:
            other_version: 要比较的版本号
            
        Returns:
            -1: 当前版本较旧
             0: 版本相同
             1: 当前版本较新
        """
        try:
            current = self.version.lstrip('v').split('.')
            other = other_version.lstrip('v').split('.')
            
            # 补齐长度
            max_len = max(len(current), len(other))
            current.extend(['0'] * (max_len - len(current)))
            other.extend(['0'] * (max_len - len(other)))
            
            current_parts = [int(x) for x in current]
            other_parts = [int(x) for x in other]
            
            if current_parts < other_parts:
                return -1
            elif current_parts > other_parts:
                return 1
            else:
                return 0
                
        except ValueError as e:
            logger.error(f"Invalid version format for comparison: {e}")
            return 0
            
    def is_newer_than(self, other_version: str) -> bool:
        """检查当前版本是否比指定版本新"""
        return self.compare_version(other_version) > 0
        
    def is_older_than(self, other_version: str) -> bool:
        """检查当前版本是否比指定版本旧"""
        return self.compare_version(other_version) < 0
        
    def export_version_summary(self) -> str:
        """导出版本摘要信息"""
        summary = f"""
B4B Assistant 版本信息
====================
版本号: {self.version}
构建号: {self.build_number}
发布日期: {self.release_date}
预发布: {'是' if self.pre_release else '否'}

最近更新:
"""
        
        # 显示最近5条更新日志
        recent_changes = self._version_info.get("changelog", [])[:5]
        for change in recent_changes:
            summary += f"- [{change['type']}] {change['description']} ({change['date']})\n"
            
        return summary


# 创建全局版本管理器实例
version_manager = VersionManager()
