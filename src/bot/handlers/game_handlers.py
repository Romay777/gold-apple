from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
import asyncio
import random

from sqlalchemy import select

from src.bot.database import User
from src.bot.handlers.auth_handlers import generate_profile_message
from src.bot.keyboards import get_start_elf_keyboard, get_back_profile_keyboard, get_games_keyboard, \
    get_after_box_keyboard, get_after_game_keyboard, get_stop_auto_work_keyboard, get_items_keyboard
from src.config.constants import BASE_URL, AUTH_PARAMS, HEADERS
from src.core.api.client import GameAPI, UserAPI, QuestAPI
from src.core.services.beauty_manager import BeautyManager
from src.core.services.game_manager import GameManager
from src.core.services.quest_manager import QuestManager
from src.core.services.user_manager import UserManager
from src.utils.logger import logger, clear_user_context, set_user_context
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class AutoWorkStates(StatesGroup):
    active = State()


router = Router()


async def get_api(
        callback: CallbackQuery = None,
        message: Message = None,
        session=None,
        api_to_get: str = None
):
    """
    Универсальная функция для получения API клиента
    """
    # Определяем источник user_id
    if callback:
        user_id = callback.from_user.id
    elif message:
        user_id = message.chat.id
    else:
        raise ValueError("Требуется либо callback, либо message")

    # Получаем пользователя из БД
    user = await session.scalar(
        select(User).where(User.tg_user_id == user_id)
    )

    if not user or not user.token:
        raise ValueError("Пользователь не авторизован")

    # Инициализация параметров API
    ap = AUTH_PARAMS.copy()
    ap.update({
        "access_token": user.token,
        "token": user.token
    })

    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {user.token}"

    # Создаем нужный API клиент
    if api_to_get == "game":
        return GameAPI(BASE_URL, ap, headers)
    elif api_to_get == "user":
        return UserAPI(BASE_URL, ap, headers)
    elif api_to_get == "quest":
        return QuestAPI(BASE_URL, ap, headers)
    else:
        raise ValueError("Неизвестный тип API")

