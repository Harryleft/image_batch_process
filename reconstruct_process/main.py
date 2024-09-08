# -*- coding: utf-8 -*-
import tkinter as tk
from images_processor_gui import ImageProcessorGUI


def main():
    """
    主函数
    :return:
    """
    root = tk.Tk()
    root.geometry("400x300")
    ImageProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
