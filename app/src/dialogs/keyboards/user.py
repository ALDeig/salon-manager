

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def kb_user_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Выбрать смену", callback_data="add_shift")
    builder.button(text="Мои смены", callback_data="my_shifts")
    builder.adjust(1)
    return builder.as_markup()
