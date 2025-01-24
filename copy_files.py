import os
import sys
from pathlib import Path
from shutil import copy, copytree
from distutils.sysconfig import get_python_lib # type: ignore

# Set stdout encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

def copy_appdata(src="AppData", dist_folder="build/main.dist"):
    """Copy application data files"""
    def ignore_files(dir, files):
        return ["game_positions.json", "deck.json"] if dir.endswith("AppData") else []

    src_path = os.path.join(os.getcwd(), src)
    dst_path = os.path.join(os.getcwd(), dist_folder, src)

    print(f"Copying application data from {src_path} to {dst_path}")
    if os.path.exists(src_path):
        copytree(src_path, dst_path, ignore=ignore_files, dirs_exist_ok=True)

def copy_packages(dist_folder="build/main.dist"):
    """Copy required package files"""
    site_packages = Path(get_python_lib())
    dist_folder = Path(os.getcwd()) / dist_folder

    # Site packages to copy
    copied_site_packages = [
        "numpy",
        "PIL",
        "openvino",
        "numpy.libs",
        "scipy.libs",
        "rapidocr_openvino",
    ]

    # Standard library files to copy
    copied_standard_packages = [
        "hashlib.py",
        "hmac.py",
        "random.py",
        "secrets.py",
        "uuid.py",
    ]

    # Copy site packages
    for package in copied_site_packages:
        src = site_packages / package
        dist = dist_folder / src.name
        print(f"Copying package {src} to {dist}")
        try:
            if src.is_file():
                copy(src, dist)
            else:
                copytree(src, dist, dirs_exist_ok=True)
        except Exception as e:
            print(f"Error copying {package}: {e}")

    # Copy standard library files
    for file in copied_standard_packages:
        src = site_packages.parent / file
        dist = dist_folder / src.name
        print(f"Copying standard library {src} to {dist}")
        try:
            if src.is_file():
                copy(src, dist)
            else:
                copytree(src, dist, dirs_exist_ok=True)
        except Exception as e:
            print(f"Error copying {file}: {e}")

def main():
    """Main function"""
    try:
        dist_folder = "build/main.dist"
        os.makedirs(dist_folder, exist_ok=True)
        
        try:
            print("Starting file copy...")
        except UnicodeEncodeError:
            print("[INFO] Starting file copy...")
            
        copy_appdata(dist_folder=dist_folder)
        copy_packages(dist_folder=dist_folder)
        
        try:
            print("File copy completed!")
        except UnicodeEncodeError:
            print("[INFO] File copy completed!")
        
    except Exception as e:
        try:
            print(f"Error: {e}")
        except UnicodeEncodeError:
            print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
