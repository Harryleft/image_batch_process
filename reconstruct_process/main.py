# -*- coding: utf-8 -*-
import tkinter as tk
from reconstruct_process.images_processor_gui import ImageProcessorGUI


def main():
    """
    主函数
    :return:
    """
    root = tk.Tk()
    ImageProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
