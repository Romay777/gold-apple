from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.database import User
from src.bot.keyboards import get_start_elf_keyboard
from src.config.constants import HEADERS, BASE_URL, AUTH_PARAMS
from src.core.api.client import GameAPI
from src.core.services.beauty_manager import BeautyManager

router = Router()


class AuthStates(StatesGroup):
    waiting_for_token = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Добро пожаловать! Пожалуйста, отправьте ваш Bearer token:")
    await state.set_state(AuthStates.waiting_for_token)

@router.message(Command("me"))
async def show_account_info(message: Message, session: AsyncSession):
    # try:
        query = select(User).where(User.tg_user_id == message.from_user.id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()

        if user:
            profile = await get_profile_data(user.token, message)
            user_rating = await get_user_rating_data(user.token, message)

            await message.answer(
                generate_profile_message(profile, user_rating),
                reply_markup=get_start_elf_keyboard(),
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer("Вы не авторизованы. Пожалуйста, отправьте ваш Bearer token:")
    # except Exception:
    #     await message.answer("Произошла ошибка при получении информации о пользователе.")

@router.message(AuthStates.waiting_for_token)
async def process_token(message: Message, state: FSMContext, session: AsyncSession):
    try:
        # Пробуем найти существующего пользователя
        query = select(User).where(User.tg_user_id == message.from_user.id)
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Если пользователь существует, обновляем токен
            existing_user.token = message.text
            existing_user.username = message.from_user.username
        else:
            # Если пользователя нет, создаем нового
            user = User(
                username=message.from_user.username,
                tg_user_id=message.from_user.id,
                token=message.text
            )
            session.add(user)

        await session.commit()

        await state.clear()

        profile = await get_profile_data(message.text, message)

        user_rating = await get_user_rating_data(message.text, message)

        await message.answer(
            generate_profile_message(profile, user_rating),
            reply_markup=get_start_elf_keyboard(),
            parse_mode=ParseMode.HTML
        )

    except Exception:
        await message.answer(
            "Произошла ошибка при сохранении токена. Пожалуйста, попробуйте снова или обратитесь к администратору.")
        await state.clear()


def generate_profile_message(profile, user_rating):
    return (
        f"👤 Имя: <b>{profile.username}</b>\n"
        f"🌟 Рейтинг: <b>{profile.score}({profile.level}lvl)</b>\n"
        f"⚡ Энергия: <b>{profile.attempts}</b>\n"
        f"🪙 Баланс: <b>{profile.money}</b>\n"
        f"🏆 Место в рейтинге: <b>{user_rating.position}</b>\n"
    )

async def get_profile_data(user_token: str = None, message: Message = None):
    req_headers = HEADERS
    req_headers["Authorization"] = f"Bearer {user_token}"

    user_info = {
        'id': message.from_user.id,
        'username': message.from_user.username
    }

    # Вывод Данных аккаунта в консоль
    api = GameAPI(BASE_URL, AUTH_PARAMS, req_headers)
    beauty_manager = BeautyManager(api, user_info)
    return await beauty_manager.get_profile()

async def get_user_rating_data(user_token: str = None, message: Message = None):
    req_headers = HEADERS
    req_headers["Authorization"] = f"Bearer {user_token}"

    user_info = {
        'id': message.from_user.id,
        'username': message.from_user.username
    }

    # Вывод Данных аккаунта в консоль
    api = GameAPI(BASE_URL, AUTH_PARAMS, req_headers)
    beauty_manager = BeautyManager(api, user_info)
    return await beauty_manager.get_user_rating()