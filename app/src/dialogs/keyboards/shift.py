from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def kb_select_item(items: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(
            text=item, callback_data=item
        )
    builder.adjust(1)
    return builder.as_markup()


def kb_shift_remove(row: int, col: int, label: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✖️", callback_data=f"shift_remove:{row}:{col}:{label}"
    )
    builder.adjust(1)
    return builder.as_markup()
