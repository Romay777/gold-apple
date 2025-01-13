from enum import Enum

class QuestStatus(Enum):
    COMPLETED_COLLECTED = "Выполнено, получена награда"
    COMPLETED_UNCOLLECTED = "Выполнено, награда не получена"
    IN_PROGRESS = "В процессе"