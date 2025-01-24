import os
import sys
from pathlib import Path
from shutil import copy, copytree
from distutils.sysconfig import get_python_lib # type: ignore

# 设置标准输出编码为utf-8
sys.stdout.reconfigure(encoding='utf-8')

def copy_appdata(src="AppData", dist_folder="build/main.dist"):
    """复制应用数据文件"""
    def ignore_files(dir, files):
        return ["game_positions.json", "deck.json"] if dir.endswith("AppData") else []

    src_path = os.path.join(os.getcwd(), src)
    dst_path = os.path.join(os.getcwd(), dist_folder, src)

    print(f"复制应用数据从 {src_path} 到 {dst_path}")
    if os.path.exists(src_path):
        copytree(src_path, dst_path, ignore=ignore_files, dirs_exist_ok=True)

def copy_packages(dist_folder="build/main.dist"):
    """复制必要的包文件"""
    site_packages = Path(get_python_lib())
    dist_folder = Path(os.getcwd()) / dist_folder

    # 需要复制的站点包
    copied_site_packages = [
        "numpy",
        "PIL",
        "openvino",
        "numpy.libs",
        "scipy.libs",
        "rapidocr_openvino",
    ]

    # 需要复制的标准库
    copied_standard_packages = [
        "hashlib.py",
        "hmac.py",
        "random.py",
        "secrets.py",
        "uuid.py",
    ]

    # 复制站点包
    for package in copied_site_packages:
        src = site_packages / package
        dist = dist_folder / src.name
        print(f"复制包 {src} 到 {dist}")
        try:
            if src.is_file():
                copy(src, dist)
            else:
                copytree(src, dist, dirs_exist_ok=True)
        except Exception as e:
            print(f"复制 {package} 时出错: {e}")

    # 复制标准库文件
    for file in copied_standard_packages:
        src = site_packages.parent / file
        dist = dist_folder / src.name
        print(f"复制标准库 {src} 到 {dist}")
        try:
            if src.is_file():
                copy(src, dist)
            else:
                copytree(src, dist, dirs_exist_ok=True)
        except Exception as e:
            print(f"复制 {file} 时出错: {e}")

def main():
    """主函数"""
    try:
        dist_folder = "build/main.dist"
        os.makedirs(dist_folder, exist_ok=True)
        
        try:
            print("开始复制文件...")
        except UnicodeEncodeError:
            print("[INFO] Starting file copy...")
            
        copy_appdata(dist_folder=dist_folder)
        copy_packages(dist_folder=dist_folder)
        
        try:
            print("文件复制完成!")
        except UnicodeEncodeError:
            print("[INFO] File copy completed!")
        
    except Exception as e:
        try:
            print(f"错误: {e}")
        except UnicodeEncodeError:
            print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
