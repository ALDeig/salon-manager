from collections.abc import Sequence

from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import TableIndex
from app.src.services.gsheet.utils import (
    find_col_and_row_index_by_name,
    find_col_name_by_address,
)


class TableSettings:
    """Класс для работы с таблицами."""

    def __init__(self, dao: HolderDao) -> None:
        self._dao = dao

    async def get_current_settings(self) -> Sequence[TableIndex]:
        return await self._dao.table_index_dao.find_all()

    async def change_setting(self, value: str, label: str) -> None:
        if label.isalnum():
            label += "1"
        row, col, col_name = self._get_indexes_by_label(label)
        await self._dao.table_index_dao.update(
            {"label": label, "col": col_name, "col_int": col, "row": row}, value=value
        )

    async def add_setting(self, value: str, label: str, verbose: str):
        row, col, col_name = self._get_indexes_by_label(label)
        await self._dao.table_index_dao.add(
            TableIndex(
                value=value,
                label=label,
                col=col_name,
                col_int=col,
                row=row,
                verbose=verbose,
            )
        )

    @staticmethod
    def _get_indexes_by_label(label: str) -> tuple[int, int, str]:
        row, col = find_col_and_row_index_by_name(label)
        col_name = find_col_name_by_address(label)
        return row, col, col_name
