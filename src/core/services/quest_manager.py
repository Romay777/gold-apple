import html
from typing import Dict, List, Optional

from src.core.api.client import QuestAPI
from src.core.models.enums import QuestStatus
from src.core.models.quest import Quest
from src.utils.encodings import fix_encoding
from src.utils.logger import logger, set_user_context, clear_user_context


class QuestManager:
    def __init__(self, api: QuestAPI, user_info: Optional[dict] = None):
        self.api = api
        self.user_info = user_info or {}

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

    def get_all_quests(self) -> Dict[QuestStatus, List[Quest]]:
        """Получает все квесты"""
        result = self.api.get_quests()
        if not result or not result.get("success"):
            return {status: [] for status in QuestStatus}

        quests = result.get("data", {}).get("quests", [])
        all_quests: Dict[QuestStatus, List[Quest]] = {status: [] for status in QuestStatus}

        for quest_data in quests:
            quest = QuestManager._parse_quest(quest_data)
            all_quests[quest.status].append(quest)

        return all_quests

    def format_daily_quests_status(self) -> str:
        """Форматирует статус дневных квестов для вывода в Telegram"""
        # ВЫВОД ВСЕХ ТИПОВ ЗАДАЧ
        # daily_quests = self.get_daily_quests()
        #
        # messages = []
        #
        # for status, quests in daily_quests.items():
        #     messages.append(f"\n{status.value.upper()} ({len(quests)} задач):")
        #
        #     if not quests:
        #         messages.append("🎉 Все награды получены")
        #         continue
        #
        #     for quest in quests:
        #         messages.append(f"— {quest.text}")
        #         if quest.progress and status != QuestStatus.COMPLETED_COLLECTED:
        #             messages.append(f"    · Прогресс: {quest.progress}/{quest.trigger_count}")
        #
        # return "\n".join(messages)

        # ВЫВОД ТОЛЬКО ЗАВЕРШЕННЫХ И В ПРОЦЕССЕ
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))

        try:
            logger.info("Daily quests status formatting started")
            daily_quests = self.get_daily_quests()

            messages = []

            # First handle completed quests (both collected and uncollected)
            completed_quests = []
            completed_quests.extend(daily_quests[QuestStatus.COMPLETED_COLLECTED])
            completed_quests.extend(daily_quests[QuestStatus.COMPLETED_UNCOLLECTED])

            if completed_quests:
                messages.append(f"\nВЫПОЛНЕНО ({len(completed_quests)} задач):")
                for quest in completed_quests:
                    messages.append(f"— {clean_text(quest.text)}")

            # Then handle in progress quests
            in_progress_quests = daily_quests[QuestStatus.IN_PROGRESS]
            if in_progress_quests:
                messages.append(f"\nВ ПРОЦЕССЕ ({len(in_progress_quests)} задач):")
                for quest in in_progress_quests:
                    messages.append(f"— {clean_text(quest.text)}")
                    if quest.progress:
                        messages.append(f"    · Прогресс: {quest.progress}/{quest.trigger_count}")

            return "\n".join(messages)
        finally:
            if self.user_info:
                clear_user_context()

    def format_rewards_collection(self) -> str:
        """Форматирует результат сбора наград для вывода в Telegram"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            logger.info("Collecting rewards")
            messages = []

            quests = self.get_all_quests()

            completed_quests = quests.get(QuestStatus.COMPLETED_UNCOLLECTED, [])

            if not completed_quests:
                logger.info("All rewards collected")
                messages.append("🎁 <b>Все награды получены</b>")
            else:
                for quest in completed_quests:
                    result = self.api.collect_quest_reward(quest.id)
                    if result and result.get("success"):
                        logger.info(f"Reward collected for quest '{quest.text}'")
                        messages.append(f"✅ Награда за квест <b>'{quest.text}'</b> успешно получена")
                    else:
                        logger.error(f"Unable to collect reward for quest '{quest.text}'")
                        messages.append(f"❌ Не удалось получить награду за квест '{quest.text}'")
            result = "\n".join(messages)
        finally:
            if self.user_info:
                clear_user_context()
        return result

def clean_text(text):
    return html.unescape(text)