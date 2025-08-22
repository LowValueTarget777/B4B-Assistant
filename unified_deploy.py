# coding: utf-8
"""
统一部署脚本 - 整合 deploy.py 和 copy_files.py 功能
支持 venv 虚拟环境的自动化打包和部署
"""

import os
import sys
import subprocess
import shutil
import json
import time
import sysconfig
from pathlib import Path
import argparse


class UnifiedDeployer:
    """统一部署器 - 整合所有部署功能"""
    
    def __init__(self, use_venv=True):
        self.base_dir = Path(__file__).parent.absolute()
        self.use_venv = use_venv
        self.venv_path = self._detect_venv_path()
        self.build_dir = self.base_dir / "build"
        self.dist_dir = self.build_dir / "main.dist"
        
        # 设置 stdout 编码为 utf-8
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
            
    def _detect_venv_path(self):
        """自动检测虚拟环境路径"""
        venv_names = [".venv", "venv", "env", ".env"]
        for name in venv_names:
            venv_path = self.base_dir / name
            if venv_path.exists() and (venv_path / ("Scripts" if os.name == 'nt' else "bin")).exists():
                return venv_path
        return self.base_dir / "venv"  # 默认路径
        
    def check_environment(self):
        """检查环境和依赖"""
        print("🔍 检查环境...")
        print("=" * 50)
        
        # 检查 venv 环境
        if self.use_venv:
            if not self.venv_path.exists():
                print(f"❌ 找不到虚拟环境: {self.venv_path}")
                return False
            print(f"✅ 发现虚拟环境: {self.venv_path}")
            
            # 检查 Python 可执行文件
            if os.name == 'nt':  # Windows
                python_exe = self.venv_path / "Scripts" / "python.exe"
                pip_exe = self.venv_path / "Scripts" / "pip.exe"
            else:  # Linux/macOS
                python_exe = self.venv_path / "bin" / "python"
                pip_exe = self.venv_path / "bin" / "pip"
                
            if not python_exe.exists():
                print(f"❌ 找不到 Python 可执行文件: {python_exe}")
                return False
            print(f"✅ Python 可执行文件: {python_exe}")
            
            self.python_exe = str(python_exe)
            self.pip_exe = str(pip_exe)
        else:
            self.python_exe = sys.executable
            self.pip_exe = "pip"
        
        # 检查主程序文件
        main_py = self.base_dir / "main.py"
        if not main_py.exists():
            print(f"❌ 找不到主程序文件: {main_py}")
            return False
        print(f"✅ 主程序文件: {main_py}")
        
        return True
        
    def check_dependencies(self):
        """检查依赖包"""
        print("\n📦 检查依赖包...")
        print("-" * 30)
        
        required_packages = [
            ("nuitka", "nuitka"),
            ("pyside6", "PySide6"), 
            ("pyside6-fluent-widgets", "qfluentwidgets"),
            ("opencv-python", "cv2"),
            ("pillow", "PIL"),
            ("numpy", "numpy"),
            ("openvino", "openvino"),
            ("rapidocr-openvino", "rapidocr_openvino")
        ]
        
        missing_packages = []
        
        for pip_name, import_name in required_packages:
            try:
                result = subprocess.run(
                    [self.python_exe, "-c", f"import {import_name}"],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"✅ {pip_name}")
                else:
                    print(f"❌ {pip_name}")
                    missing_packages.append(pip_name)
            except (subprocess.TimeoutExpired, Exception):
                print(f"❌ {pip_name}")
                missing_packages.append(pip_name)
        
        if missing_packages:
            print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
            install = input("是否自动安装缺少的包? (y/N): ").lower().strip()
            if install == 'y':
                try:
                    print("正在安装缺少的包...")
                    subprocess.run([
                        self.pip_exe, "install"
                    ] + missing_packages, check=True)
                    print("✅ 依赖包安装完成")
                except subprocess.CalledProcessError as e:
                    print(f"❌ 依赖包安装失败: {e}")
                    return False
            else:
                print("❌ 请手动安装缺少的依赖包")
                return False
        
        return True
        
    def clean_build_directory(self):
        """清理构建目录"""
        print("\n🧹 清理构建目录...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"✅ 已清理: {self.build_dir}")
        
        self.build_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建构建目录: {self.build_dir}")
        
    def build_with_nuitka(self):
        """使用 Nuitka 构建应用"""
        print("\n🔨 使用 Nuitka 构建应用...")
        print("-" * 40)
        
        # Nuitka 构建参数
        nuitka_args = [
            self.python_exe, "-m", "nuitka",
            "--standalone",
            "--assume-yes-for-downloads",
            "--mingw64",
            f"--report={self.build_dir}/build_report.xml",
            f'--windows-icon-from-ico={self.base_dir}/app/resource/images/logo.ico',
            "--nofollow-import-to=numpy,scipy,PIL,colorthief,openvino",
            "--include-module=cv2,yaml",
            "--enable-plugins=pyside6",
            "--windows-product-version=0.1.0",
            "--show-progress",
            "--windows-disable-console",
            '--windows-file-description="B4B Assistant"',
            "--show-memory",
            "--windows-file-version=0.1.0",
            "--windows-company-name=ruming",
            "--output-filename=B4ba.exe",
            f'--output-dir={self.build_dir}',
            f'{self.base_dir}/main.py'
        ]
        
        try:
            print("执行 Nuitka 构建命令...")
            print(f"命令: {' '.join(nuitka_args)}")
            print()
            
            result = subprocess.run(nuitka_args, cwd=self.base_dir)
            
            if result.returncode == 0:
                print("✅ Nuitka 构建成功!")
                return True
            else:
                print(f"❌ Nuitka 构建失败，退出码: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Nuitka 构建异常: {e}")
            return False
            
    def copy_appdata(self):
        """复制 AppData 目录"""
        print("\n📁 复制 AppData 目录...")
        
        def ignore_files(dir_path, files):
            """忽略某些文件"""
            ignored = []
            for file in files:
                if file in ["game_positions.json", "deck.json"]:
                    ignored.append(file)
                    print(f"  跳过: {file}")
            return ignored
        
        src_path = self.base_dir / "AppData"
        dst_path = self.dist_dir / "AppData"
        
        if src_path.exists():
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path, ignore=ignore_files)
            print(f"✅ AppData 复制完成: {dst_path}")
        else:
            print(f"⚠️  AppData 目录不存在: {src_path}")
            
    def copy_dependencies(self):
        """复制依赖包"""
        print("\n📦 复制依赖包...")
        
        # 获取 site-packages 路径
        if self.use_venv:
            if os.name == 'nt':
                site_packages = self.venv_path / "Lib" / "site-packages"
            else:
                site_packages = self.venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        else:
            site_packages = Path(sysconfig.get_paths()["platlib"])
            
        print(f"site-packages 路径: {site_packages}")
        
        # 需要复制的包
        packages_to_copy = [
            "numpy",
            "PIL",
            "openvino",
            "numpy.libs",
            "scipy.libs",
            "rapidocr_openvino",
        ]
        
        # 复制包
        for package in packages_to_copy:
            src_package = site_packages / package
            dst_package = self.dist_dir / package
            
            if src_package.exists():
                if dst_package.exists():
                    shutil.rmtree(dst_package)
                
                if src_package.is_dir():
                    shutil.copytree(src_package, dst_package)
                else:
                    shutil.copy2(src_package, dst_package)
                    
                print(f"✅ 复制包: {package}")
            else:
                print(f"⚠️  包不存在: {package}")
                
        # 复制标准库文件
        stdlib_files = [
            "hashlib.py",
            "hmac.py", 
            "random.py",
            "secrets.py",
            "uuid.py"
        ]
        
        python_lib_dir = Path(sys.executable).parent.parent / "Lib"
        
        for file in stdlib_files:
            src_file = python_lib_dir / file
            dst_file = self.dist_dir / file
            
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"✅ 复制标准库: {file}")
            else:
                print(f"⚠️  标准库文件不存在: {file}")
                
    def create_deployment_info(self):
        """创建部署信息文件"""
        print("\n📋 创建部署信息...")
        
        # 读取版本信息
        version_file = self.base_dir / "version.json"
        version_info = {"version": "v0.1.0"}
        if version_file.exists():
            try:
                import json
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_info = json.load(f)
            except Exception as e:
                print(f"⚠️  无法读取版本信息: {e}")
        
        deployment_info = {
            "app_name": "B4B Assistant",
            "version": version_info.get("version", "v0.1.0"),
            "build_number": version_info.get("build_number", 1),
            "build_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "build_environment": "venv" if self.use_venv else "system",
            "python_version": sys.version,
            "platform": sys.platform,
            "architecture": os.name,
            "release_notes": version_info.get("release_notes", ""),
            "changelog": version_info.get("changelog", [])[:5]  # 只保留最近5条
        }
        
        info_file = self.dist_dir / "deployment_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(deployment_info, f, indent=2, ensure_ascii=False)
            
        print(f"✅ 部署信息已保存: {info_file}")
        print(f"📦 应用版本: {deployment_info['version']}")
        print(f"🔢 构建号: {deployment_info['build_number']}")
        
        # 更新版本文件的构建信息
        if version_file.exists():
            try:
                version_info["build_info"] = {
                    "build_time": deployment_info["build_time"],
                    "build_environment": deployment_info["build_environment"],
                    "python_version": sys.version,
                    "platform": sys.platform
                }
                with open(version_file, 'w', encoding='utf-8') as f:
                    json.dump(version_info, f, indent=2, ensure_ascii=False)
                print(f"✅ 版本信息已更新: {version_file}")
            except Exception as e:
                print(f"⚠️  无法更新版本信息: {e}")
        
    def validate_build(self, skip_build=False):
        """验证构建结果"""
        print("\n✅ 验证构建结果...")
        
        # 检查可执行文件 (只有在没有跳过构建时才检查)
        if not skip_build:
            exe_file = self.dist_dir / "B4ba.exe"
            if exe_file.exists():
                size_mb = exe_file.stat().st_size / (1024 * 1024)
                print(f"✅ 可执行文件: {exe_file} ({size_mb:.1f} MB)")
            else:
                print(f"❌ 可执行文件不存在: {exe_file}")
                return False
        else:
            print("⏭️  跳过可执行文件检查 (因为跳过了构建)")
            
        # 检查关键目录
        required_dirs = ["AppData"]
        for dir_name in required_dirs:
            dir_path = self.dist_dir / dir_name
            if dir_path.exists():
                print(f"✅ 目录存在: {dir_name}")
            else:
                print(f"⚠️  目录不存在: {dir_name}")
                
        # 统计文件数量
        file_count = sum(1 for _ in self.dist_dir.rglob('*') if _.is_file())
        dir_count = sum(1 for _ in self.dist_dir.rglob('*') if _.is_dir())
        
        print(f"📊 构建统计: {file_count} 个文件, {dir_count} 个目录")
        
        return True
        
    def deploy(self, skip_build=False, no_clean=False):
        """执行完整部署流程"""
        print("🚀 B4B Assistant 统一部署")
        print("=" * 50)
        print(f"项目目录: {self.base_dir}")
        print(f"构建目录: {self.build_dir}")
        print(f"输出目录: {self.dist_dir}")
        print()
        
        # 1. 检查环境
        if not self.check_environment():
            return False
            
        # 2. 检查依赖
        if not self.check_dependencies():
            return False
            
        # 3. 清理构建目录
        if not no_clean:
            self.clean_build_directory()
            
        # 4. 构建应用 (可选跳过)
        if not skip_build:
            if not self.build_with_nuitka():
                return False
        else:
            print("\n⏭️  跳过 Nuitka 构建")
            
        # 5. 复制文件
        self.copy_appdata()
        self.copy_dependencies()
        
        # 6. 创建部署信息
        self.create_deployment_info()
        
        # 7. 验证构建
        if not self.validate_build(skip_build=skip_build):
            return False
            
        print("\n🎉 部署完成!")
        print(f"输出目录: {self.dist_dir}")
        print(f"可执行文件: {self.dist_dir / 'B4ba.exe'}")
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="B4B Assistant 统一部署脚本")
    parser.add_argument("--no-venv", action="store_true", help="不使用虚拟环境")
    parser.add_argument("--no-clean", action="store_true", help="不清理构建目录")
    parser.add_argument("--skip-build", action="store_true", help="跳过 Nuitka 构建，只复制文件")
    
    args = parser.parse_args()
    
    deployer = UnifiedDeployer(use_venv=not args.no_venv)
    
    try:
        success = deployer.deploy(
            skip_build=args.skip_build,
            no_clean=args.no_clean
        )
        
        if success:
            print("\n✅ 部署成功!")
            sys.exit(0)
        else:
            print("\n❌ 部署失败!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消部署")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 部署异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
