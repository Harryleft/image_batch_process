# -*- coding: utf-8 -*-
"""图片处理器的图形用户界面模块。

本模块提供了一个图形用户界面,用于与图片处理器进行交互。
它允许用户选择源文件夹和目标文件夹,并启动图片处理过程。

Classes:
    ImageProcessorGUI: 图片处理器的图形用户界面类。
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional, List, Tuple
from images_processor import ImageProcessor

class ImageProcessorGUI:
    """图片处理器的图形用户界面类。

    该类负责创建和管理用户界面,并与ImageProcessor类进行交互。

    Attributes:
        master (tk.Tk): Tkinter的主窗口对象。
        processor (ImageProcessor): ImageProcessor类的实例,用于处理图片。
        source_listbox (tk.Listbox): 显示源文件夹的列表框。
        target_label (ttk.Label): 显示目标文件夹的标签。
    """

    def __init__(self, master: tk.Tk) -> None:
        """初始化ImageProcessorGUI类。

        Args:
            master: Tkinter的主窗口对象。
        """
        self.master = master
        master.title("图片整理助手")
        self.processor = ImageProcessor()
        self.processor.add_observer(self)
        
        self.source_listbox: Optional[tk.Listbox] = None
        self.target_label: Optional[ttk.Label] = None
        
        self.setup_ui()

    def setup_ui(self) -> None:
        """设置用户界面的布局和控件。"""
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)

        self._create_source_folder_frame(main_frame)
        self._create_target_folder_frame(main_frame)
        self._create_process_button(main_frame)

    def _create_source_folder_frame(self, parent: ttk.Frame) -> None:
        """创建源文件夹框架及其子控件。

        Args:
            parent: 父框架。
        """
        source_frame = ttk.LabelFrame(parent, text="源文件夹", padding="5")
        source_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        source_frame.columnconfigure(0, weight=1)

        self.source_listbox = tk.Listbox(source_frame, height=5)
        self.source_listbox.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        source_scrollbar = ttk.Scrollbar(source_frame, orient=tk.VERTICAL, command=self.source_listbox.yview)
        source_scrollbar.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.source_listbox.configure(yscrollcommand=source_scrollbar.set)

        source_button_frame = ttk.Frame(source_frame)
        source_button_frame.grid(column=0, row=1, columnspan=2, sticky=tk.W, pady=5)

        add_button = ttk.Button(source_button_frame, text="添加源文件夹", command=self.add_source_folder)
        add_button.pack(side=tk.LEFT, padx=(0, 5))

        remove_button = ttk.Button(source_button_frame, text="删除源文件夹", command=self.remove_source_folder)
        remove_button.pack(side=tk.LEFT)

    def _create_target_folder_frame(self, parent: ttk.Frame) -> None:
        """创建目标文件夹框架及其子控件。

        Args:
            parent: 父框架。
        """
        target_frame = ttk.LabelFrame(parent, text="目标文件夹", padding="5")
        target_frame.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=5)
        target_frame.columnconfigure(1, weight=1)

        self.target_label = ttk.Label(target_frame, text="未选择")
        self.target_label.grid(column=1, row=0, sticky=tk.W, padx=5)

        target_button = ttk.Button(target_frame, text="选择目标文件夹", command=self.select_target_folder)
        target_button.grid(column=0, row=0, sticky=tk.W)

    def _create_process_button(self, parent: ttk.Frame) -> None:
        """创建处理图片按钮。

        Args:
            parent: 父框架。
        """
        process_button = ttk.Button(parent, text="处理图片", command=self.process_images)
        process_button.grid(column=0, row=2, pady=10)

    def add_source_folder(self) -> None:
        """添加源文件夹的回调函数。"""
        folder: str = filedialog.askdirectory()
        if folder:
            self.processor.add_folder(folder)

    def remove_source_folder(self) -> None:
        """删除源文件夹的回调函数。"""
        selection: Tuple[int, ...] = self.source_listbox.curselection()
        if selection:
            self.processor.remove_folder(selection[0])

    def select_target_folder(self) -> None:
        """选择目标文件夹的回调函数。"""
        folder: str = filedialog.askdirectory()
        if folder:
            self.processor.select_target_folder(folder)

    def process_images(self) -> None:
        """处理图片的回调函数。"""
        try:
            self.processor.process_images()
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def update(self, event: str, data: Optional[List[str]] = None) -> None:
        """更新GUI的回调函数,响应ImageProcessor的通知。

        Args:
            event: 事件类型的字符串。
            data: 与事件相关的数据(可选)。
        """
        if event == 'source_folders_updated':
            self.source_listbox.delete(0, tk.END)
            for folder in data:
                self.source_listbox.insert(tk.END, folder)
        elif event == 'target_folder_updated':
            self.target_label.config(text=data)
        elif event == 'collection_completed':
            messagebox.showinfo("信息", f"已收集 {data} 张图片")
        elif event == 'renaming_completed':
            messagebox.showinfo("信息", f"已重命名 {data} 张图片")
        elif event == 'processing_completed':
            messagebox.showinfo("完成", "图片处理完成")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("图片处理器")
    root.geometry("400x300")  # 设置初始窗口大小
    app = ImageProcessorGUI(root)
    root.mainloop()
