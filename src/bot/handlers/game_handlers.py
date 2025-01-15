from aiogram import Router, F
from aiogram.types import CallbackQuery
import asyncio
import random

from sqlalchemy import select

from src.bot.database import User
from src.bot.keyboards import get_start_elf_keyboard
from src.config.constants import BASE_URL, AUTH_PARAMS, HEADERS
from src.core.api.client import GameAPI, UserAPI, QuestAPI
from src.core.services.beauty_manager import BeautyManager
from src.core.services.game_manager import GameManager
from src.core.services.quest_manager import QuestManager
from src.core.services.user_manager import UserManager

router = Router()

@router.callback_query(F.data == "start_elf_care")
async def process_elf_care(callback: CallbackQuery, session):
    message = await callback.message.edit_text("Занимаюсь с вашим эльфом!..\nПолучаю данные...")

    user = await session.scalar(
        select(User).where(User.tg_user_id == callback.from_user.id)
    )
    if not user:
        await callback.message.edit_text("Ошибка: токен не найден. Используйте /start")
        return

    # Initialize your API clients with user.token
    ap = AUTH_PARAMS
    ap["access_token"] = {user.token}
    ap['token'] = user.token

    h = HEADERS
    h["Authorization"] = f"Bearer {user.token}"

    game_api = GameAPI(BASE_URL, ap, {"Authorization": f"Bearer {user.token}"})
    game_manager = GameManager(game_api)

    user_api = UserAPI(BASE_URL, ap, {"Authorization": f"Bearer {user.token}"})
    users_manager = UserManager(user_api)

    quest_api = QuestAPI(BASE_URL, ap, {"Authorization": f"Bearer {user.token}"})
    quest_manager = QuestManager(quest_api)

    await message.edit_text(
        "Занимаюсь с вашим эльфом!..\n"
        "Текущее состояние квестов:\n"
        f"{quest_manager.format_daily_quests_status()}"
    )

    await asyncio.sleep(5)

    # Update message for each step
    await message.edit_text("Занимаюсь с вашим эльфом!..\nИграю в мини-игры...")
    game_manager = GameManager(game_api)
    game_manager.auto_play_games()

    await asyncio.sleep(random.randint(2, 4))

    await message.edit_text("Занимаюсь с вашим эльфом!..\nВыполняю бьюти-процедуры...")
    beauty_manager = BeautyManager(game_api)
    beauty_manager.perform_procedures() # TODO: Сделать асинхронным с задержкой между процедурами

    await asyncio.sleep(random.randint(2, 4))

    await message.edit_text("Занимаюсь с вашим эльфом!..\nСтавлю лайк другу...")

    users_manager.like_first_friend()

    await asyncio.sleep(random.randint(2, 4))

    await message.edit_text(
        "Занимаюсь с вашим эльфом!..\n"
        "Текущее состояние квестов:\n"
        f"{quest_manager.format_daily_quests_status()}"
    )

    await asyncio.sleep(5)

    rewards_text = quest_manager.format_rewards_collection()
    await message.edit_text(
        "Занимаюсь с вашим эльфом!..\n"
        f"{rewards_text}"
    )

    # Final profile update
    profile = beauty_manager.get_profile()
    await message.edit_text(
        "✅ Все действия выполнены!\n\n"
        f"👤 Имя: {profile.username}\n"
        f"🌟 Рейтинг: {profile.score}\n"
        f"⚡ Энергия: {profile.attempts}\n"
        f"🪙 Баланс: {profile.money}",
        reply_markup=get_start_elf_keyboard()
    )