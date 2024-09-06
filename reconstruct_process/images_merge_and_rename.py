import os
import re
import shutil
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import piexif


class ImageProcessorGUI:
    def __init__(self, master):
        self.master = master
        master.title("图片处理器")
        master.geometry("600x400")

        self.source_folders = []
        self.target_folder = ""

        # 创建并放置控件
        self.create_widgets()

    def create_widgets(self):
        # 源文件夹列表框
        self.listbox_frame = tk.Frame(self.master)
        self.listbox_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.listbox_label = tk.Label(self.listbox_frame, text="源文件夹:")
        self.listbox_label.pack(anchor=tk.W)

        self.listbox = tk.Listbox(self.listbox_frame)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # 按钮
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)

        self.add_button = tk.Button(self.button_frame, text="添加文件夹",
                                    command=self.add_folder)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(self.button_frame, text="删除文件夹",
                                       command=self.remove_folder)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.target_button = tk.Button(self.master, text="选择目标文件夹",
                                       command=self.select_target_folder)
        self.target_button.pack(pady=5)

        self.process_button = tk.Button(self.master, text="处理图片",
                                        command=self.process_images)
        self.process_button.pack(pady=10)

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.source_folders:
            self.source_folders.append(folder)
            self.listbox.insert(tk.END, folder)

    def remove_folder(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.listbox.delete(index)
            del self.source_folders[index]

    def select_target_folder(self):
        self.target_folder = filedialog.askdirectory()
        if self.target_folder:
            messagebox.showinfo("目标文件夹",
                                f"已选择目标文件夹: {self.target_folder}")

    def process_images(self):
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
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def collect_and_deduplicate_images(self):
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        collected_images = []
        hash_dict = {}

        for folder in self.source_folders:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        source_path = os.path.join(root, file)
                        file_hash = self.get_file_hash(source_path)

                        if file_hash not in hash_dict:
                            target_path = os.path.join(self.target_folder, file)

                            counter = 1
                            while os.path.exists(target_path):
                                name, ext = os.path.splitext(file)
                                target_path = os.path.join(self.target_folder,
                                                           f"{name}_{counter}{ext}")
                                counter += 1

                            shutil.copy2(source_path, target_path)
                            collected_images.append(target_path)
                            hash_dict[file_hash] = target_path

        return collected_images

    def rename_images(self, image_files):
        image_dates = []
        for f in image_files:
            try:
                date = self.get_image_date(f)
                image_dates.append((f, date))
            except Exception as e:
                print(f"Error processing {f}: {e}")

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


def main():
    root = tk.Tk()
    ImageProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
