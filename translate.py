import os
import glob
import subprocess

# 设置基础路径
base_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(base_path, 'app', 'view', 'ui')
view_path = os.path.join(base_path, 'app', 'view')
output_path = os.path.join(base_path, 'app', 'resource', 'i18n', 'app.zh_CN.ts')

# 收集需要处理的Python文件
ui_files = glob.glob(os.path.join(ui_path, '*_ui.py'))
view_files = glob.glob(os.path.join(view_path, '*.py'))

# 合并所有文件路径
all_files = ui_files + view_files

# 确保输出目录存在
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# 构建命令
cmd = ['pyside6-lupdate'] + all_files + ['-ts', output_path]

# 执行命令
try:
    subprocess.run(cmd, check=True)
    print(f"翻译文件已成功生成到: {output_path}")
    
    # 用 pyside6-linguist 打开翻译文件
    linguist_cmd = ['pyside6-linguist', output_path]
    subprocess.Popen(linguist_cmd)
    print("已启动 Qt Linguist")
except subprocess.CalledProcessError as e:
    print(f"生成翻译文件时发生错误: {e}")
