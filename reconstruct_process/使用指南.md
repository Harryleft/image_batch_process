# 使用指南

## 1. 安装 Python

1. 访问 Python 官方网站：https://www.python.org/downloads/windows/
2. 下载最新版本的 Python（例如 Python 3.9 或更高版本）
3. 运行安装程序，选择"Add Python to PATH"选项
4. 完成安装

## 2. 验证 Python 安装

1. 快捷键`win+R`，输入cmd，即可打开命令提示符（CMD）界面
2. 输入 `python --version`，应该显示 Python 版本号
3. 输入 `pip --version`，应该显示 pip 版本号

## 3. 创建项目文件夹

1. 在您想要的位置创建一个新文件夹，例如 `C:\Projects\ImageProcessor`
2. 在命令提示符中，导航到该文件夹：
   ```
   cd C:\Projects\ImageProcessor
   ```

## 4. 创建虚拟环境

1. 在项目文件夹中创建虚拟环境：
   ```
   python -m venv venv
   ```
2. 激活虚拟环境：
   ```
   venv\Scripts\activate
   ```

## 5. 安装所需的库

在激活的虚拟环境中，安装必要的库：
```
pip install Pillow piexif
```

## 6. 创建 Python 脚本

- 在项目文件夹中，将`py`文件复制到项目文件夹中

## 7. 修改脚本中的目标文件夹路径

在 `py` 文件中，找到 `main` 函数，修改 `target_folder` 变量为您的实际图片文件夹路径，例如：
```python
target_folder = r"C:\Users\YourName\Pictures\ToRename"
```

## 8. 运行脚本

在命令提示符中（确保虚拟环境已激活），运行：
```
python reorder_rename_images.py
```

## 注意事项

- 确保在运行脚本之前已经激活虚拟环境
- 如果遇到权限问题，尝试以管理员身份运行命令提示符
- 在处理重要文件之前，请先备份您的图片
