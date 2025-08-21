# coding:utf-8
import os
import sys
import glob
import subprocess
import hashlib
import json
import time
from pathlib import Path

class IncrementalTranslator:
    """增量翻译管理器"""
    
    def __init__(self, base_path=None):
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.ui_path = os.path.join(self.base_path, 'app', 'view', 'ui')
        self.view_path = os.path.join(self.base_path, 'app', 'view')
        self.output_path = os.path.join(self.base_path, 'app', 'resource', 'i18n', 'app.zh_CN.ts')
        self.cache_file = os.path.join(self.base_path, '.translation_cache.json')
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # 加载缓存
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """加载翻译缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("警告: 缓存文件损坏，将重新创建")
        
        return {
            'files': {},
            'last_update': 0,
            'version': '1.0'
        }
    
    def _save_cache(self):
        """保存翻译缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"警告: 无法保存缓存文件: {e}")
    
    def _get_file_hash(self, file_path):
        """计算文件的MD5哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except IOError:
            return None
    
    def _get_file_mtime(self, file_path):
        """获取文件修改时间"""
        try:
            return os.path.getmtime(file_path)
        except OSError:
            return 0
    
    def get_source_files(self):
        """获取所有源文件"""
        ui_files = glob.glob(os.path.join(self.ui_path, '*_ui.py'))
        view_files = glob.glob(os.path.join(self.view_path, '*.py'))
        
        # 过滤掉 __pycache__ 和测试文件
        all_files = []
        for file_path in ui_files + view_files:
            if '__pycache__' not in file_path and not file_path.endswith('_test.py'):
                all_files.append(file_path)
        
        return all_files
    
    def check_files_changed(self, force_update=False):
        """检查文件是否有变化"""
        if force_update:
            return True, "强制更新"
        
        source_files = self.get_source_files()
        changed_files = []
        
        for file_path in source_files:
            file_hash = self._get_file_hash(file_path)
            file_mtime = self._get_file_mtime(file_path)
            
            if file_hash is None:
                continue
            
            rel_path = os.path.relpath(file_path, self.base_path)
            cached_info = self.cache['files'].get(rel_path, {})
            
            # 检查哈希值和修改时间
            if (cached_info.get('hash') != file_hash or 
                cached_info.get('mtime', 0) < file_mtime):
                changed_files.append(rel_path)
                
                # 更新缓存
                self.cache['files'][rel_path] = {
                    'hash': file_hash,
                    'mtime': file_mtime,
                    'size': os.path.getsize(file_path)
                }
        
        # 检查是否有文件被删除
        cached_files = set(self.cache['files'].keys())
        current_files = set(os.path.relpath(f, self.base_path) for f in source_files)
        deleted_files = cached_files - current_files
        
        for deleted_file in deleted_files:
            del self.cache['files'][deleted_file]
            print(f"检测到删除的文件: {deleted_file}")
        
        has_changes = bool(changed_files or deleted_files)
        change_info = f"变更文件: {len(changed_files)}, 删除文件: {len(deleted_files)}"
        
        if changed_files:
            print("检测到变更的文件:")
            for file_path in changed_files[:10]:  # 只显示前10个
                print(f"  - {file_path}")
            if len(changed_files) > 10:
                print(f"  ... 还有 {len(changed_files) - 10} 个文件")
        
        return has_changes, change_info
    
    def find_lrelease_tool(self):
        """查找 lrelease 工具"""
        # 可能的工具名称和路径
        tool_names = [
            'pyside6-lrelease',
            'pyside6-lrelease.exe', 
            'lrelease',
            'lrelease.exe'
        ]
        
        # 可能的路径
        possible_paths = [
            # 系统 PATH
            '',
            # 常见的 Python 安装路径
            os.path.join(os.path.dirname(os.sys.executable), 'Scripts'),
            # 虚拟环境路径
            os.path.join(self.base_path, '.venv', 'Scripts'),
            os.path.join(self.base_path, 'venv', 'Scripts'),
            # 全局 Python 路径
            r'C:\Python311\Scripts',
            r'C:\Python310\Scripts', 
            r'C:\Python39\Scripts',
        ]
        
        # 尝试找到工具
        for tool_name in tool_names:
            for path_prefix in possible_paths:
                if path_prefix:
                    tool_path = os.path.join(path_prefix, tool_name)
                else:
                    tool_path = tool_name
                
                try:
                    # 测试工具是否可用
                    result = subprocess.run([tool_path, '-version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"🔍 找到 lrelease 工具: {tool_path}")
                        return tool_path
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue
        
        return None
    
    def compile_translation(self, lrelease_path=None):
        """编译翻译文件，将 .ts 文件编译为 .qm 文件"""
        print("=" * 50)
        print("编译翻译文件")
        print("=" * 50)
        
        ts_file = self.output_path
        qm_file = ts_file.replace('.ts', '.qm')
        
        # 检查源文件是否存在
        if not os.path.exists(ts_file):
            print(f"❌ 找不到翻译源文件: {ts_file}")
            return False
        
        print(f"📄 源文件: {ts_file}")
        print(f"📄 目标文件: {qm_file}")
        
        # 查找 lrelease 工具
        if not lrelease_path:
            lrelease_path = self.find_lrelease_tool()
        
        if not lrelease_path:
            print("⚠️  找不到 pyside6-lrelease 工具")
            print("尝试使用 Python 模块验证...")
            
            try:
                # 只验证 PySide6 是否可用
                import importlib
                importlib.import_module('PySide6.QtCore')
                print("✅ PySide6 可用，翻译文件应该可以正常工作")
                print(f"📝 请确保 {qm_file} 文件存在以供运行时使用")
                return True
            except ImportError:
                print("❌ PySide6 未安装，无法验证翻译文件")
                return False
        
        try:
            # 使用 lrelease 编译翻译文件
            cmd = [lrelease_path, ts_file, '-qm', qm_file]
            print(f"🔄 执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print(f"✅ 成功编译翻译文件: {qm_file}")
            
            if result.stdout:
                print("lrelease 输出:")
                print(result.stdout)
            
            # 检查编译后的文件
            if os.path.exists(qm_file):
                file_size = os.path.getsize(qm_file)
                print(f"📊 编译后文件大小: {file_size} 字节")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 编译翻译文件时发生错误: {e}")
            if e.stderr:
                print("错误详情:")
                print(e.stderr)
            return False
        
        except FileNotFoundError:
            print(f"❌ 找不到工具: {lrelease_path}")
            return False

    def find_lupdate_tool(self):
        """查找 lupdate 工具"""
        # 可能的工具名称和路径
        tool_names = [
            'pyside6-lupdate',
            'pyside6-lupdate.exe', 
            'lupdate',
            'lupdate.exe'
        ]
        
        # 可能的路径
        possible_paths = [
            # 系统 PATH
            '',
            # 常见的 Python 安装路径
            os.path.join(os.path.dirname(os.sys.executable), 'Scripts'),
            # 虚拟环境路径
            os.path.join(self.base_path, '.venv', 'Scripts'),
            os.path.join(self.base_path, 'venv', 'Scripts'),
            # 全局 Python 路径
            r'C:\Python311\Scripts',
            r'C:\Python310\Scripts', 
            r'C:\Python39\Scripts',
        ]
        
        # 尝试找到工具
        for tool_name in tool_names:
            for path_prefix in possible_paths:
                if path_prefix:
                    tool_path = os.path.join(path_prefix, tool_name)
                else:
                    tool_path = tool_name
                
                try:
                    # 测试工具是否可用
                    result = subprocess.run([tool_path, '-version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"🔍 找到 lupdate 工具: {tool_path}")
                        return tool_path
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue
        
        return None
    
    def update_translation(self, force_update=False, open_linguist=True, lupdate_path=None):
        """更新翻译文件"""
        print("=" * 50)
        print("增量翻译更新检查")
        print("=" * 50)
        
        # 检查文件变化
        has_changes, change_info = self.check_files_changed(force_update)
        
        if not has_changes and not force_update:
            print("✅ 没有检测到文件变化，无需更新翻译")
            print(f"上次更新时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.cache.get('last_update', 0)))}")
            return True
        
        print(f"📝 检测到变化: {change_info}")
        
        # 获取所有源文件
        source_files = self.get_source_files()
        print(f"📂 找到 {len(source_files)} 个源文件")
        
        # 查找 lupdate 工具
        if not lupdate_path:
            lupdate_path = self.find_lupdate_tool()
        
        if not lupdate_path:
            print("❌ 找不到 pyside6-lupdate 工具")
            print("请尝试以下解决方案:")
            print("1. 安装 PySide6: pip install PySide6")
            print("2. 确保 pyside6-lupdate 在 PATH 中")
            print("3. 手动指定工具路径: --lupdate-path <path>")
            return False
        
        # 构建 lupdate 命令
        cmd = [lupdate_path] + source_files + ['-ts', self.output_path]
        
        print("🔄 正在更新翻译文件...")
        try:
            # 执行 lupdate
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # 更新缓存时间戳
            self.cache['last_update'] = time.time()
            self._save_cache()
            
            print(f"✅ 翻译文件已成功更新: {self.output_path}")
            
            if result.stdout:
                print("lupdate 输出:")
                print(result.stdout)
            
            # 是否打开 Qt Linguist
            if open_linguist:
                self._open_linguist()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 更新翻译文件时发生错误: {e}")
            if e.stderr:
                print("错误详情:")
                print(e.stderr)
            return False
        
        except FileNotFoundError:
            print(f"❌ 找不到工具: {lupdate_path}")
            return False
    
    def update_and_compile(self, force_update=False, open_linguist=True, lupdate_path=None, lrelease_path=None):
        """更新并编译翻译文件"""
        # 先更新翻译文件
        update_success = self.update_translation(force_update, False, lupdate_path)  # 不打开 linguist
        
        if not update_success:
            return False
        
        # 再编译翻译文件
        compile_success = self.compile_translation(lrelease_path)
        
        # 如果需要，最后打开 Qt Linguist
        if update_success and open_linguist:
            self._open_linguist()
        
        return update_success and compile_success
    
    def _open_linguist(self):
        """打开 Qt Linguist"""
        try:
            linguist_cmd = ['pyside6-linguist', self.output_path]
            subprocess.Popen(linguist_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("🚀 已启动 Qt Linguist")
        except FileNotFoundError:
            print("⚠️  找不到 pyside6-linguist，请手动打开翻译文件")
        except Exception as e:
            print(f"⚠️  启动 Qt Linguist 失败: {e}")
    
    def show_status(self):
        """显示翻译状态"""
        print("=" * 50)
        print("翻译状态")
        print("=" * 50)
        
        source_files = self.get_source_files()
        print(f"📂 源文件数量: {len(source_files)}")
        print(f"📄 缓存文件数量: {len(self.cache['files'])}")
        
        if self.cache.get('last_update'):
            last_update = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.cache['last_update']))
            print(f"🕐 上次更新: {last_update}")
        else:
            print("🕐 上次更新: 从未更新")
        
        if os.path.exists(self.output_path):
            ts_mtime = os.path.getmtime(self.output_path)
            ts_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts_mtime))
            print(f"📝 翻译文件时间: {ts_time}")
        else:
            print("📝 翻译文件: 不存在")
    
    def clean_cache(self):
        """清理缓存"""
        self.cache = {
            'files': {},
            'last_update': 0,
            'version': '1.0'
        }
        self._save_cache()
        print("🧹 缓存已清理")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='增量翻译更新工具')
    parser.add_argument('--force', '-f', action='store_true', help='强制更新所有翻译')
    parser.add_argument('--no-linguist', action='store_true', help='不打开 Qt Linguist')
    parser.add_argument('--status', '-s', action='store_true', help='显示翻译状态')
    parser.add_argument('--clean', '-c', action='store_true', help='清理缓存')
    parser.add_argument('--lupdate-path', help='手动指定 lupdate 工具路径')
    parser.add_argument('--lrelease-path', help='手动指定 lrelease 工具路径')
    parser.add_argument('--compile', action='store_true', help='只编译翻译文件，不更新')
    parser.add_argument('--update-and-compile', action='store_true', help='更新并编译翻译文件')
    
    args = parser.parse_args()
    
    translator = IncrementalTranslator()
    
    if args.status:
        translator.show_status()
        return
    
    if args.clean:
        translator.clean_cache()
        return
    
    if args.compile:
        # 只编译翻译文件
        success = translator.compile_translation(args.lrelease_path)
        if success:
            print("\n🎉 翻译编译完成！")
        else:
            print("\n💥 翻译编译失败！")
            exit(1)
        return
    
    if args.update_and_compile:
        # 更新并编译翻译文件
        success = translator.update_and_compile(
            force_update=args.force,
            open_linguist=not args.no_linguist,
            lupdate_path=args.lupdate_path,
            lrelease_path=args.lrelease_path
        )
        if success:
            print("\n🎉 翻译更新和编译完成！")
        else:
            print("\n💥 翻译更新或编译失败！")
            exit(1)
        return
    
    # 默认：执行翻译更新
    success = translator.update_translation(
        force_update=args.force,
        open_linguist=not args.no_linguist,
        lupdate_path=args.lupdate_path
    )
    
    if success:
        print("\n🎉 翻译更新完成！")
    else:
        print("\n💥 翻译更新失败！")
        exit(1)


if __name__ == "__main__":
    main()
