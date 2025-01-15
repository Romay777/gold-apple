from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from main import request_profile_data
from src.bot.database import User
from src.bot.keyboards import get_start_elf_keyboard

router = Router()


class AuthStates(StatesGroup):
    waiting_for_token = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Добро пожаловать! Пожалуйста, отправьте ваш Bearer token:")
    await state.set_state(AuthStates.waiting_for_token)

@router.message(Command("me"))
async def show_account_info(message: Message, session: AsyncSession):
    try:
        query = select(User).where(User.tg_user_id == message.from_user.id)
        user = await session.execute(query)
        user = user.scalar_one_or_none()

        if user:
            profile = await request_profile_data(user.token)
            await message.answer(
                generate_profile_message(profile),
                reply_markup=get_start_elf_keyboard(),
                parse_mode=ParseMode.HTML
            )
        else:
            await message.answer("Вы не авторизованы. Пожалуйста, отправьте ваш Bearer token:")
    except Exception:
        await message.answer("Произошла ошибка при получении информации о пользователе.")

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
        # Get profile info using your existing API
        profile = await request_profile_data(message.text)  # You'll need to implement this

        await message.answer(
            generate_profile_message(profile),
            reply_markup=get_start_elf_keyboard(),
            parse_mode=ParseMode.HTML
        )

    except Exception:
        await message.answer(
            "Произошла ошибка при сохранении токена. Пожалуйста, попробуйте снова или обратитесь к администратору.")
        await state.clear()


def generate_profile_message(profile):
    return (
        f"👤 Имя: {profile.username}\n"
        f"🌟 Рейтинг: {profile.score}({profile.level}lvl)\n"
        f"⚡ Энергия: {profile.attempts}\n"
        f"🪙 Баланс: {profile.money}"
    )