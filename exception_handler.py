# -*- coding: utf-8 -*-
"""自定义异常模块。

本模块定义了图片处理过程中可能出现的各种异常。

Classes:
    ImageProcessorError: 图片处理器基础异常类。
    FileAccessError: 文件访问错误。
    HashCalculationError: 哈希计算错误。
    ImageCopyError: 图片复制错误。
    ImageRenameError: 图片重命名错误。
"""

class ImageProcessorError(Exception):
    """图片处理器基础异常类。"""
    pass

class FileAccessError(ImageProcessorError):
    """文件访问错误。"""
    def __init__(self, file_path: str, message: str):
        self.file_path = file_path
        self.message = message
        super().__init__(f"无法访问文件 {file_path}: {message}")

class HashCalculationError(ImageProcessorError):
    """哈希计算错误。"""
    def __init__(self, file_path: str, message: str):
        self.file_path = file_path
        self.message = message
        super().__init__(f"计算文件 {file_path} 的哈希值时出错: {message}")

class ImageCopyError(ImageProcessorError):
    """图片复制错误。"""
    def __init__(self, source_path: str, target_path: str, message: str):
        self.source_path = source_path
        self.target_path = target_path
        self.message = message
        super().__init__(f"复制图片从 {source_path} 到 {target_path} 时出错: {message}")

class ImageRenameError(ImageProcessorError):
    """图片重命名错误。"""
    def __init__(self, old_path: str, new_path: str, message: str):
        self.old_path = old_path
        self.new_path = new_path
        self.message = message
        super().__init__(f"重命名图片从 {old_path} 到 {new_path} 时出错: {message}")
