from aiogram.filters.callback_data import CallbackData


class EntryCallbackFactory(CallbackData, prefix="entry"):
    """Коллбеки для ввода смены."""

    action: str
    value: str
