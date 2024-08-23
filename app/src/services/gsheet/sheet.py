from dataclasses import dataclass

import gspread_asyncio
from gspread import Cell
from gspread.utils import Dimension, ValueRenderOption

from app.src.services.gsheet.utils import find_col_name_by_address


@dataclass
class CellData:
    """Координаты ячейки в таблице."""

    row: int
    col: int
    label: str
    value: str = ""

    @property
    def col_name(self) -> str:
        return find_col_name_by_address(self.label)


class GSheet:
    """Класс работы с таблицей Google Sheets."""

    def __init__(self, ws: gspread_asyncio.AsyncioGspreadWorksheet) -> None:
        self._ws = ws

    async def get_values_by_rows(self, range_name: str) -> list[list[str]]:
        return await self._ws.get_values(
            range_name=range_name, major_dimension=Dimension.rows
        )

    async def get_values_by_columns(self, range_name: str) -> list[list[str]]:
        return await self._ws.get_values(
            range_name=range_name,
            major_dimension=Dimension.cols,
            value_render_option=ValueRenderOption.formatted,
        )

    async def get_cells(self, *args, **kwargs) -> list[Cell]:  # noqa: ANN002
        return await self._ws.range(*args, **kwargs)

    async def find_cell(self, value: str) -> CellData:
        cell = await self._ws.find(value)
        return CellData(row=cell.row, col=cell.col, label=cell.address)

    async def get_cell_by_coordinates(self, row: int, col: int) -> CellData:
        cell = await self._ws.cell(row, col)
        return CellData(row=cell.row, col=cell.col, label=cell.address)

    async def update_cell(
        self,
        cell: CellData,
        format_color: dict[str, float] | None = None,
    ):
        await self._ws.update_cell(row=cell.row, col=cell.col, value=cell.value)
        if format_color:
            await self._ws.format(cell.label, {"backgroundColor": format_color})

    async def update_cells(self, cells: list[Cell]) -> None:
        await self._ws.update_cells(cells)
