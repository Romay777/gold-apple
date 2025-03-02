# keyboards.py
from gc import callbacks

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_elf_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # TODO NEEDS FIX
            # [InlineKeyboardButton(text="👽 Выполнить все доступное", callback_data="start_elf_care")],
            # [InlineKeyboardButton(text="--------------------", callback_data="nothing")],
            # [InlineKeyboardButton(text="❤️ Поставить лайк", callback_data="give_like")],
            [InlineKeyboardButton(text="💅 Выполнить процедуры", callback_data="perform_procedures")],
            [InlineKeyboardButton(text="⚡️ Потратить энергию", callback_data="spend_energy")],
            [InlineKeyboardButton(text="🎮 Сыграть в игры", callback_data="play_games")],
            [InlineKeyboardButton(text="🎁 Открыть бокс [300 🪙]", callback_data="open_box")],
            [InlineKeyboardButton(text="📋 Просмотреть квесты + награды", callback_data="view_quests")],
        ]
    )

def get_back_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧝‍♂️ Вернуться к меню", callback_data="back_to_profile")],
        ]
    )

def get_games_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="♾️ Прыжки", callback_data="play_jumper")],
            [InlineKeyboardButton(text="👛 Бьюти-пад", callback_data="play_runner")],
            [InlineKeyboardButton(text="⁉️ Memories", callback_data="play_match3")],
            [InlineKeyboardButton(text="🧩 Match3", callback_data="play_match3")],
            [InlineKeyboardButton(text="🧝‍♂️ Вернуться к меню", callback_data="back_to_profile")],
        ]
    )

def get_stop_autoplay_keyboard() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с кнопкой остановки авто-игры"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛑 Остановить", callback_data="stop_auto_play")],
        ]
    )

def get_after_game_keyboard(game: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧝‍♂️ Вернуться к меню", callback_data="back_to_profile")],
            [InlineKeyboardButton(text="🎮 Сыграть ещё", callback_data=f"play_{game}")],
        ]
    )

def get_after_box_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧝‍♂️ Вернуться к меню", callback_data="back_to_profile")],
            [InlineKeyboardButton(text="🎁 Открыть ещё", callback_data="open_box")],
        ]
    )