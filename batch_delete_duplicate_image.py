# -*- coding: utf-8 -*-
"""
批量删除指定文件路径下的重复图片文件
重复图片特征：
    1. 文件大小相同
    2. 重复文件名在后缀前有(1)、(2)等数字

例如：
    - 文件1：1543675753021(1).jpg
    - 文件2：1543675753021.jpg
"""
import os
import re


def delete_duplicate_images(directory):
    """
    删除指定目录中的重复图片文件
    :param directory:
    :return:
    """

    # 获取目录中的所有文件
    files = os.listdir(directory)

    # 正则表达式匹配带有(1)、(2)等标记的文件
    pattern = re.compile(r"^(.+)\(\d+\)(\.[^.]+)$")

    for file in files:
        file_path = os.path.join(directory, file)

        # 检查是否为文件（而非目录）
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)

            # 检查文件名是否匹配模式
            match = pattern.match(file)
            if match:
                original_name = match.group(1) + match.group(2)

                # 检查是否存在原始文件（没有数字标记的文件）
                if original_name in files:
                    original_path = os.path.join(directory, original_name)

                    # 如果原始文件存在且大小相同，则删除带数字标记的文件
                    if (
                        os.path.exists(original_path)
                        and os.path.getsize(original_path) == file_size
                    ):
                        os.remove(file_path)
                        print(f"Deleted duplicate file: {file}")


def main():
    """
    主函数
    :return:
    """
    # 使用示例
    # directory = r"S:\BaiduNetdiskDownload\"
    directory = r"[你的文件路径]"
    delete_duplicate_images(directory)


if __name__ == "__main__":
    main()
