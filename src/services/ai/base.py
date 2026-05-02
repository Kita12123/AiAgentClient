"""
AI活用の基底クラス
"""

from abc import ABC, abstractmethod
from PIL import Image

class Base(ABC):

    @abstractmethod
    def request_message(self, msg: str) -> str:
        """Request message.

        Args:
            msg (str): message.

        Returns:
            str: response message.
        """
        pass

    @abstractmethod
    def request_message_and_upload_file(self, msg: str, file_path: str) -> str:
        """Request message and attachment file.

        Args:
            msg (str): message.
            file_path(str): attachment file path.

        Returns:
            str: response message.
        """
        pass

    @abstractmethod
    def request_message_with_image(self, msg: str, img: Image.Image) -> str:
        """Request message and image.

        Args:
            msg (str): message.
            img(ImageFile): image data.

        Returns:
            str: response message.
        """
        pass

