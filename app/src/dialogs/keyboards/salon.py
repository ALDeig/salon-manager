from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.src.services.db.models import Salon


def kb_select_salon(salons: Sequence[Salon]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for salon in salons:
        builder.add(InlineKeyboardButton(text=salon.name, callback_data=salon.name))
    builder.adjust(1)
    return builder.as_markup()
