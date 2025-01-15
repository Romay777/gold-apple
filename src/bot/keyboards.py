# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_elf_keyboard() -> InlineKeyboardMarkup:
    # В aiogram 3.x нужно передавать список кнопок при создании
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Заняться эльфиком", callback_data="start_elf_care")]
        ]
    )