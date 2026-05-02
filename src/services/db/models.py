from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class Schedule:
    """予定データ
    """
    id: UUID
    title: str
    description : str
    status_cd: int
    location: str
    start_at: datetime
    end_at: datetime
    is_all_day: bool

@dataclass
class Chat:
    """チャットデータ
    """
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime