from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
import asyncio
import random

from sqlalchemy import select

from src.bot.database import User
from src.bot.handlers.auth_handlers import generate_profile_message
from src.bot.keyboards import get_start_elf_keyboard
from src.config.constants import BASE_URL, AUTH_PARAMS, HEADERS
from src.core.api.client import GameAPI, UserAPI, QuestAPI
from src.core.services.beauty_manager import BeautyManager
from src.core.services.game_manager import GameManager
from src.core.services.quest_manager import QuestManager
from src.core.services.user_manager import UserManager

router = Router()

async def get_api(callback: CallbackQuery, session, api_to_get):
    """
    Функция для получения API клиента
    :param callback:
    :param session:
    :param api_to_get: game, quest, user
    :return:
    """
    user = await session.scalar(
        select(User).where(User.tg_user_id == callback.from_user.id)
    )
    user_token = user.token

    # Initialize your API clients with user_token
    ap = AUTH_PARAMS
    ap["access_token"] = {user_token}
    ap['token'] = user_token

    h = HEADERS
    h["Authorization"] = f"Bearer {user_token}"

    if api_to_get == "game":
        api = GameAPI(BASE_URL, ap, {"Authorization": f"Bearer {user_token}"})
    elif api_to_get == "user":
        api = UserAPI(BASE_URL, ap, {"Authorization": f"Bearer {user_token}"})
    else:
        api = QuestAPI(BASE_URL, ap, {"Authorization": f"Bearer {user_token}"})

    return api

@router.callback_query(F.data == "start_elf_care")
async def process_elf_care(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ Начинаю уход за вашим эльфом!\n⏳ Получаю данные...")

    game_api = await get_api(callback, session, "game")
    game_manager = GameManager(game_api)

    user_api = await get_api(callback, session, "user")
    users_manager = UserManager(user_api)

    quest_api = await get_api(callback, session, "quest")
    quest_manager = QuestManager(quest_api)

    await asyncio.sleep(1)

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
        "📋 Текущие квесты:\n"
        f"{quest_manager.format_daily_quests_status()}",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(5)

    # Update message for each step
    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
        "🎮 Начинаем играть в <b>мини-игры</b>...",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(1)

    await game_manager.auto_play_games(message)

    await asyncio.sleep(random.randint(2, 4))

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
        "💅 Выполняем <b>бьюти-процедуры</b>...\n"
        "⏳ Пожалуйста, подождите",
        parse_mode=ParseMode.HTML
    )
    beauty_manager = BeautyManager(game_api)
    await beauty_manager.perform_procedures(message)

    await asyncio.sleep(random.randint(3, 5))

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
        "❤️ Ставим лайк другу...\n"
        "⏳ Пожалуйста, подождите",
        parse_mode=ParseMode.HTML
    )
    await users_manager.like_first_friend(message)

    await asyncio.sleep(random.randint(2, 4))

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом почти завершен!</b>\n\n"
        "🎁 Получение наград:\n"
        f"{quest_manager.format_rewards_collection()}",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(2)

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом завершается!</b>\n\n"
        "📋 Итоговое состояние квестов:\n"
        f"{quest_manager.format_daily_quests_status()}",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(3)

    # Final profile update
    profile = await beauty_manager.get_profile()
    await message.edit_text(
            generate_profile_message(profile),
            reply_markup=get_start_elf_keyboard(),
            parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "perform_3_procedures")
async def perform_procedures(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Выполняем процедуры!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)

    game_api = await get_api(callback, session, "game")
    beauty_manager = BeautyManager(game_api)
    await beauty_manager.perform_procedures(message)


@router.callback_query(F.data == "play_games")
async def play_games(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю играть!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)

    game_api = await get_api(callback, session, "game")
    game_manager = GameManager(game_api)
    await game_manager.auto_play_games(message)


@router.callback_query(F.data == "give_like")
async def give_like(callback: CallbackQuery, session):
    await callback.message.edit_text("🧝‍♂️ <b>Ставлю лайк!</b>\n⏳ Получаю данные...",
                                     parse_mode=ParseMode.HTML)

    user_api = await get_api(callback, session, "user")
    users_manager = UserManager(user_api)
    await users_manager.like_first_friend(callback.message)


@router.callback_query(F.data == "view_quests")
async def show_quests(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Просматриваю квесты и награды!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.5)

    quest_api = await get_api(callback, session, "quest")
    quest_manager = QuestManager(quest_api)

    await message.edit_text(
        f"{quest_manager.format_rewards_collection()}",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(1)

    await message.edit_text(
        "📋 <b>Состояние квестов:</b>\n"
        f"{quest_manager.format_daily_quests_status()}",
        parse_mode=ParseMode.HTML
    )
