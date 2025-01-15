# keyboards.py
from gc import callbacks

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_elf_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👽 Выполнить все доступное", callback_data="start_elf_care")],
            [InlineKeyboardButton(text="--------------------", callback_data="nothing")],
            [InlineKeyboardButton(text="💅 Сделать 3 процедуры", callback_data="perform_3_procedures")],
            [InlineKeyboardButton(text="🎮 Сыграть в игры", callback_data="play_games")],
            [InlineKeyboardButton(text="❤️ Поставить лайк", callback_data="give_like")],
            [InlineKeyboardButton(text="📋 Просмотреть квесты + награды", callback_data="view_quests")],
        ]
    )

def get_back_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧝‍♂️ Вернуться к меню", callback_data="back_to_profile")],
        ]
    )