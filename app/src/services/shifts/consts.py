from enum import StrEnum


class TableIndexes(StrEnum):
    """Класс для хранения настроек таблицы."""

    PENALTIES_DOWN = "penalties_down"
    SHIFTS_WEEK = "shifts_on_week"
    SHIFTS_MONTH = "shifts_on_month"
    TOTAL_SHIFTS = "total_shifts"
    PERCENT = "percent"
    FINAL_PERCENT = "final_percent"
    USERS_START = "users_start"
    USERS_END = "users_end"


COLS_ON_SALON = 2
DAYS_ON_WEEK = 7
DAYS_ON_MONTH = 30
COLORS = {
    "11-23": {"red": 1.0, "green": 0.0, "blue": 1.0},
    "13-22": {"red": 1.0, "green": 0.0, "blue": 1.0},
    "13-7": {"red": 0.0, "green": 1.0, "blue": 0.0},
    "22-7": {"red": 0.64, "green": 0.78, "blue": 0.96},
    "23-11": {"red": 0.64, "green": 0.78, "blue": 0.96},
    "white": {"red": 1.0, "green": 1.0, "blue": 1.0},
}


def get_last_column_week(mondey_col: int, salon_amount: int) -> int:
    """Возвращает номер последний колонки недели с учетом количества салонов."""
    return (mondey_col + salon_amount * COLS_ON_SALON * DAYS_ON_WEEK) - 1


def get_last_column_day(mondey_col: int, salon_amount: int) -> int:
    """Возвращает номер последний колонки дня с учетом количества салонов."""
    return (mondey_col + salon_amount * COLS_ON_SALON) - 1
