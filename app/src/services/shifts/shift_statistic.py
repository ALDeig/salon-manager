from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from gspread import Cell

from app.src.services.dates import get_dates_current_week
from app.src.services.db.base import session_factory
from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import Salon, TableIndex
from app.src.services.gsheet.creds import get_worksheet
from app.src.services.gsheet.sheet import GSheet
from app.src.services.shifts.consts import (
    COLS_ON_SALON,
    TableIndexes,
    get_last_column_week,
)


@dataclass
class Shift:
    """Данные смены пользователя в таблице."""

    day: str
    salon: str
    time: str


@dataclass
class Data:
    """Данные из таблицы."""

    week: list[str]
    month: list[str]
    total: list[str]
    penalties: list[str]
    shifts: list[list[str]]


@dataclass
class Indexes:
    """Индексы в таблице."""

    first_user_cell: TableIndex
    week_cell: TableIndex
    month_cell: TableIndex
    total_cell: TableIndex
    penalties: TableIndex
    percent: TableIndex
    first_shift_col: str
    last_shift_col: str


class ShiftStatistic:
    """Класс для работы со сменами в салонах."""

    def __init__(self, dao: HolderDao, gs: GSheet) -> None:
        self._dao = dao
        self._gs = gs
        self._days = get_dates_current_week()

    async def update_statistic(self):
        users = await self._dao.user_dao.find_all()
        salons = await self._dao.salon_dao.find_all_by_order()
        indexes = await self._get_indexes(self._days[0], len(salons))
        data = await self._get_data(indexes, len(users))
        cells = []
        for index in range(len(users)):
            shifts = self._user_shifts(data.shifts[index], salons)
            if not shifts:
                continue
            shifts_amount = len(shifts)
            user_cells = [
                self._create_cell_amount_shifts(
                    indexes.first_user_cell.row + index,
                    indexes.week_cell.col_int,
                    data.week,
                    index,
                    shifts_amount,
                ),
                self._create_cell_amount_shifts(
                    indexes.first_user_cell.row + index,
                    indexes.month_cell.col_int,
                    data.month,
                    index,
                    shifts_amount,
                ),
                self._create_cell_amount_shifts(
                    indexes.first_user_cell.row + index,
                    indexes.total_cell.col_int,
                    data.total,
                    index,
                    shifts_amount,
                ),
                self._create_cell_penalties(
                    indexes.first_user_cell.row + index,
                    indexes.penalties.col_int,
                    shifts,
                ),
            ]
            percent = UpPercent(
                shifts, indexes.first_user_cell.row + index, indexes.percent.col_int
            ).calculate()
            if percent:
                user_cells.append(percent)
            cells.extend(user_cells)
        # print(cells)
        await self._gs.update_cells(cells)

    @staticmethod
    def _create_cell_amount_shifts(
        row: int, col: int, data: list[str], index: int, shifts: int
    ) -> Cell:
        try:
            old_value = int(data[index])
        except (IndexError, ValueError):
            old_value = ""
        value = old_value + shifts if old_value else shifts
        return Cell(row=row, col=col, value=value)  # type: ignore[]

    @staticmethod
    def _create_cell_penalties(row: int, col: int, shifts: dict[int, Shift]) -> Cell:
        min_shifts = 3
        salon_shifts = defaultdict(int)
        for shift in shifts.values():
            salon_shifts[shift.salon] += 1
        if (
            ("Сохо" in salon_shifts and "Барби" in salon_shifts)
            or salon_shifts.get("Сохо", 0) > min_shifts
            or salon_shifts.get("Барби", 0) > min_shifts
        ):
            value = ""
        else:
            value = -2
        return Cell(row=row, col=col, value=value)  # type: ignore[]

    async def _get_indexes(self, day: str, amount_salons: int) -> Indexes:
        first_cell = await self._gs.find_cell(day)
        last_cell = await self._gs.get_cell_by_coordinates(
            row=1,
            col=get_last_column_week(first_cell.col, amount_salons),
        )
        return Indexes(
            await self._dao.table_index_dao.find_one(value=TableIndexes.USERS_START),
            await self._dao.table_index_dao.find_one(value=TableIndexes.SHIFTS_WEEK),
            await self._dao.table_index_dao.find_one(value=TableIndexes.SHIFTS_MONTH),
            await self._dao.table_index_dao.find_one(value=TableIndexes.TOTAL_SHIFTS),
            await self._dao.table_index_dao.find_one(value=TableIndexes.PENALTIES_DOWN),
            await self._dao.table_index_dao.find_one(value=TableIndexes.PERCENT),
            first_cell.col_name,
            last_cell.col_name,
        )

    def _user_shifts(
        self, shifts_row: list[str], salons: Sequence[Salon]
    ) -> dict[int, Shift]:
        salons_amount = len(salons)
        shifts = {}
        for idx_day, day in enumerate(self._days):
            for idx_salon, salon in enumerate(salons):
                try:
                    shift = shifts_row[
                        idx_day * (salons_amount * COLS_ON_SALON)
                        + idx_salon * COLS_ON_SALON
                    ]
                except IndexError:
                    return shifts
                if shift:
                    shifts[idx_day + 1] = Shift(day, salon.name, shift)
        return shifts

    async def _get_data(self, indexes: Indexes, amount_users: int) -> Data:
        first_row = indexes.first_user_cell.row
        last_row = indexes.first_user_cell.row + amount_users - 1
        week = await self._gs.get_values_by_columns(
            f"{indexes.week_cell.col}{first_row}:{indexes.week_cell.col}{last_row}"
        )
        month = await self._gs.get_values_by_columns(
            f"{indexes.month_cell.col}{first_row}:{indexes.month_cell.col}{last_row}"
        )
        total = await self._gs.get_values_by_columns(
            f"{indexes.total_cell.col}{first_row}:{indexes.total_cell.col}{last_row}"
        )
        penalties = await self._gs.get_values_by_columns(
            f"{indexes.penalties.col}{first_row}:{indexes.penalties.col}{last_row}"
        )
        shifts = await self._gs.get_values_by_rows(
            f"{indexes.first_shift_col}{first_row}:{indexes.last_shift_col}{last_row}"
        )
        return Data(week[0], month[0], total[0], penalties[0], shifts)


