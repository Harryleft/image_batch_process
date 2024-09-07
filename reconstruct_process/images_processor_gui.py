# -*- coding: utf-8 -*-
import tkinter as tk
from reconstruct_process.images_processor import ImageProcessor


class ImageProcessorGUI:
    """
    图片处理器GUI
    """
    def __init__(self, master):
        self.master = master
        master.title("ImagesMerge")
        master.geometry("600x400")

        self.processor = ImageProcessor()

        # 创建并放置控件
        self.create_widgets()

    def create_widgets(self):
        # 源文件夹列表显示框
        self.create_origin_folder_show_area()

        # 按钮
        self.create_button()

    def create_button(self):
        # 按钮
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)

        self.add_button = tk.Button(self.button_frame, text="添加文件夹",
                                    command=ImageProcessor.add_folder)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(self.button_frame, text="删除文件夹",
                                       command=ImageProcessor.remove_folder)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.target_button = tk.Button(self.master, text="选择目标文件夹",
                                       command=ImageProcessor.select_target_folder)
        self.target_button.pack(pady=5)

        self.process_button = tk.Button(self.master, text="处理图片",
                                        command=ImageProcessor.process_images)
        self.process_button.pack(pady=10)

    def create_origin_folder_show_area(self):

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
