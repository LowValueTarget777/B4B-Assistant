import os
from pathlib import Path
from shutil import copy, copytree
from distutils.sysconfig import get_python_lib # type: ignore

# 1. activate virtual environment
#    $ conda activate YOUR_ENV_NAME
#
# 2. run deploy script
#    $ python deploy.py
BASE_DIR = Path(__file__).parent.absolute()

args = [
    "nuitka",
    "--standalone",
    "--assume-yes-for-downloads",
    "--mingw64",
    "--report=report.xml",
    f'--windows-icon-from-ico={BASE_DIR/"app"/"resource"/"images"/"logo.ico"}',
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
    " --output-filename=B4ba.exe",
    f'--output-dir={BASE_DIR/"build"}',
    f'{BASE_DIR/"main.py"}',
]

dist_folder = Path(f"{BASE_DIR}/build/main.dist/")

copied_site_packages = [
    "numpy",
    "PIL",
    "openvino",
    "numpy.libs",
    "scipy.libs",
    "rapidocr_openvino",
]

copied_standard_packages = [
    "hashlib.py",
    "hmac.py",
    "random.py",
    "secrets.py",
    "uuid.py",
]


# run nuitka
# https://blog.csdn.net/qq_25262697/article/details/129302819
# https://www.cnblogs.com/happylee666/articles/16158458.html
def copy_appdata(src="AppData", dst=dist_folder):
    def ignore_files(dir, files):
        return ["game_positions.json","deck.json"] if dir.endswith("AppData") else []

    src_path = os.path.join(os.path.dirname(__file__), src)
    dst_path = os.path.join(dst, src)

    if os.path.exists(src_path):
        copytree(src_path, dst_path, ignore=ignore_files, dirs_exist_ok=True)


os.system(" ".join(args))

# copy Appdata to dist folder
copy_appdata()

# copy site-packages to dist folder
site_packages = Path(get_python_lib())

for src in copied_site_packages:
    src = site_packages / src
    dist = dist_folder / src.name

    print(f"Coping site-packages `{src}` to `{dist}`")

    try:
        if src.is_file():
            copy(src, dist)
        else:
            copytree(src, dist)
    except:
        pass


# copy standard library
for file in copied_standard_packages:
    src = site_packages.parent / file
    dist = dist_folder / src.name

    print(f"Coping stand library `{src}` to `{dist}`")

    try:
        if src.is_file():
            copy(src, dist)
        else:
            copytree(src, dist)
    except:
        pass
