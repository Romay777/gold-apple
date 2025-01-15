from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from src.bot.database import User

from main import request_profile_data
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
            profile = request_profile_data(user.token)
            await message.answer(
                f"👤 Имя: {profile.username}\n"
                f"🌟 Рейтинг: {profile.score}\n"
                f"⚡ Энергия: {profile.attempts}\n"
                f"🪙 Баланс: {profile.money}",
                reply_markup=get_start_elf_keyboard()
            )
        else:
            await message.answer("Вы не авторизованы. Пожалуйста, отправьте ваш Bearer token:")
    except Exception as e:
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
        profile = request_profile_data(message.text)  # You'll need to implement this

        await message.answer(
            f"👤 Имя: {profile.username}\n"
            f"🌟 Рейтинг: {profile.score}\n"
            f"⚡ Энергия: {profile.attempts}\n"
            f"🪙 Баланс: {profile.money}",
            reply_markup=get_start_elf_keyboard()
        )

    except Exception as e:
        await message.answer(
            "Произошла ошибка при сохранении токена. Пожалуйста, попробуйте снова или обратитесь к администратору.")
        await state.clear()