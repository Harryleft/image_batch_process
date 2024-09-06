# -*- coding: utf-8 -*-
"""
对多文件夹下的图片开展批量重组和命名

功能：
    1. 从指定的源文件夹中收集图片文件，并复制到目标文件夹。
    2. 通过计算文件的MD5哈希值来避免重复文件。
    3. 根据图片的拍摄时间或文件名中的时间信息对图片进行排序和重命名。

主要函数：
    - get_image_date(file_path): 获取图片的拍摄时间或文件名中的时间信息。
    - rename_images(image_files, target_folder): 根据时间信息对图片进行排序和重命名。
    - collect_and_duplicate_images(source_folders, target_folder): 收集并复制图片文件，避免重复。
    - get_file_hash(file_path): 计算文件的MD5哈希值。
    - main(): 主函数，执行收集、复制和重命名图片的操作。

使用方法：
    1. 设置源文件夹列表 source_folders 。
    2. 运行 main()函数。
"""
import hashlib
import os
import re
import shutil
from datetime import datetime
from PIL import Image
import piexif


def get_image_date(file_path):
    """
    获取图片的拍摄时间或文件名中的时间信息
    :param file_path:
    :return:
    """
    # 1. 尝试从文件名提取时间
    file_name = os.path.basename(file_path)
    date_pattern = (
        r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})"
    )
    match = re.search(date_pattern, file_name)
    if match:
        try:
            date_parts = map(int, match.groups())
            year, month, day, hour, minute, second = date_parts
            if 1 <= month <= 12 and 1 <= day <= 31:
                return datetime(year, month, day, hour, minute, second)
            else:
                print(f"Invalid date in filename: {file_name}")
        except ValueError as e:
            print(f"Failed to parse date from filename {file_name}: {e}")

    # 2. 尝试从EXIF数据获取拍摄时间
    try:
        img = Image.open(file_path)
        exif_data = img._getexif()
        if exif_data:
            exif = piexif.load(img.info["exif"])
            date_time = exif["0th"][piexif.ImageIFD.DateTime].decode("utf-8")
            return datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
    except:
        pass

    # 如果都失败，返回文件修改时间
    return datetime.fromtimestamp(os.path.getmtime(file_path))


def rename_images(image_files, target_folder):
    """
    根据时间信息对图片进行排序和重命名
    :param image_files:
    :param target_folder:
    :return:
    """
    # 获取每个图片的日期并排序
    image_dates = []
    for f in image_files:
        try:
            date = get_image_date(f)
            image_dates.append((f, date))
        except Exception as e:
            print(f"Error processing {f}: {e}")

    image_dates.sort(key=lambda x: x[1])

    # 重命名文件
    for index, (old_path, date) in enumerate(image_dates, start=1):
        old_name = os.path.basename(old_path)
        # 提取原始文件名中的时间信息（如果有）
        time_info = re.search(r"\d{8}_\d{6}", old_name)
        time_str = time_info.group(0) if time_info else date.strftime("%Y%m%d_%H%M%S")

        # 构建新文件名
        file_extension = os.path.splitext(old_name)[1]
        new_name = f"{index:04d}_{time_str}{file_extension}"
        new_path = os.path.join(target_folder, new_name)

        # 重命名文件
        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {old_name} -> {new_name}")
        except Exception as e:
            print(f"Failed to rename {old_name}: {e}")


def collect_and_duplicate_images(source_folders, target_folder):
    """
    收集并复制图片文件，避免重复
    :param source_folders:
    :param target_folder:
    :return:
    """
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
    collected_images = []
    hash_dict = {}

    for folder in source_folders:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(image_extensions):
                    source_path = os.path.join(root, file)
                    file_hash = get_file_hash(source_path)

                    if file_hash not in hash_dict:
                        target_path = os.path.join(target_folder, file)

                        # 如果目标文件已存在，添加数字后缀
                        counter = 1
                        while os.path.exists(target_path):
                            name, ext = os.path.splitext(file)
                            target_path = os.path.join(
                                target_folder, f"{name}_{counter}{ext}"
                            )
                            counter += 1

                        shutil.copy2(source_path, target_path)
                        collected_images.append(target_path)
                        hash_dict[file_hash] = target_path
                        print(f"Copied: {source_path} -> {target_path}")
                    else:
                        print(f"Skipped duplicate: {source_path}")

    return collected_images


def get_file_hash(file_path):
    """计算文件的 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main():
    """主函数"""
    # 源文件夹列表
    source_folders = [
        r"S:\照片",
        # 添加更多文件夹路径...
    ]

    # 目标文件夹
    target_folder = "target_folder"

    # 确保目标文件夹存在
    os.makedirs(target_folder, exist_ok=True)

    # 收集所有图片到目标文件夹
    collected_images = collect_and_duplicate_images(source_folders, target_folder)

    # 重命名收集到的图片
    rename_images(collected_images, target_folder)


if __name__ == "__main__":
    main()
