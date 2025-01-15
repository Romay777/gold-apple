from src.core.api.client import UserAPI
from src.core.models.user import User


class UserManager:
    def __init__(self, api: UserAPI):
        self.api = api

    def _parse_user(self, user_data: dict) -> User:
        return User(
            uid=user_data.get("uid"),
            username=user_data.get("username")
        )

    def like_first_friend(self) -> bool:
        """Ставит лайк первому другу из списка избранных"""
        result = self.api.get_favorites()
        if not result or not result.get("success"):
            print("\033[91mНе удалось получить список друзей\033[0m")
            return False

        items = result.get("data", {}).get("items", [])
        if not items:
            print("\033[93mСписок друзей пуст\033[0m")
            return False

        first_friend = self._parse_user(items[0])
        like_result = self.api.like_profile(first_friend.uid)

        if like_result and like_result.get("success"):
            print(f"\n\033[92mУспешно поставлен лайк пользователю {first_friend.username}\033[0m")
            return True
        else:
            print(f"\n\033[91mНе удалось поставить лайк пользователю {first_friend.username}\033[0m")
            return False