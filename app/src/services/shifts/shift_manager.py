import logging
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from gspread import Cell

from app.src.services.dates import (
    get_days_from_today_to_next_week,
    get_days_month,
)
from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import Salon
from app.src.services.exceptions import (
    CancellationNotAvailableError,
    CellNotFoundError,
    ShiftIsExistError,
    UserNotFoundError,
    WritingShiftError,
)
from app.src.services.gsheet.creds import get_worksheet
from app.src.services.gsheet.sheet import CellData, GSheet
from app.src.services.shifts.consts import (
    COLORS,
    COLS_ON_SALON,
    TableIndexes,
    get_last_column_day,
    get_last_column_week,
)

logger = logging.getLogger(__name__)


@dataclass
class Shift:
    """Данные смены пользователя в таблице."""

    day: str
    salon: str
    time: str
    row: int
    col: int
    label: str


class ShiftManager:
    """Класс для работы со сменами в салонах."""

    def __init__(self, username: str, dao: HolderDao) -> None:
        self._dao = dao
        self._username = username

    async def add_entry(self, salon: str, day: str, time: str) -> None:
        """Добавляет смену в таблицу."""
        gs = GSheet(await get_worksheet())
        user_cell = await gs.find_cell(f"@{self._username}")
        try:
            day_cell = await gs.find_cell(day)
        except CellNotFoundError as er:
            raise WritingShiftError from er
        salons = await self._dao.salon_dao.find_all_by_order()
        last_cell = await gs.get_cell_by_coordinates(
            row=user_cell.row,
            col=get_last_column_day(day_cell.col, len(salons)),
        )
        user_shifts = await gs.get_values_by_rows(
            f"{day_cell.col_name}{user_cell.row}:{last_cell.label}"
        )
        if user_shifts[0]:
            raise ShiftIsExistError
        current_cell = await gs.get_cell_by_coordinates(
            user_cell.row, day_cell.col + self._get_shift_salon_column(salon, salons)
        )
        current_cell.value = time
        await gs.update_cell(current_cell, COLORS.get(time))

    async def get_my_shifts(self) -> dict[str, Shift]:
        user = await self._dao.user_dao.find_one_or_none(username=self._username)
        if user is None:
            raise UserNotFoundError
        gs = GSheet(await get_worksheet())
        user_cell = await gs.find_cell(f"@{user.username}")
        days = get_days_month()
        first_cell = await gs.find_cell(days[0])
        salons = await self._dao.salon_dao.find_all_by_order()
        cells = await gs.get_cells(
            f"{first_cell.col_name}{user_cell.row}:{user_cell.row}"
        )
        return calculate_user_shifts(cells, salons, days)

    async def remove_shift(self, row: int, col: int, label: str) -> None:
        user = await self._dao.user_dao.find_one(username=self._username)
        max_shift_cancellations = 2
        if user.cancellations == max_shift_cancellations:
            raise CancellationNotAvailableError
        gs = GSheet(await get_worksheet())
        await gs.update_cell(CellData(row, col, label, value=""), COLORS.get("white"))
        await self._dao.user_dao.update(
            {"cancellations": user.cancellations + 1}, username=self._username
        )

    async def get_all_shifts(self) -> dict[str, dict[str, dict[str, int]]]:
        """Возвращает словарь с днями, в дне салоны, в салоне смены и их кол-во."""
        gs = GSheet(await get_worksheet())
        user_start_row = await self._dao.table_index_dao.find_one(
            value=TableIndexes.USERS_START
        )
        user_end_row = await self._dao.table_index_dao.find_one(
            value=TableIndexes.USERS_END
        )
        salons = await self._dao.salon_dao.find_all_by_order()
        days = get_days_from_today_to_next_week()
        first_cell = await gs.find_cell(days[0])
        last_cell = await gs.get_cell_by_coordinates(
            user_end_row.row, get_last_column_week(first_cell.col, len(salons))
        )
        shifts = await gs.get_values_by_columns(
            f"{first_cell.col_name}{user_start_row.row}:{last_cell.label}"
        )
        return self._get_all_shifts(shifts, days, salons)

    def _get_all_shifts(
        self, shifts: list[list[str]], days: list[str], salons: Sequence[Salon]
    ) -> dict[str, dict[str, dict[str, int]]]:
        """Возвращает словарь с днями, в дне салоны, в салоне смены и их кол-во."""
        result = defaultdict(dict)
        day_idx = 0
        for day in days:
            for idx, salon in enumerate(salons):
                try:
                    col = shifts[day_idx + idx * COLS_ON_SALON]
                except IndexError:
                    continue
                result[day][salon.name] = self._count_shifts_in_col(col)
            day_idx += len(salons) * COLS_ON_SALON
        return result

    @staticmethod
    def _count_shifts_in_col(col: list[str]) -> dict[str, int]:
        result = defaultdict(int)
        for row in col:
            if row:
                result[row] += 1
        return result

    @staticmethod
    def _get_shift_salon_column(salon: str, salons: Sequence[Salon]) -> int:
        """Получает значение сдвига колонки для выбранного салона."""
        index = next((i for i, s in enumerate(salons) if s.name == salon))
        return index * COLS_ON_SALON


def calculate_user_shifts(
    cells: list[Cell], salons: Sequence[Salon], days: list[str]
) -> dict[str, Shift]:
    """Возвращает словарь со сменами."""
    salons_amount = len(salons)
    result = {}
    for idx_day, day in enumerate(days):
        for idx_salon, salon in enumerate(salons):
            try:
                cell = cells[
                    idx_day * (salons_amount * COLS_ON_SALON)
                    + idx_salon * COLS_ON_SALON
                ]
            except IndexError:
                return result
            if cell.value:
                result[day] = Shift(
                    day, salon.name, cell.value, cell.row, cell.col, cell.address
                )
    return result
