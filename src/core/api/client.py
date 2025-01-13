from typing import Optional

import requests

from src.core.api.endpoints import GameEndpoints


class QuestAPI:
    def __init__(self, base_url: str, auth_params: dict, headers: dict):
        self.base_url = base_url
        self.auth_params = auth_params
        self.headers = headers

    def _make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> Optional[dict]:
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=self.auth_params,
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

    def get_quests(self) -> Optional[dict]:
        return self._make_request(GameEndpoints.QUESTS)

    def collect_reward(self, quest_id: str) -> Optional[dict]:
        """Будущий метод для сбора наград"""
        return self._make_request(f"{GameEndpoints.QUESTS}/{quest_id}/collect", method="POST")

    def complete_quest(self, quest_id: str) -> Optional[dict]:
        """Будущий метод для выполнения квеста"""
        return self._make_request(f"{GameEndpoints.QUESTS}/{quest_id}/complete", method="POST")


class GameAPI:
    def __init__(self, base_url: str, auth_params: dict, headers: dict):
        self.base_url = base_url
        self.auth_params = auth_params
        self.headers = headers

    def _make_request(self, endpoint: str, method: str = "GET", params: dict = None, data: dict = None) -> Optional[
        dict]:
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

    def perform_beauty_procedure(self, procedure_id: int) -> Optional[dict]:
        params = {**self.auth_params, "id": procedure_id}
        return self._make_request(GameEndpoints.BEAUTY_PROCEDURE, method="POST", params=params)

    def get_profile(self) -> Optional[dict]:
        return self._make_request(GameEndpoints.PROFILE)

