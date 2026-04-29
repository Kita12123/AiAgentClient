"""
AI活用の基底クラス
"""

from abc import ABC, abstractmethod
from PIL import Image

class Base(ABC):

    @abstractmethod
    def reqMsg(self, msg: str) -> str:
        """Request message.

        Args:
            msg (str): message.

        Returns:
            str: response message.
        """
        pass

    @abstractmethod
    def reqFile(self, msg: str, file_path: str) -> str:
        """Request message and attachment file.

        Args:
            msg (str): message.
            file_path(str): attachment file path.

        Returns:
            str: response message.
        """
        pass

    @abstractmethod
    def reqImg(self, msg: str, img: Image.ImageFile.ImageFile) -> str:
        """Request message and image.

        Args:
            msg (str): message.
            img(ImageFile): image data.

        Returns:
            str: response message.
        """
        pass

