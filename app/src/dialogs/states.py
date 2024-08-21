from aiogram.fsm.state import State, StatesGroup


class ShiftEntry(StatesGroup):
    """Состояния для ввода смены."""

    salon = State()
    day = State()
    time = State()
    other_time = State()


class AdminStates(StatesGroup):
    """Состояния для админки."""

    get_salon_name = State()
    get_salon_shifts = State()
    get_salon_index = State()
