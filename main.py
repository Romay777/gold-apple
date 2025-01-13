from src.config.constants import BASE_URL, AUTH_PARAMS, HEADERS
from src.core.api.client import QuestAPI, GameAPI
from src.core.services.beauty_manager import BeautyManager
from src.core.services.quest_manager import QuestManager


def main():
    # Получение задач
    api = QuestAPI(BASE_URL, AUTH_PARAMS, HEADERS)
    manager = QuestManager(api)
    manager.print_daily_quests_status()

    # Выполнение бьюти процедур
    api = GameAPI(BASE_URL, AUTH_PARAMS, HEADERS)
    beauty_manager = BeautyManager(api)
    beauty_manager.perform_procedures()


if __name__ == "__main__":
    main()