class UpPercent:
    """Класс подсчета увеличенного процента."""

    def __init__(self, shifts: dict[int, Shift], row: int, col: int) -> None:
        self._shifts = shifts
        self._row = row
        self._col = col

    def calculate(self) -> Cell | None:
        """Подсчет процента."""
        percent = self._count_percent()
        if percent:
            return Cell(self._row, self._col, percent)  # type: ignore[]
        return None

    def _count_percent(self) -> int | None:
        """Подсчет процента."""
        salon_shifts = self._shifts_on_salon()
        shifts_sum = sum(salon_shifts.values())
        percent = None
        if shifts_sum == 4:  # noqa: PLR2004
            percent = 40
        elif shifts_sum == 5:  # noqa: PLR2004
            percent = 42
        elif shifts_sum > 5:  # noqa: PLR2004
            percent = 44
        elif self._amount_lub_shifts() > 3:  # noqa: PLR2004
            percent = 40
        else:
            percent = None
        return percent

    def _shifts_on_salon(self) -> dict[str, int]:
        """Подсчитывает кол-во смен в салонах.
        Смена 13-7 для некоторых салонов считается за две.
        """
        salons_shifts = defaultdict(int)
        for shift in self._shifts.values():
            if shift.salon in {"Сохо", "Барби", "Имп"} and shift.time == "13-7":
                salons_shifts[shift.salon] += 2
            else:
                salons_shifts[shift.salon] += 1
        return salons_shifts

    def _amount_lub_shifts(self) -> int:
        """Подсчитывает количество суточных смен в салоне Луб."""
        cnt = 0
        for shift in self._shifts.values():
            if shift.salon == "Луб" and shift.time == "13-7":
                cnt += 1
        return cnt


async def clear_column(value: str):
    async with session_factory() as session:
        dao = HolderDao(session)
        gs = GSheet(await get_worksheet())
        value_range = await dao.table_index_dao.find_one_or_none(value=value)
        if not value_range:
            return
        users_start = await dao.table_index_dao.find_one(value=TableIndexes.USERS_START)
        users = await dao.user_dao.find_all()
        cells = [
            Cell(users_start.row + i, value_range.col_int, value="")
            for i in range(len(users))
        ]
        await gs.update_cells(cells)


async def update_statistic():
    async with session_factory() as session:
        statistic_maneger = ShiftStatistic(
            HolderDao(session), GSheet(await get_worksheet())
        )
        await statistic_maneger.update_statistic()
