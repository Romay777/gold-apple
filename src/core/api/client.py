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
            return None


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
    def perform_beauty_procedure(self, procedure_id: int) -> Optional[dict]:
        params = {**self.auth_params, "id": procedure_id}
        return self._make_request(GameEndpoints.BEAUTY_PROCEDURE, method="POST", params=params)

    def get_profile(self) -> Optional[dict]:
        return self._make_request(GameEndpoints.PROFILE, method="POST", params=AUTH_PARAMS)
