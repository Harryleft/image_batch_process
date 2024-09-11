"""图片处理器模块。

本模块提供了一个ImageProcessor类,用于处理图片文件,包括收集、去重和重命名等功能。

Classes:
    ImageProcessor: 图片处理器类。
"""

import os
import re
import shutil
import hashlib
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from PIL import Image
import piexif

from exception_handler import (
    ImageRenameError,
    ImageCopyError,
    HashCalculationError,
    FileAccessError,
)


class ImageProcessor:
    """图片处理器类。

    该类负责处理图片文件,包括收集、去重和重命名等功能。

    Attributes:
        source_folders (List[str]): 源文件夹列表。
        target_folder (str): 目标文件夹路径。
        observers (List): 观察者列表。
    """

    def __init__(self):
        """初始化ImageProcessor类。"""
        self.source_folders: List[str] = []
        self.target_folder: str = ""
        self.observers: List = []

    def add_observer(self, observer: object) -> None:
        """添加观察者。

        Args:
            observer: 观察者对象。
        """
        self.observers.append(observer)

    def remove_observer(self, observer: object) -> None:
        """删除观察者。

        Args:
            observer: 观察者对象。
        """
        self.observers.remove(observer)

    def notify_observers(self, event: str, data: Optional[object] = None) -> None:
        """通知所有观察者。

        Args:
            event: 事件名称。
            data: 事件相关数据(可选)。
        """
        for observer in self.observers:
            observer.update(event, data)

    def add_folder(self, folder: str) -> None:
        """添加源文件夹。

        Args:
            folder: 要添加的文件夹路径。
        """
        if folder and folder not in self.source_folders:
            self.source_folders.append(folder)
            self.notify_observers("source_folders_updated", self.source_folders)

    def remove_folder(self, index: int) -> None:
        """删除源文件夹。

        Args:
            index: 要删除的文件夹索引。
        """
        if 0 <= index < len(self.source_folders):
            del self.source_folders[index]
            self.notify_observers("source_folders_updated", self.source_folders)

    def select_target_folder(self, folder: str) -> None:
        """选择目标文件夹。

        Args:
            folder: 目标文件夹路径。
        """
        self.target_folder = folder
        self.notify_observers("target_folder_updated", self.target_folder)

    def process_images(self) -> None:
        """处理图片。

        收集、去重和重命名图片。

        Raises:
            ValueError: 如果没有设置源文件夹或目标文件夹。
        """
        if not self.source_folders:
            raise ValueError("请至少添加一个源文件夹")
        if not self.target_folder:
            raise ValueError("请选择目标文件夹")

        collected_images = self._collect_and_deduplicate_images()
        self._rename_images(collected_images)
        self.notify_observers("processing_completed")

    def _get_image_date(self, file_path: str) -> datetime:
        """获取图片日期。

        首先尝试从EXIF数据获取日期,如果失败则从文件名或修改时间获取。

        Args:
            file_path: 图片文件路径。

        Returns:
            图片的日期时间。
        """
        # 尝试从EXIF数据获取日期
        try:
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    exif = piexif.load(img.info["exif"])
                    date_time = exif["0th"][piexif.ImageIFD.DateTime].decode("utf-8")
                    return datetime.strptime(date_time, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass

        # 尝试从文件名获取日期
        file_name = os.path.basename(file_path)
        date_pattern = (
            r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})"
        )
        match = re.search(date_pattern, file_name)
        if match:
            try:
                date_parts = map(int, match.groups())
                return datetime(*date_parts)
            except ValueError:
                pass

        # 如果上述方法都失败,则使用文件修改时间
        return datetime.fromtimestamp(os.path.getmtime(file_path))

    def _get_file_hash(self, file_path: str) -> str:
        """获取文件的MD5哈希值。

        Args:
            file_path: 文件路径。

        Returns:
            文件的MD5哈希值。
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            raise HashCalculationError(file_path, str(e))

    def _collect_and_deduplicate_images(self) -> List[str]:
        """收集并去重图片。

        Returns:
            去重后的图片路径列表。
        """
        collected_images: List[str] = []
        hash_dict: Dict[str, str] = {}

        for folder in self.source_folders:
            self._process_folder(folder, collected_images, hash_dict)

        self.notify_observers("collection_completed", len(collected_images))
        return collected_images

    def _process_folder(
        self, folder: str, collected_images: List[str], hash_dict: Dict[str, str]
    ) -> None:
        """处理单个文件夹中的图片。

        Args:
            folder: 要处理的文件夹路径。
            collected_images: 收集的图片列表。
            hash_dict: 用于去重的哈希字典。
        """
        for root, _, files in os.walk(folder):
            for file in files:
                if self._is_image_file(file):
                    self._process_image_file(root, file, collected_images, hash_dict)

    def _is_image_file(self, file: str) -> bool:
        """检查文件是否为图片。

        Args:
            file: 文件名。

        Returns:
            如果文件是图片则返回True，否则返回False。
        """
        image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
        return file.lower().endswith(image_extensions)

    def _process_image_file(
        self,
        root: str,
        file: str,
        collected_images: List[str],
        hash_dict: Dict[str, str],
    ) -> None:
        """处理单个图片文件。

        Args:
            root: 文件所在的根目录。
            file: 文件名。
            collected_images: 收集的图片列表。
            hash_dict: 用于去重的哈希字典。
        """
        source_path = os.path.join(root, file)
        try:
            file_hash = self._get_file_hash(source_path)
        except HashCalculationError as e:
            print(f"处理文件 {file} 的哈希出错: {e}")
            return
        except FileAccessError as e:
            print(f"处理文件 {file} 的文件访问出错: {e}")
            return

        if file_hash not in hash_dict:
            self._copy_unique_image(
                source_path, file, collected_images, hash_dict, file_hash
            )

    def _get_unique_target_path(self, file: str) -> str:
        """获取唯一的目标文件路径。

        如果目标路径已存在,则在文件名后添加计数器。

        Args:
            file: 原始文件名。

        Returns:
            唯一的目标文件路径。
        """
        target_path = os.path.join(self.target_folder, file)
        counter = 1
        while os.path.exists(target_path):
            name, ext = os.path.splitext(file)
            target_path = os.path.join(self.target_folder, f"{name}_{counter}{ext}")
            counter += 1
        return target_path

    def _rename_images(self, image_files: List[str]) -> None:
        """重命名图片。

        Args:
            image_files: 要重命名的图片文件路径列表。
        """
        image_dates: List[Tuple[str, datetime]] = [
            (f, self._get_image_date(f)) for f in image_files
        ]
        image_dates.sort(key=lambda x: x[1])

        for index, (old_path, date) in enumerate(image_dates, start=1):
            old_name = os.path.basename(old_path)
            time_str = self._get_time_string(old_name, date)
            new_name = f"{index:04d}_{time_str}{os.path.splitext(old_name)[1]}"
            new_path = os.path.join(self.target_folder, new_name)

            try:
                os.rename(old_path, new_path)
            except Exception as e:
                raise ImageRenameError(old_path, new_path, str(e))

        self.notify_observers("renaming_completed", len(image_files))

    def _get_time_string(self, file_name: str, date: datetime) -> str:
        """获取时间字符串。

        首先尝试从文件名中提取时间信息,如果失败则使用给定的日期。

        Args:
            file_name: 文件名。
            date: 日期时间对象。

        Returns:
            格式化的时间字符串。
        """
        time_info = re.search(r"\d{8}_\d{6}", file_name)
        return time_info.group(0) if time_info else date.strftime("%Y%m%d_%H%M%S")

    def _copy_unique_image(
        self,
        source_path: str,
        file: str,
        collected_images: List[str],
        hash_dict: Dict[str, str],
        file_hash: str,
    ) -> None:
        """复制唯一的图片到目标文件夹，并添加前缀。

        Args:
            source_path: 源文件路径。
            file: 文件名。
            collected_images: 收集的图片列表。
            hash_dict: 用于去重的哈希字典。
            file_hash: 文件的哈希值。
        """
        target_path = self._get_unique_target_path(file)
        if self._is_random_name(file):
            target_path = self.add_prefix_to_image(source_path, self.target_folder)

        try:
            shutil.copy2(source_path, target_path)
            collected_images.append(target_path)
            hash_dict[file_hash] = target_path
        except ImageCopyError as e:
            raise ImageCopyError(source_path, target_path, str(e))

    def add_prefix_to_image(
        self, file_path: str, target_folder: str, prefix: str = "疑似网图"
    ) -> str:
        """为文件名为随机字母和数字组合的图片添加前缀。

        Args:
            file_path: 图片文件路径。
            target_folder: 目标文件夹路径。
            prefix: 要添加的前缀。

        Returns:
            新的文件路径。
        """
        file_name = os.path.basename(file_path)
        new_name = f"{prefix}_{file_name}"
        new_path = os.path.join(target_folder, new_name)
        os.rename(file_path, new_path)
        return new_path

    def _is_random_name(self, file_name: str) -> bool:
        """检查文件名是否为随机字母和数字组合。

        Args:
            file_name: 文件名。

        Returns:
            如果文件名是随机字母和数字组合则返回True，否则返回False。
        """
        return re.match(r"^[a-zA-Z0-9]+$", os.path.splitext(file_name)[0]) is not None
