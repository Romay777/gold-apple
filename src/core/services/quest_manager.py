from typing import Dict, List

from src.core.api.client import QuestAPI
from src.core.models.enums import QuestStatus
from src.core.models.quest import Quest
from src.utils.encodings import fix_encoding


class QuestManager:
    def __init__(self, api: QuestAPI):
        self.api = api

    @staticmethod
    def _parse_quest(quest_data: dict) -> Quest:
        return Quest(
            id=quest_data.get("id", ""),
            text=fix_encoding(quest_data.get("text", "")),
            description=fix_encoding(quest_data.get("description", "")),
            is_complete=quest_data.get("isComplete", False),
            is_daily=quest_data.get("isDaily", False),
            is_collected=quest_data.get("isCollected", False),
            trigger_count=quest_data.get("triggerCount", ""),
            progress=quest_data.get("progress")
        )

    def get_daily_quests(self) -> Dict[QuestStatus, List[Quest]]:
        """Получает дневные квесты"""
        result = self.api.get_quests()
        if not result or not result.get("success"):
            return {status: [] for status in QuestStatus}

        quests = result.get("data", {}).get("quests", [])
        daily_quests: Dict[QuestStatus, List[Quest]] = {status: [] for status in QuestStatus}

        for quest_data in quests:
            if quest_data.get("isDaily"):
                quest = QuestManager._parse_quest(quest_data)
                daily_quests[quest.status].append(quest)

        return daily_quests

    def print_daily_quests_status(self):
        """Выводит статус дневных квестов"""
        daily_quests = self.get_daily_quests()

        print("\033[38;5;223m\n=== Статус Дневных Задач ===\033[0m", end="")
        for status, quests in daily_quests.items():
            print(f"\033[97m\n{status.value.upper()} ({len(quests)} задач(-a):\033[0m")

            if not quests:
                print("🎉 Все задачи выполнены")
                continue
            for quest in quests:
                print(f"- {quest.text}")
                if quest.progress:
                    print(f"    · Прогресс: {quest.progress}/{quest.trigger_count}")

    def collect_rewards_for_completed_quests(self):
        """Собирает награды за выполненные квесты"""
        print("\033[96m\n=== Сбор наград за выполненные квесты ===\033[0m")

        quests = self.get_daily_quests()
        completed_quests = quests.get(QuestStatus.COMPLETED_UNCOLLECTED, [])

        if not completed_quests:
            print("    🎁 Все награды получены")
            return

        for quest in completed_quests:
            result = self.api.collect_quest_reward(quest.id)
            if result and result.get("success"):
                print(f"    Награда за квест '{quest.text}' успешно получена")
            else:
                print(f"    Не удалось получить награду за квест '{quest.text}'")
