class WritingShiftError(Exception):
    """Невозможно записать смену."""


class CellNotFoundError(Exception):
    """Ячейка не найдена."""


class CancellationNotAvailableError(Exception):
    """Смена не может быть отменена."""


class IncorrectCellNameError(Exception):
    """Некорректное имя ячейки."""


class ShiftIsExistError(Exception):
    """Уже есть смена в этот день."""


class UserNotFoundError(Exception):
    """Юзер не найден в базе данных."""


class NotUniqueUsersError(Exception):
    """Не уникальные пользователи в таблице."""

    def __init__(self, *args: object, user: str) -> None:
        self.user = user
        super().__init__(*args)


class BadRangeError(Exception):
    """Некорректный диапазон."""

    def __init__(self, *args: object, ranges: str) -> None:
        self.ranges = ranges
        super().__init__(*args)
