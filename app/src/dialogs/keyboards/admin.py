from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.src.services.db.models import TableIndex


def kb_change_setting(table_index: TableIndex) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✏️", callback_data=f"change_setting:{table_index.value}"
    )
    builder.adjust(1)
    return builder.as_markup()


def kb_add_setting() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕", callback_data="add_setting"
    )
    builder.adjust(1)
    return builder.as_markup()


def kb_remove_salon(salon_index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✖️", callback_data=f"remove_salon:{salon_index}"
    )
    builder.adjust(1)
    return builder.as_markup()