@router.callback_query(F.data == "play_games")
async def show_available_games(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AutoWorkStates.active:
        await callback.answer("Авто-работа активна! Сначала остановите её.")
        return
    try:
        await callback.message.edit_reply_markup(reply_markup=get_games_keyboard())
    except Exception as e:
        logger.error(f"Error in show_available_games: {e}")

# @router.callback_query(F.data == "start_elf_care")
# async def process_elf_care(callback: CallbackQuery, session):
#     message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю уход за вашим эльфом!</b>\n⏳ Получаю данные...",
#                                                parse_mode=ParseMode.HTML)
#     user_info = {
#         'id': callback.from_user.id,
#         'username': callback.from_user.username
#     }
#
#     game_api = await get_api(callback, session, "game")
#     game_manager = GameManager(game_api, user_info)
#     beauty_manager = BeautyManager(game_api, user_info)
#
#     user_api = await get_api(callback, session, "user")
#     users_manager = UserManager(user_api, user_info)
#
#     quest_api = await get_api(callback, session, "quest")
#     quest_manager = QuestManager(quest_api, user_info)
#
#     await asyncio.sleep(0.5)
#
#     await message.edit_text(
#         "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
#         "📋 Текущие квесты:\n"
#         f"{quest_manager.format_daily_quests_status()}",
#         parse_mode=ParseMode.HTML
#     )
#
#     await asyncio.sleep(3.5)
#
#     # Update message for each step
#     await message.edit_text(
#         "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
#         "🎮 Начинаем играть в <b>мини-игры</b>...",
#         parse_mode=ParseMode.HTML
#     )
#     await asyncio.sleep(0.5)
#     await game_manager.auto_play_games(message)
#
#     await asyncio.sleep(random.randint(2, 4))
#
#     await message.edit_text(
#         "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
#         "💅 Выполняем <b>бьюти-процедуры</b>...\n"
#         "⏳ Пожалуйста, подождите",
#         parse_mode=ParseMode.HTML
#     )
#     await beauty_manager.perform_procedures(message)
#
#     await asyncio.sleep(random.randint(3, 5))
#
#     await message.edit_text(
#         "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
#         "❤️ Ставим лайк другу...\n"
#         "⏳ Пожалуйста, подождите",
#         parse_mode=ParseMode.HTML
#     )
#     await users_manager.like_first_friend(message)
#
#     await asyncio.sleep(random.randint(2, 4))
#
#     await message.edit_text(
#         "🧝‍♂️ <b>Уход за эльфом почти завершен!</b>\n\n"
#         "🎁 Получение наград:\n"
#         f"{quest_manager.format_rewards_collection()}",
#         parse_mode=ParseMode.HTML
#     )
#
#     await asyncio.sleep(3)
#
#     await message.edit_text(
#         "🧝‍♂️ <b>Уход за эльфом в процессе!</b>\n\n"
#         "🎮 Снова играем в <b>мини-игры</b>...",
#         parse_mode=ParseMode.HTML
#     )
#     await asyncio.sleep(0.7)
#     await game_manager.auto_play_games(message)
#
#     await asyncio.sleep(1)
#
#     await message.edit_text(
#         "🧝‍♂️ <b>Уход за эльфом завершается!</b>\n\n"
#         "📋 Итоговое состояние квестов:\n"
#         f"{quest_manager.format_daily_quests_status()}",
#         parse_mode=ParseMode.HTML
#     )
#
#     await asyncio.sleep(2.5)
#
#     # Final profile update
#     profile = await beauty_manager.get_profile()
#     await message.edit_text(
#             generate_profile_message(profile),
#             reply_markup=get_start_elf_keyboard(),
#             parse_mode=ParseMode.HTML
#     )

@router.callback_query(F.data == "perform_procedures")
async def perform_procedures(callback: CallbackQuery, session, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AutoWorkStates.active:
        await callback.answer("Авто-работа активна! Сначала остановите её.")
        return

    message = await callback.message.edit_text("🧝‍♂️ <b>Выполняем процедуры!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    game_api = await get_api(callback=callback, session=session,api_to_get="game")
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


@router.callback_query(F.data == "spend_energy")
async def spend_energy(callback: CallbackQuery, session, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AutoWorkStates.active:
        await callback.answer("Авто-работа активна! Сначала остановите её.")
        return

    message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю играть!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    game_api = await get_api(callback=callback, session=session, api_to_get="game")
    game_manager = GameManager(game_api, user_info)
    await game_manager.auto_play_games(message)

@router.callback_query(F.data == "play_jumper")
async def play_jumper(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю играть!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }
    try:
        game_api = await get_api(callback=callback, session=session, api_to_get="game")
        game_manager = GameManager(game_api, user_info)
        await game_manager.start_jumper(message)
        await message.edit_reply_markup(reply_markup=get_after_game_keyboard("jumper"))
    except:
        logger.warning("Failed to play jumper")
        await message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


@router.callback_query(F.data == "play_runner")
async def play_runner(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю играть!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }
    try:
        game_api = await get_api(callback=callback, session=session, api_to_get="game")
        game_manager = GameManager(game_api, user_info)
        await game_manager.start_runner(message)
        await message.edit_reply_markup(reply_markup=get_after_game_keyboard("runner"))
    except:
        logger.warn("Failed to play runner")
        await message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


@router.callback_query(F.data == "play_memories")
async def play_runner(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю играть!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }
    try:
        game_api = await get_api(callback=callback, session=session, api_to_get="game")
        game_manager = GameManager(game_api, user_info)
        await game_manager.start_memories(message)
        await message.edit_reply_markup(reply_markup=get_after_game_keyboard("memories"))
    except:
        logger.warn("Failed to play memories")
        await message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


@router.callback_query(F.data == "play_match3")
async def play_runner(callback: CallbackQuery, session):
    message = await callback.message.edit_text("🧝‍♂️ <b>Начинаю играть!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }
    try:
        game_api = await get_api(callback=callback, session=session, api_to_get="game")
        game_manager = GameManager(game_api, user_info)
        await game_manager.start_match3(message)
        await message.edit_reply_markup(reply_markup=get_after_game_keyboard("match3"))
    except:
        logger.warn("Failed to play memories")
        await message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


@router.callback_query(F.data == "give_like")
async def give_like(callback: CallbackQuery, session):
    await callback.message.edit_text("🧝‍♂️ <b>Ставлю лайк!</b>\n⏳ Получаю данные...",
                                     parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    user_api = await get_api(callback=callback, session=session, api_to_get="user")
    users_manager = UserManager(user_api, user_info)
    await users_manager.like_first_friend(callback.message)
    await callback.message.edit_reply_markup(reply_markup=get_back_profile_keyboard())


@router.callback_query(F.data == "open_box")
async def open_box(callback: CallbackQuery, session, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AutoWorkStates.active:
        await callback.answer("Авто-работа активна! Сначала остановите её.")
        return

    message = await callback.message.edit_text("🧝‍♂️ <b>Открываю ящик!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    game_api = await get_api(callback=callback, session=session, api_to_get="game")
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
async def show_quests(callback: CallbackQuery, session, state: FSMContext):
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    message = await callback.message.edit_text("🧝‍♂️ <b>Просматриваю квесты и награды!</b>\n⏳ Получаю данные...",
                                               parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.5)

    quest_api = await get_api(callback=callback,session=session, api_to_get="quest")
    quest_manager = QuestManager(quest_api, user_info)

    await message.edit_text(
        f"{quest_manager.format_rewards_collection()}",
        parse_mode=ParseMode.HTML
    )

    await asyncio.sleep(0.5)

    await message.edit_text(
        "📋 <b>Состояние квестов:</b>\n"
        f"{quest_manager.format_daily_quests_status()}",
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_profile_keyboard()
    )

@router.callback_query(F.data == "get_items_to_buy")
async def get_items_to_buy(callback: CallbackQuery, session, state: FSMContext):
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    user_api = await get_api(callback=callback, session=session, api_to_get="user")
    users_manager = UserManager(user_api, user_info)

    items = await users_manager.find_cheapest_clothes(callback.message) # list
    # 0 -> cheapest interior
    # 1 -> cheapest clothes

    await callback.message.edit_text("🧝‍♂️ <b>Выберите предмет!</b>",
                                               parse_mode=ParseMode.HTML,
                                               reply_markup=get_items_keyboard(items[0], items[1]))


@router.callback_query(F.data.startswith("buy_item_"))
async def buy_item(callback: CallbackQuery, session, state: FSMContext):
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    user_api = await get_api(callback=callback, session=session, api_to_get="user")
    users_manager = UserManager(user_api, user_info)

    await users_manager.buy_item(callback.message, callback.data.split("_")[2])

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery, session):
    user_info = {
        'id': callback.from_user.id,
        'username': callback.from_user.username
    }

    api = await get_api(callback=callback, session=session, api_to_get="game")
    beauty_manager = BeautyManager(api, user_info)
    profile = await beauty_manager.get_profile()
    user_rating = await beauty_manager.get_user_rating()

    try:
        await callback.message.edit_text(
            generate_profile_message(profile, user_rating),
            reply_markup=get_start_elf_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except:
        logger.error("Failed to back to profile")


@router.callback_query(F.data == "auto_work")
async def start_auto_work(callback: CallbackQuery, session, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AutoWorkStates.active:
        await callback.answer("Авто-работа уже активна!")
        return

    message = await callback.message.edit_text(
        "<b>🤖 В режиме автоматической работы</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🛑 Стоп", callback_data="stop_auto_work")]]
        )
    )

    await state.set_state(AutoWorkStates.active)
    asyncio.create_task(auto_work_loop(message, session, state))


async def auto_work_loop(message, session, state: FSMContext):
    while True:
        if await state.get_state() != AutoWorkStates.active:
            break
        current_day = datetime.now().day
        try:
            user_info = {
                'id': message.chat.id,
                'username': message.chat.username
            }

            # 1. Бьюти-процедуры
            game_api = await get_api(message=message, session=session, api_to_get="game")
            user_api = await get_api(message=message, session=session, api_to_get="user")
            quest_api = await get_api(message=message, session=session, api_to_get="quest")
            set_user_context(user_info.get("id"), user_info.get("username"))
            logger.info("API's got, AutoWork started")

            beauty_manager = BeautyManager(game_api, user_info)
            await beauty_manager.perform_procedures(message)

            await asyncio.sleep(random.uniform(1, 2))

            # 2. Игры
            game_manager = GameManager(game_api, user_info)
            await game_manager.auto_play_games(message)

            # 3. Лайк другу (test)
            users_manager = UserManager(user_api, user_info)
            await users_manager.like_first_friend(message)

            await asyncio.sleep(random.uniform(1, 2))

            # 4. Открытие боксов
            profile = await beauty_manager.get_profile()
            can_open = profile.money // 300
            system_box_limit = await game_manager.get_limit(message)

            # Открываем боксы, не превышая доступное количество и системный лимит
            num_boxes_to_open = min(can_open, system_box_limit)
            for _ in range(num_boxes_to_open):
                await game_manager.open_box(message)
                await asyncio.sleep(1)

            await asyncio.sleep(1)

            # 5. Покупка вещи+интерьера
            # await buy_item(message, session, state)
            #
            # await asyncio.sleep(random.uniform(1, 2))

            # 6. Сбор наград
            quest_manager = QuestManager(quest_api, user_info)
            quest_manager.format_rewards_collection()

            # 7. Повтор игры после сбора наград
            await game_manager.auto_play_games(message)

        except Exception as e:
            logger.error(f"Auto-work error: {str(e)}")
        finally:
            clear_user_context()

        await message.edit_text(
            "<b>🤖 В режиме автоматической работы</b>\n"
            "Последнее обновление: " + datetime.now().strftime("%H:%M:%S"),
            parse_mode=ParseMode.HTML,
            reply_markup=get_stop_auto_work_keyboard()
        )

        # Ожидание 7 - 9 часов
        await asyncio.sleep(random.uniform(25200, 32400))  # 7*3600=25200, 9*3600=32400


@router.callback_query(F.data == "stop_auto_work")
async def init_stop_auto_work(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Авто-работа остановлена",
        reply_markup=get_back_profile_keyboard()
    )

    set_user_context(callback.from_user.id, callback.from_user.username)
    logger.info("Stopped auto-work")