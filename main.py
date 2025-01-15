from src.config.constants import BASE_URL, AUTH_PARAMS, HEADERS
from src.core.api.client import QuestAPI, GameAPI, UserAPI
from src.core.services.beauty_manager import BeautyManager
from src.core.services.game_manager import GameManager
from src.core.services.quest_manager import QuestManager
from src.core.services.user_manager import UserManager


def main():

    # Данные аккаунта
    api = GameAPI(BASE_URL, AUTH_PARAMS, HEADERS)
    beauty_manager = BeautyManager(api)
    beauty_manager.print_profile_normalized()

    # Сыграть в мини игры
    game_manager = GameManager(api)
    game_manager.auto_play_games()

    # Выполнение бьюти процедур
    beauty_manager.perform_procedures()

    # Поставить реакцию на аккаунт друга
    api = UserAPI(BASE_URL, AUTH_PARAMS, HEADERS)
    users_manager = UserManager(api)
    users_manager.like_first_friend()

    # Получение квестов
    api = QuestAPI(BASE_URL, AUTH_PARAMS, HEADERS)
    quest_manager = QuestManager(api)
    quest_manager.print_daily_quests_status()

    # Сбор наград за выполненные ежедневные квесты
    quest_manager.collect_rewards_for_completed_quests()




if __name__ == "__main__":
    main()