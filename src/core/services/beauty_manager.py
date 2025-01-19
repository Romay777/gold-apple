import asyncio

from aiogram.enums import ParseMode
from aiogram.types import Message
from typing import Optional

from src.bot.keyboards import get_back_profile_keyboard
from src.core.api.client import GameAPI
from src.core.models.beauty_procedure import BeautyProcedure, Profile
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
            beauty_procedures=[
                BeautyProcedure(
                    id=proc.get("id"),
                    title=proc.get("title"),
                    action=proc.get("action"),
                    cost=proc.get("cost"),
                    score=proc.get("score"),
                    multiplier=proc.get("multiplier"),
                    multiplier_user_money=proc.get("multiplierUserMoney"),
                    is_new=proc.get("isNew"),
                    description=proc.get("description")
                )
                for proc in profile_data.get("beautyProcedures", [])
            ],
            username=profile_data.get("username"),
        )

    async def get_profile(self) -> Optional[Profile]:
        """Получает профиль игрока с информацией о бьюти процедурах"""
        if self.user_info:
            set_user_context(self.user_info.get("id"), self.user_info.get("username"))
        logger.info("Получение профиля игрока")
        result = self.api.get_profile()
        return self._parse_profile(result)

    async def print_profile_normalized(self) -> None:
        profile = await self.get_profile()
        if not profile:
            print("Не удалось получить профиль")
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
            logger.debug("Выполнение бьюти-процедур")
            profile = await self.get_profile()
            if not profile:
                logger.error("Не удалось получить профиль")
                await message.edit_text("Не удалось получить профиль", parse_mode=ParseMode.HTML)
                return

            procedure_ids = [profile.beauty_procedures[-3].id, profile.beauty_procedures[-2].id,
                             profile.beauty_procedures[-1].id]

            for procedure_id in procedure_ids:
                # Находим процедуру в списке доступных
                procedure = next(
                    (p for p in profile.beauty_procedures if p.id == procedure_id),
                    None
                )

                if not procedure:
                    logger.error(f"Процедура с ID {procedure_id} не найдена")
                    await message.edit_text(f"Процедура с ID {procedure_id} не найдена", parse_mode=ParseMode.HTML)
                    continue

                if profile.can_afford_procedure(procedure.cost):
                    result = self.api.perform_beauty_procedure(procedure_id)
                    if result and result.get("success"):
                        logger.info(f"Успешно выполнена процедура: {procedure.title}")
                        await message.edit_text(f"☑️ Успешно выполнена процедура: <b>{procedure.title}</b>",
                                                parse_mode=ParseMode.HTML)
                        profile.money -= procedure.cost
                    else:
                        logger.error(f"Не удалось выполнить процедуру: {procedure.title}")
                        await message.edit_text(f"⚠️ Не удалось выполнить процедуру: <b>{procedure.title}</b>",
                                                parse_mode=ParseMode.HTML)
                else:
                    logger.info(f"Недостаточно денег для процедуры: {procedure.title}")
                    await message.edit_text(f"⚠️ Недостаточно денег для процедуры: <b>{procedure.title}</b>",
                                            parse_mode=ParseMode.HTML)

                # Добавляем асинхронную задержку в 1 секунду между процедурами
                await asyncio.sleep(1.3)

            logger.info("Баланс: %s 🪙", profile.money)
            await message.edit_text(f"Процедуры завершены!\n🪙 Баланс: <b>{profile.money}</b>",
                                    parse_mode=ParseMode.HTML)
        finally:
            if self.user_info:
                clear_user_context()
            logger.debug("Выполнение бьюти-процедур завершено")
