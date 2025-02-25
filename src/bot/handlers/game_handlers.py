from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
import asyncio
import random

from sqlalchemy import select

from src.bot.database import User
from src.bot.handlers.auth_handlers import generate_profile_message
from src.bot.keyboards import get_start_elf_keyboard, get_back_profile_keyboard, get_games_keyboard, \
    get_after_jumper_keyboard, get_after_box_keyboard
from src.config.constants import BASE_URL, AUTH_PARAMS, HEADERS
from src.core.api.client import GameAPI, UserAPI, QuestAPI
from src.core.services.beauty_manager import BeautyManager
from src.core.services.game_manager import GameManager
from src.core.services.quest_manager import QuestManager
from src.core.services.user_manager import UserManager
from src.utils.logger import logger

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
    ap["access_token"] = user_token
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

@router.callback_query(F.data == "play_games")
async def show_available_games(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=get_games_keyboard())

@router.callback_query(F.data == "start_elf_care")
async def process_elf_care(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю уход за вашим эльфом!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    game_api = await get_api(callback, session, "game")
    game_manager = GameManager(game_api, user_info)
    beauty_manager = BeautyManager(game_api, user_info)

    user_api = await get_api(callback, session, "user")
    users_manager = UserManager(user_api, user_info)

    quest_api = await get_api(callback, session, "quest")
    quest_manager = QuestManager(quest_api, user_info)

    await asyncio.sleep(0.5)

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
        "📋 Текущие квесты:\n"
        f"{quest_manager.format_daily_quests_status()}",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(3.5)

    # Update message for each step
    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
        "🎮 Начинаем играть в <b>мини-игры</b>...",
        parse_mode=ParseMode.HTML
    )
    await asyncio.sleep(0.5)
    await game_manager.auto_play_games(message)

    await asyncio.sleep(random.randint(2, 4))

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
        "💅 Выполняем <b>бьюти-процедуры</b>...\n"
        "⏳ Пожалуйста, подождите",
        parse_mode=ParseMode.HTML
    )
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

    await asyncio.sleep(3)

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
        "🎮 Снова играем в <b>мини-игры</b>...",
        parse_mode=ParseMode.HTML
    )
    await asyncio.sleep(0.7)
    await game_manager.auto_play_games(message)

    await asyncio.sleep(1)

    await message.edit_text(
        "🧝‍♂️ <b>Уход за эльфом завершается!</b>\n\n"
        "📋 Итоговое состояние квестов:\n"
        f"{quest_manager.format_daily_quests_status()}",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(2.5)

    # Final profile update
    profile = await beauty_manager.get_profile()
    await message.edit_text(
            generate_profile_message(profile),
            reply_markup=get_start_elf_keyboard(),
            parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == "perform_procedures")
async def perform_procedures(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Выполняем процедуры!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    game_api = await get_api(callback, session, "game")
    beauty_manager = BeautyManager(game_api, user_info)
    await beauty_manager.perform_procedures(message)
    await message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


# TODO adapt for minigames
# @router.callback_query(F.data == "play_games")
# async def play_games(callback: CallbackQuery, session):
#     message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю играть!</b>\n⏳ Получаю данные...",
#                                                parse_mode=ParseMode.HTML)
#     user_info = {
#         'id': callback.from_user.id,
#         'username': callback.from_user.username
#     }
#
#     game_api = await get_api(callback, session, "game")
#     game_manager = GameManager(game_api, user_info)
#     await game_manager.auto_play_games(message)
#     await message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


@router.callback_query(F.data == "play_jumper")
async def play_jumper(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю играть!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }
    try:
        game_api = await get_api(callback, session, "game")
        game_manager = GameManager(game_api, user_info)
        await game_manager.play_jumper(message)
        await message.edit_reply_markup(reply_markup=get_after_jumper_keyboard())
    except:
        logger.warn("Failed to play jumper")
        await message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


# @router.callback_query(F.data == "give_like")
# async def give_like(callback: CallbackQuery, session):
#     await callback.message.edit_text("🧝‍♂️ <b>Ставлю лайк!</b>\n⏳ Получаю данные...",
#                                      parse_mode=ParseMode.HTML)
#     user_info = {
#         'id': callback.from_user.id,
#         'username': callback.from_user.username
#     }
#
#     user_api = await get_api(callback, session, "user")
#     users_manager = UserManager(user_api, user_info)
#     await users_manager.like_first_friend(callback.message)
#     await callback.message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


@router.callback_query(F.data == "open_box")
async def open_box(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Открываю ящик!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    game_api = await get_api(callback, session, "game")
    game_manager = GameManager(game_api, user_info)
    # drop = await game_manager.open_box(message)
    await game_manager.open_box(message)

    # msg = f"Выпало: <b>{drop.title}</b>\n"
    # msg += f"Получено энергии: {drop.attempts}\n" if drop.attempts != 0 else ""
    # msg += f"Получено монет: {drop.money}\n" if drop.money != 0 else ""
    # msg += f"Получено опыта: {drop.score}\n" if drop.score != 0 else ""
    #
    # # TODO get limit from list
    # msg += f"Можно открыть боксов сегодня: <b>{await game_manager.get_limit(message)}</b>"
    #
    # await message.edit_text(
    #     f"{msg}",
    #     parse_mode=ParseMode.HTML
    # )

    await message.edit_reply_markup(reply_markup=get_after_box_keyboard())



@router.callback_query(F.data == "view_quests")
async def show_quests(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Просматриваю квесты и награды!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }
    await asyncio.sleep(0.5)

    quest_api = await get_api(callback, session, "quest")
    quest_manager = QuestManager(quest_api, user_info)

    await message.edit_text(
        f"{quest_manager.format_rewards_collection()}",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(1)

    await message.edit_text(
        "📋 <b>Состояние квестов:</b>\n"
        f"{quest_manager.format_daily_quests_status()}",
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_profile_keyboard()
    )

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery, session):
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    api = await get_api(callback, session, "game")
    beauty_manager = BeautyManager(api, user_info)
    profile = await beauty_manager.get_profile()
    user_rating = await beauty_manager.get_user_rating()

    await callback.message.edit_text(
        generate_profile_message(profile, user_rating),
        reply_markup=get_start_elf_keyboard(),
        parse_mode=ParseMode.HTML
    )