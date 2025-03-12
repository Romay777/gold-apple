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
        self.user_info = user_info or {}

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
                logger.error("Unable to get friend list")
                await message.edit_text("❌ Не удалось получить список друзей", parse_mode=ParseMode.HTML)
                return False

            items = result.get("data", {}).get("items", [])
            if not items:
                logger.warning("Friend list is empty")
                await message.edit_text("❌ Список друзей пуст", parse_mode=ParseMode.HTML)
                return False

            first_friend = self._parse_user(items[0])
            like_result = self.api.like_profile(first_friend.uid)

            if like_result and like_result.get("success"):
                logger.info(f"Successfully liked user {first_friend.username}")
                await message.edit_text(f"☑️ Успешно поставлен лайк пользователю <b>{first_friend.username}</b>",
                                        parse_mode=ParseMode.HTML)
                return True
            else:
                logger.error(f"Unable to like user {first_friend.username}")
                await message.edit_text(f"❌ Не удалось поставить лайк пользователю <b>{first_friend.username}</b>",
                                        parse_mode=ParseMode.HTML)
                return False
        finally:
            clear_user_context()


    # TODO AUTO CHECK AND BUY CHEAPEST

    async def get_user_interior_and_clothes(self, message: Message) -> list:
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            result = self.api.get_profile()
            if not result or not result.get("success"):
                logger.error("Unable to get user interior and clothes")
                await message.edit_text("❌ Не удалось получить интерьер и одежду", parse_mode=ParseMode.HTML)
                return []

            logger.info("Successfully got user interior and clothes")
            items = result.get("data", {}).get("profile", {}).get("items", [])

            return items
        except:
            logger.error("internal error on get_user_interior_and_clothes")
            await message.edit_text("❌ Внутренняя ошибка", parse_mode=ParseMode.HTML)
            return []


    async def get_all_interior_and_clothes(self, message: Message) -> list:
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            result = self.api.get_items()
            if not result or not result.get("success"):
                logger.error("Unable to get all interior and clothes")
                await message.edit_text("❌ Не удалось получить интерьер и одежду", parse_mode=ParseMode.HTML)
                return []

            logger.info("Successfully got all interior and clothes")
            items = result.get("data", {}).get("shopItems", [])

            return items
        except:
            logger.error("internal error on get_all_interior_and_clothes")
            await message.edit_text("❌ Внутренняя ошибка", parse_mode=ParseMode.HTML)
            return []


    async def find_cheapest_clothes(self, message: Message, auto_buy: bool = False) -> list:
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            user_items = await self.get_user_interior_and_clothes(message)
            all_items = await self.get_all_interior_and_clothes(message)

            clothing_titles = {"Штаны", "Прическу", "Верхнюю одежду", "Очки", "Тапочки", "Шапку", "Комплект одежды"}

            bought_item_ids = {item['id'] for item in user_items}

            available_clothes = [
                item for item in all_items
                if item['title'] in clothing_titles
                   and item['id'] not in bought_item_ids
                   and item['buy_blocked'] == False
            ]

            available_interior = [
                item for item in all_items
                if item['title'] not in clothing_titles
                   and item['id'] not in bought_item_ids
                   and item['buy_blocked'] == False
            ]

            # Поиск самого дешевого в каждой категории
            cheapest_clothes = min(available_clothes, key=lambda x: x['cost']) if available_clothes else None
            cheapest_interior = min(available_interior, key=lambda x: x['cost']) if available_interior else None

            # Возвращаем оба объекта (или None, если предметов нет)
            if auto_buy:
                if cheapest_interior:
                    await self.buy_item(message, cheapest_interior['id'])
                if cheapest_clothes:
                    await self.buy_item(message, cheapest_clothes['id'])
            else:
                return [cheapest_interior, cheapest_clothes]
        except:
            clear_user_context()
            logger.error("internal error on find_cheapest_clothes")
            await message.edit_text("<b>❌ Внутренняя ошибка</b>", parse_mode=ParseMode.HTML)
            return []

    async def buy_item(self, message: Message, item_id) -> None:
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        try:
            result = self.api.buy_item(item_id)

            if not result or not result.get("success"):
                logger.error(f"Unable to buy item {item_id}", exc_info=True)
                await message.edit_text(f"<b>❌ Не удалось купить предмет</b>]\nПричина: <b>{result.get('data').get('message')}</b>", parse_mode=ParseMode.HTML,
                                        reply_markup=get_back_profile_keyboard())
                return

            logger.info(f"Successfully bought item {item_id}")
            await message.edit_text("<b>✅ Предмет успешно куплен</b>", parse_mode=ParseMode.HTML,
                                    reply_markup=get_back_profile_keyboard())
        except:
            clear_user_context()
            logger.error(f"internal error on buy_item() with id {item_id}", exc_info=True)