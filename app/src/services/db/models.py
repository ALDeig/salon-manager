from sqlalchemy import ARRAY, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.src.services.db.base import Base


class User(Base):
    """Пользователи."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(Text, primary_key=True)
    is_other_time: Mapped[bool] = mapped_column(Boolean, default=False)
    cancellations: Mapped[int] = mapped_column(Integer, default=0)


class Salon(Base):
    """Салоны."""

    __tablename__ = "salons"

    name: Mapped[str] = mapped_column(Text, primary_key=True)
    shifts: Mapped[list[str]] = mapped_column(ARRAY(Text))
    order: Mapped[int] = mapped_column(Integer, unique=True)


class TableIndex(Base):
    """Колонки или ряды в Google таблице и их значение."""

    __tablename__ = "table_indexes"

    value: Mapped[str] = mapped_column(Text, primary_key=True)
    verbose: Mapped[str] = mapped_column(Text)
    label: Mapped[str] = mapped_column(Text)
    col: Mapped[str] = mapped_column(String(3))
    col_int: Mapped[int] = mapped_column(Integer)
    row: Mapped[int] = mapped_column(Integer)
