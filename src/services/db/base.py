"""
データベース活用の基底クラス
"""
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4

from services.db.models import Chat, Schedule

class Base(ABC):

    @abstractmethod
    def get_schedules(self, date: datetime) -> list[Schedule]|None:
        """指定日時の予定データ取得する（なければ None を返す）

        Args:
            date (datetime): 日時.

        Returns:
            list[Schedule]|None: 予定データ or None.
        """
        pass

    @abstractmethod
    def get_chats(self, session_id: uuid4) -> list[Chat]|None:
        """指定セッションのチャット履歴データを取得する（なければ None を返す）

        Args:
            session_id (uuid4): セッションID

        Returns:
            list[Chat]|None: チャット履歴 or None
        """
        pass

