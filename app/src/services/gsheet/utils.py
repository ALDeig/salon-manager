from gspread.cell import Cell
from gspread.exceptions import IncorrectCellLabel

from app.src.services.exceptions import IncorrectCellNameError


def find_col_and_row_index_by_name(label: str) -> tuple[int, int]:
    try:
        cell = Cell.from_address(label)
    except IncorrectCellLabel as er:
        raise IncorrectCellNameError from er
    return cell.row, cell.col


def find_col_name_by_address(label: str) -> str:
    return "".join(char for char in label if char.isalpha())
