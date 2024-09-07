import os
import re
import shutil
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import piexif


class ImageProcessor:
    """
    图片处理器
    """
    def __init__(self):
        self.source_folders = []
        self.target_folder = ""

    def add_folder(self):
        """
        添加文件夹
        :return:
        """
        folder = filedialog.askdirectory()
        if folder and folder not in self.source_folders:
            self.source_folders.append(folder)
            self.listbox.insert(tk.END, folder)

    def remove_folder(self):
        """
        删除文件夹
        :return:
        """
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.listbox.delete(index)
            del self.source_folders[index]

    def select_target_folder(self):
        """
        选择目标文件夹
        :return:
        """
        self.target_folder = filedialog.askdirectory()
        if self.target_folder:
            messagebox.showinfo("目标文件夹",
                                f"已选择目标文件夹: {self.target_folder}")

    def process_images(self):
        """
        处理图片
        :return:
        """
        if not self.source_folders:
            messagebox.showerror("错误", "请至少添加一个源文件夹")
            return
        if not self.target_folder:
            messagebox.showerror("错误", "请选择目标文件夹")
            return

        try:
            collected_images = self.collect_and_deduplicate_images()
            self.rename_images(collected_images)
            messagebox.showinfo("成功", "图片处理完成")
        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错: {str(e)}")

    def get_image_date(self, file_path):
        """
        获取图片日期
        :param file_path:
        :return:
        """
        try:
            img = Image.open(file_path)
            exif_data = img._getexif()
            if exif_data:
                exif = piexif.load(img.info["exif"])
                date_time = exif["0th"][piexif.ImageIFD.DateTime].decode(
                    "utf-8")
                return datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass

        file_name = os.path.basename(file_path)
        date_pattern = r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})"
        match = re.search(date_pattern, file_name)
        if match:
            try:
                date_parts = map(int, match.groups())
                return datetime(*date_parts)
            except ValueError:
                pass

        return datetime.fromtimestamp(os.path.getmtime(file_path))

    def get_file_hash(self, file_path):
        """
        获取文件哈希值
        :param file_path:
        :return:
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def collect_and_deduplicate_images(self):
        """
        收集并去重图片
        :return:
        """
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        collected_images = []
        hash_dict = {}

        for folder in self.source_folders:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        source_path = os.path.join(root, file)
                        try:
                            file_hash = self.get_file_hash(source_path)
                        except Exception as e:
                            print(f"Error processing {file}: {e}")
                            continue

                        if file_hash not in hash_dict:
                            target_path = os.path.join(self.target_folder, file)

                            counter = 1
                            while os.path.exists(target_path):
                                name, ext = os.path.splitext(file)
                                target_path = os.path.join(self.target_folder,
                                                           f"{name}_{counter}{ext}")
                                counter += 1

                            try:
                                shutil.copy2(source_path, target_path)
                                collected_images.append(target_path)
                                hash_dict[file_hash] = target_path
                            except Exception as e:
                                print(f"Error copying {file}: {e}")

        return collected_images

    def rename_images(self, image_files):
        """
        重命名图片
        :param image_files:
        :return:
        """
        image_dates = []
        for f in image_files:
            date = self.get_image_date(f)
            image_dates.append((f, date))

        image_dates.sort(key=lambda x: x[1])

        for index, (old_path, date) in enumerate(image_dates, start=1):
            old_name = os.path.basename(old_path)
            time_info = re.search(r"\d{8}_\d{6}", old_name)
            time_str = time_info.group(0) if time_info else date.strftime(
                "%Y%m%d_%H%M%S")

            file_extension = os.path.splitext(old_name)[1]
            new_name = f"{index:04d}_{time_str}{file_extension}"
            new_path = os.path.join(self.target_folder, new_name)

            try:
                os.rename(old_path, new_path)
            except Exception as e:
                print(f"Failed to rename {old_name}: {e}")



