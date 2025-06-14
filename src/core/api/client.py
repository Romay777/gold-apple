import random
from typing import Optional, Dict, Any, Union
import requests
from src.config.constants import AUTH_PARAMS
from src.core.api.endpoints import GameEndpoints


class BaseAPI:
    """Base API class handling request management and error handling."""

    def __init__(self, base_url: str, auth_params: dict, headers: dict):
        self.base_url = base_url
        self.auth_params = auth_params
        self.headers = headers
        self.session = requests.Session()  # Use session for connection pooling

        # Add headers to session
        self.session.headers.update(headers)

    def _make_request(self,
                      endpoint: str,
                      method: str = "GET",
                      params: dict = None,
                      data: dict = None,
                      timeout: int = 30) -> Optional[dict]:
        """
        Make an API request with error handling.

        Args:
            endpoint: API endpoint
            method: HTTP method (GET, POST)
            params: URL parameters
            data: JSON body data
            timeout: Request timeout in seconds

        Returns:
            API response as dictionary or None on error
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            request_params = params or self.auth_params

            print(f"Sending request to {url} with data: {data}")  # Для отладки

            response = self.session.request(
                method=method,
                url=url,
                params=request_params,
                json=data,
                timeout=timeout
            )

            print(f'Sending req with:\nURL: {url}\nMethod: {method}\nParams: {request_params}\nJSON data: {data}\nHeaders: {self.session.headers}')

            # Handle common API error responses
            if response.status_code == 400:
                error_data = response.json()
                error_message = error_data.get('message', 'Unknown error')
                print(f"API Error: {error_message}")
                return None
            if response.status_code == 403:
                print(f"API Error: 403 FORBIDDEN")
                return None

            print(f"GOT CODE: {response.status_code}")

            # Handle other error status codes
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                try:
                    # Try to parse and return any available JSON response
                    print(f"JSON PARSE ERR 1: {e}")
                    return e.response.json()
                except ValueError:
                    print(f"JSON PARSE ERR 2: {e}")
                    return None
            print(f"Request exception error: {e}")
            print(f"\nRESPONSE TEXT: {e.response.text}")
            print(f"\nRESPONSE: {e.response}")
            return None
        except ValueError as e:
            print(f"JSON parsing error: {e}")
            return None

    def get_profile(self) -> Optional[dict]:
        """Get player profile information."""
        return self._make_request(GameEndpoints.PROFILE, method="POST", params=self.auth_params)


class QuestAPI(BaseAPI):
    """API for quest-related endpoints."""

    def get_quests(self) -> Optional[dict]:
        """Get available quests."""
        return self._make_request(GameEndpoints.QUESTS)

    def collect_quest_reward(self, quest_id: str) -> Optional[dict]:
        """Collect reward for completed quest."""
        params = {**self.auth_params, "id": quest_id}
        return self._make_request(GameEndpoints.COLLECT_QUEST, method="POST", params=params)

    def complete_quest(self, quest_id: str) -> Optional[dict]:
        """Complete a specific quest."""
        return self._make_request(f"{GameEndpoints.QUESTS}/{quest_id}/complete", method="POST")


class GameAPI(BaseAPI):
    """API for game-related endpoints."""

    def list_beauty_procedure(self) -> Optional[dict]:
        """Get list of available beauty procedures."""
        return self._make_request(GameEndpoints.BEAUTY_PROCEDURE_LIST, method="POST", params=self.auth_params)

    def perform_beauty_procedure(self, procedure_id: int) -> Optional[dict]:
        """
        Perform a beauty procedure.

        Args:
            procedure_id: ID of the procedure

        Returns:
            Server response
        """
        data = {"id": procedure_id}
        return self._make_request(GameEndpoints.BEAUTY_PROCEDURE, method="POST", data=data)

    def end_beauty_procedure(self, procedure_id: int, c_count: int) -> Optional[dict]:
        """
        End a beauty procedure with results.

        Args:
            procedure_id: ID of the procedure
            c_count: Correct count for procedure
        """
        data = {"id": procedure_id, "correct_count": c_count}
        return self._make_request(GameEndpoints.BEAUTY_PROCEDURE_END, method="POST", data=data)

    def get_user_rating(self) -> Optional[dict]:
        """Get player rating information."""
        return self._make_request(GameEndpoints.USER_RATING, method="POST", params=self.auth_params)

    def get_games_list(self) -> Optional[dict]:
        """Get list of available games."""
        return self._make_request(GameEndpoints.GAME_LIST)

    def start_game(self, game_type: str) -> Optional[dict]:
        """
        Start a game session.

        Args:
            game_type: Type of game to start
        """
        data = {"type": game_type}
        print('Sending game start request')
        return self._make_request(GameEndpoints.GAME_START, method="POST", data=data)

    def open_standard_box(self) -> Optional[dict]:
        """Open a standard box for 300 coins."""
        data = {"id": 2}
        return self._make_request(GameEndpoints.OPEN_BOX, method="POST", data=data)

    def get_limit(self) -> Optional[dict]:
        """Get remaining box opening limit for today."""
        return self._make_request(GameEndpoints.OPEN_BOX_LIST)

    def _end_game(self, score: int, money: int = 100, additional_data: dict = None) -> Optional[dict]:
        """
        Base method for ending any game.

        Args:
            score: Player's score
            money: Money collected
            additional_data: Additional game-specific data
        """
        data = {
            "is_win": 1,
            "score": score,
            "money": money
        }

        if additional_data:
            data.update(additional_data)

        return self._make_request(GameEndpoints.GAME_END, method="POST", data=data)

    # Specific game ending methods

    def end_jumper_game(self, score: int, money: int, additional_data) -> Optional[dict]:
        """End Jumper game with score and money."""
        return self._end_game(score, money, additional_data)

    def end_runner_game(self, score: int, money: int, additional_data) -> Optional[dict]:
        """End Runner game with score and money."""
        return self._end_game(score, money, additional_data)

    def end_match3_game(self, score: int, money: int, additional_data) -> Optional[dict]:
        """End Match3 game with score and special data."""
        return self._end_game(score, money, additional_data)

    def end_memories_game(self, score: int, additional_data) -> Optional[dict]:
        """End Memories game with score."""
        return self._end_game(score, additional_data=additional_data)


class UserAPI(BaseAPI):
    """API for user-related endpoints."""

    def get_favorites(self, page: int = 1, per_page: int = 5) -> Optional[dict]:
        """Get user favorites with pagination."""
        params = {
            **self.auth_params,
            "page": page,
            "per-page": per_page
        }
        return self._make_request(GameEndpoints.FAVORITES, params=params)

    def like_profile(self, uid: str, like_type: int = None) -> Optional[dict]:
        """
        Like a user profile.

        Args:
            uid: User ID to like
            like_type: Type of like (1-4, random if not specified)
        """
        if like_type is None:
            like_type = random.choice([1, 2, 3, 4])

        data = {
            "uid": uid,
            "type": like_type
        }
        return self._make_request(GameEndpoints.LIKE, method="POST", data=data)

    def get_items(self):
        """Get list of available items."""
        return self._make_request(GameEndpoints.ITEMS_LIST)


    def buy_item(self, item_id: str):
        """Buy an item."""
        params = {
            **self.auth_params,
            "id": item_id
        }
        return self._make_request(f"{GameEndpoints.BUY_ITEM}", method="POST", params=params)