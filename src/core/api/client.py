import random
from typing import Optional
import requests
from src.config.constants import AUTH_PARAMS
from src.core.api.endpoints import GameEndpoints


class BaseAPI:
    def __init__(self, base_url: str, auth_params: dict, headers: dict):
        self.base_url = base_url
        self.auth_params = auth_params
        self.headers = headers

    def _make_request(self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None) -> Optional[dict]:
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params or self.auth_params,
                json=data
            )

            if response.status_code == 400:
                error_data = response.json()
                print(f"API Error: {error_data.get('message', 'Unknown error')}")
                return None

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Server response: {e.response.text}")
            return response.json()


class QuestAPI(BaseAPI):
    def get_quests(self) -> Optional[dict]:
        return self._make_request(GameEndpoints.QUESTS)

    def collect_quest_reward(self, quest_id: str) -> Optional[dict]:
        params = {**self.auth_params, "id": quest_id}
        return self._make_request(GameEndpoints.COLLECT_QUEST, method="POST", params=params)

    def complete_quest(self, quest_id: str) -> Optional[dict]:
        """Будущий метод для выполнения квеста"""
        return self._make_request(f"{GameEndpoints.QUESTS}/{quest_id}/complete", method="POST")


class GameAPI(BaseAPI):
    def list_beauty_procedure(self) -> Optional[dict]:
        return self._make_request(GameEndpoints.BEAUTY_PROCEDURE_LIST, method="POST", params=AUTH_PARAMS)

    def perform_beauty_procedure(self, procedure_id: int) -> Optional[dict]:
        """
        Выполняет бьюти процедуру.
        Args:
            procedure_id: int - ID процедуры
        Returns:
            Optional[dict] - ответ от сервера
        """
        params = {**self.auth_params}
        data = {"id": procedure_id}
        return self._make_request(GameEndpoints.BEAUTY_PROCEDURE, method="POST", params=params, data=data)

    def end_beauty_procedure(self, procedure_id: int, c_count: int) -> Optional[dict]:
        params = {**self.auth_params}
        data = {"id": procedure_id, "correct_count": c_count}
        return self._make_request(GameEndpoints.BEAUTY_PROCEDURE_END, method="POST", params=params, data=data)

    def get_profile(self) -> Optional[dict]:
        """
        Получает профиль игрока.
        Returns:
            Optional[dict] - ответ от сервера
        """
        return self._make_request(GameEndpoints.PROFILE, method="POST", params=AUTH_PARAMS)

    def get_user_rating(self) -> Optional[dict]:
        """
        Получает рейтинг игрока.
        Returns:
            Optional[dict] - ответ от сервера
        """
        return self._make_request(GameEndpoints.USER_RATING, method="POST", params=AUTH_PARAMS)

    def get_games_list(self) -> Optional[dict]:
        """
        Получает список доступных игр.
        Returns:
            Optional[dict] - ответ от сервера
        """
        return self._make_request(GameEndpoints.GAME_LIST)

    def start_game(self, game_type: str) -> Optional[dict]:
        """
        Начинает игру.
        Args:
            game_type: str - тип игры
        Returns:
            Optional[dict] - ответ от сервера
        """
        data = {"type": game_type}
        return self._make_request(GameEndpoints.GAME_START, method="POST", data=data)

    def open_standard_box(self):
        """Открывает обычный бокс за 300 монет"""
        data = {"id": 2}
        return self._make_request(GameEndpoints.OPEN_BOX, method="POST", data=data)

    def get_limit(self):
        """Сколько еще можно открыть боксов сегодня"""
        return self._make_request(GameEndpoints.OPEN_BOX_LIST, method="GET")

    def _end_game(self, score: int, money: int = 0, additional_data: dict = None) -> Optional[dict]:
        """
        Базовый метод для завершения игры.
        Args:
            score: int - набранные очки
            additional_data: dict - дополнительные данные для конкретной игры
        Returns:
            Optional[dict] - ответ от сервера
        """
        data = {
            "is_win": 1,
            "score": score,
            "money": money
        }

        if additional_data:
            data.update(additional_data)

        return self._make_request(GameEndpoints.GAME_END, method="POST", data=data)

    def end_jumper_game(self, score: int, money: int) -> Optional[dict]:
        # return self._end_game(score, money)
        data = {
            "is_win": 1,
            "score": score,
            "money": money
        }

        return self._make_request(GameEndpoints.GAME_END, method="POST", data=data)

    def end_match3_game(self, score: int) -> Optional[dict]:
        additional_data = {
            "ram": 2,
            "cross": 2,
            "color": 2
        }
        return self._end_game(score, additional_data)

    def end_memories_game(self, score: int) -> Optional[dict]:
        return self._end_game(score)

    def end_runner_game(self, score: int):
        return self._end_game(score)


class UserAPI(BaseAPI):
    def get_favorites(self, page: int = 1, per_page: int = 5) -> Optional[dict]:
        params = {
            **self.auth_params,
            "page": page,
            "per-page": per_page
        }
        return self._make_request(GameEndpoints.FAVORITES, params=params)

    def like_profile(self, uid: str, like_type: int = random.choice([1, 2, 3, 4])) -> Optional[dict]:
        data = {
            "uid": uid,
            "type": like_type
        }
        return self._make_request(GameEndpoints.LIKE, method="POST", data=data)