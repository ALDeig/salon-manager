from collections.abc import Sequence

import sqlalchemy as sa

from app.src.services.db.dao.base_dao import BaseDao
from app.src.services.db.models import Salon, TableIndex, User


class UserDao(BaseDao[User]):
    """Класс работы с базой данных для таблицы User."""

    model = User


class SalonDao(BaseDao[Salon]):
    """Класс работы с базой данных для таблицы Salon."""

    model = Salon

    async def find_all_by_order(self) -> Sequence[Salon]:
        r = await self._session.scalars(sa.select(Salon).order_by(Salon.order))
        return r.all()


class TableIndexDao(BaseDao[TableIndex]):
    """Класс работы с базой данных для таблицы TableIndex."""

    model = TableIndex
