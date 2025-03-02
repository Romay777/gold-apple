import asyncio
import random

from aiogram.enums import ParseMode
from aiogram.types import Message
from typing import Optional

from src.bot.keyboards import get_back_profile_keyboard
from src.core.api.client import GameAPI
from src.core.models.beauty_procedure import BeautyProcedure, Profile, UserRating
from src.utils.logger import logger, set_user_context, clear_user_context


class BeautyManager:
    def __init__(self, api: GameAPI, user_info: Optional[dict] = None):
        self.api = api
        self.user_info = user_info or {}

    def _parse_profile(self, data: dict) -> Optional[Profile]:
        if not data or not data.get("success"):
            return None

        profile_data = data.get("data", {}).get("profile", {})
        return Profile(
            attempts=profile_data.get("attempts", 0),
            score=profile_data.get("score", 0),
            money=profile_data.get("money", 0),
            level=profile_data.get("level", 1),
            attempts_cooldown=profile_data.get("attemptsCooldown", 0),
            attempts_restored_at=profile_data.get("attemptsRestoredAt", 0),
            # --- OUTDATED ---
            # beauty_procedures=[
            #     BeautyProcedure(
            #         id=proc.get("id"),
            #         title=proc.get("title"),
            #         action=proc.get("action"),
            #         cost=proc.get("cost"),
            #         score=proc.get("score"),
            #         multiplier=proc.get("multiplier"),
            #         multiplier_user_money=proc.get("multiplierUserMoney"),
            #         is_new=proc.get("isNew"),
            #         description=proc.get("description")
            #     )
            #     for proc in profile_data.get("beautyProcedures", [])
            # ],
            beauty_procedures=[],
            username=profile_data.get("username"),
        )

    def _parse_user_rating(self, data: dict) -> Optional[UserRating]:
        if not data or not data.get("success"):
            return None

        user_rating_data = data.get("data", {}).get("user", {})
        return UserRating(
            score=user_rating_data.get("score", 0),
            position=user_rating_data.get("position", 0)
        )

    def _parse_beauty_id(self, data: dict) -> Optional[int]:
        if not data or not data.get("success"):
            return None

        items = data.get("data", {}).get("list", [])
        return items[0].get("id") if items else None

    async def get_profile(self) -> Optional[Profile]:
        """Получает профиль игрока с информацией о бьюти процедурах"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        logger.info("Getting profile")
        result = self.api.get_profile()
        return self._parse_profile(result)

    async def get_user_rating(self) -> Optional[UserRating]:
        """Получает рейтинг игрока"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        logger.info("Getting user rating")
        result = self.api.get_user_rating()
        return self._parse_user_rating(result)

    async def print_profile_normalized(self) -> None:
        profile = await self.get_profile()
        if not profile:
            logger.error("Error getting profile")
            return

        print(
            "\033[95m\n=== Профиль игрока ===\033[0m"
            f"\n👤 Имя: {profile.username}"
            f"\n🌟 Рейтинг: {profile.score}"
            f"\n⚡ Энергия: {profile.attempts}"
            f"\n🪙 Баланс: {profile.money} "
            "\033[95m\n=======================\033[0m"
        )

    async def perform_procedures(self, message: Message) -> None:
        """Выполняет каждую бьюти процедуру по одному разу с задержкой"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))

        try:
            logger.debug("Begin perform_procedures")
            profile = await self.get_profile()
            if not profile:
                logger.error("Cannot get profile")
                await message.edit_text("Не удалось получить профиль", parse_mode=ParseMode.HTML)
                return

            if profile.money < 250:
                logger.warn("Not enough money")
                await message.edit_text("🚫 <b>Недостаточно денег</b>", parse_mode=ParseMode.HTML)
                return

            # TODO get id by
            b_list =  self.api.list_beauty_procedure()
            if list:
                b_id = self._parse_beauty_id(b_list)
            else:
                logger.error("Cannot get beauty id")
                await message.edit_text("Не удалось получить id процедуры", parse_mode=ParseMode.HTML)
                return

            result = self.api.perform_beauty_procedure(b_id)
            if result and result.get("success"):
                logger.info(f"Successfully started procedures")
                await message.edit_text(f"☑️ <b>Успешно запущены процедуры!</b>",
                                        parse_mode=ParseMode.HTML)
            else:
                reason = result.get("data", {}).get("name", "Неизвестная причина")
                if reason == "You have reached the day limit of this routine":
                    logger.debug(f"Cannot start procedures", "Reason: You have reached the day limit of this routine", )
                    await message.edit_text(f"⚠️ <b>Не удалось начать процедуры</b>\n"
                                            f"Причина: <b>Процедуры уже выполнены</b>\f",
                                            parse_mode=ParseMode.HTML)
                else:
                    logger.warning(f"Cannot start procedures", "Reason: ", reason)
                    await message.edit_text(f"⚠️ <b>Не удалось начать процедуры</b>\n"
                                            f"Причина: <b>{reason}</b>\f",
                                            parse_mode=ParseMode.HTML)
                return

            await asyncio.sleep(random.randint(2, 4))
            result = self.api.end_beauty_procedure(b_id, 4)
            if result and result.get("success"):
                logger.info(f"Successfully ended procedures")
                await message.edit_text(f"✨ Процедуры завершены!",
                                        parse_mode=ParseMode.HTML)
            else:
                logger.error(f"Cannot end procedures")
                await message.edit_text(f"⚠️ <b>Не удалось завершить процедуры</b>",
                                        parse_mode=ParseMode.HTML)
                return

        finally:
            if self.user_info:
                clear_user_context()
