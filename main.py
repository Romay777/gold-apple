import asyncio
import random

from src.config.constants import BASE_URL, AUTH_PARAMS, HEADERS
from src.core.api.client import QuestAPI, GameAPI, UserAPI
from src.core.services.beauty_manager import BeautyManager
from src.core.services.game_manager import GameManager
from src.core.services.quest_manager import QuestManager
from src.core.services.user_manager import UserManager


def main(user_token: str = None):
    req_headers = HEADERS
    req_headers["Authorization"] = f"Bearer {user_token}"

    # # Вывод Данных аккаунта в консоль
    # api = GameAPI(BASE_URL, AUTH_PARAMS, req_headers)
    # beauty_manager = BeautyManager(api)
    # beauty_manager.print_profile_normalized()
    #
    # asyncio.sleep(random.randint(2, 4))
    #
    # # Сыграть в мини игры
    # game_manager = GameManager(api)
    # game_manager.auto_play_games()
    #
    # asyncio.sleep(random.randint(2, 4))
    #
    # # Выполнение бьюти процедур
    # beauty_manager.perform_procedures()
    #
    # asyncio.sleep(random.randint(2, 4))
    #
    # # Поставить реакцию на аккаунт друга
    # api = UserAPI(BASE_URL, AUTH_PARAMS, req_headers)
    # users_manager = UserManager(api)
    # users_manager.like_first_friend()
    #
    # asyncio.sleep(random.randint(2, 4))
    #
    # # Получение квестов и вывод их в консоль
    # api = QuestAPI(BASE_URL, AUTH_PARAMS, req_headers)
    # quest_manager = QuestManager(api)
    # quest_manager.print_daily_quests_status()
    #
    # asyncio.sleep(random.randint(2, 4))
    #
    # # Сбор наград за выполненные ежедневные квесты
    # quest_manager.collect_rewards_for_completed_quests()

async def request_profile_data(user_token: str = None):
    req_headers = HEADERS
    req_headers["Authorization"] = f"Bearer {user_token}"

    # Вывод Данных аккаунта в консоль
    api = GameAPI(BASE_URL, AUTH_PARAMS, req_headers)
    beauty_manager = BeautyManager(api)
    return await beauty_manager.get_profile()


