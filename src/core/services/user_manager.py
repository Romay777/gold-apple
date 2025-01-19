from typing import Optional

from aiogram.enums import ParseMode
from aiogram.types import Message

from src.bot.keyboards import get_start_elf_keyboard, get_back_profile_keyboard
from src.core.api.client import UserAPI
from src.core.models.user import User
from src.utils.logger import logger, clear_user_context, set_user_context


class UserManager:
    def __init__(self, api: UserAPI, user_info: Optional[dict] = None):
        self.api = api
        self.user_info = {}

    def _parse_user(self, user_data: dict) -> User:
        return User(
            uid=user_data.get("uid"),
            username=user_data.get("username")
        )

    async def like_first_friend(self, message: Message) -> bool:
        """Ставит лайк первому другу из списка избранных"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            result = self.api.get_favorites()
            if not result or not result.get("success"):
                logger.error("Не удалось получить список друзей")
                await message.edit_text("❌ Не удалось получить список друзей", parse_mode=ParseMode.HTML)
                return False

            items = result.get("data", {}).get("items", [])
            if not items:
                logger.warning("Список друзей пуст")
                await message.edit_text("❌ Список друзей пуст", parse_mode=ParseMode.HTML)
                return False

            first_friend = self._parse_user(items[0])
            like_result = self.api.like_profile(first_friend.uid)

            if like_result and like_result.get("success"):
                logger.info(f"Успешно поставлен лайк пользователю {first_friend.username}")
                await message.edit_text(f"☑️ Успешно поставлен лайк пользователю <b>{first_friend.username}</b>",
                                        parse_mode=ParseMode.HTML)
                return True
            else:
                logger.error(f"Не удалось поставить лайк пользователю {first_friend.username}")
                await message.edit_text(f"❌ Не удалось поставить лайк пользователю <b>{first_friend.username}</b>",
                                        parse_mode=ParseMode.HTML)
                return False
        finally:
            clear_user_context()