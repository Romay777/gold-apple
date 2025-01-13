from dataclasses import dataclass
from typing import Dict, Optional
from src.core.models.enums import QuestStatus

@dataclass
class Quest:
    id: str
    text: str
    description: str
    is_complete: bool
    is_daily: bool
    is_collected: bool
    trigger_count: str
    progress: Optional[Dict] = None

    @property
    def status(self) -> QuestStatus:
        if self.is_complete:
            return QuestStatus.COMPLETED_COLLECTED if self.is_collected else QuestStatus.COMPLETED_UNCOLLECTED
        return QuestStatus.IN_PROGRESS