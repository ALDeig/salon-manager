import logging
from collections.abc import Sequence

from sqlalchemy.exc import NoResultFound

from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import Salon
from app.src.services.exceptions import SalonNotFoundError

logger = logging.getLogger(__name__)


class SalonsManager:
    """Класс для работы с салонами."""

    def __init__(self, dao: HolderDao) -> None:
        self._dao = dao

    async def get_salons(self) -> Sequence[Salon]:
        return await self._dao.salon_dao.find_all_by_order()

    async def add_salon(self, name: str, shifts: list[str], index: int) -> None:
        await self._dao.salon_dao.add(Salon(name=name, shifts=shifts, order=index))

    async def get_salon(self, name: str) -> Salon:
        try:
            salon = await self._dao.salon_dao.find_one(name=name)
        except NoResultFound as er:
            logger.error("Salon %s not found", name)  # noqa: TRY400
            raise SalonNotFoundError from er
        return salon

    async def get_salon_times(self, name: str) -> list[str]:
        salon = await self.get_salon(name)
        return salon.shifts

    async def remove_salon(self, salon_index: int) -> None:
        await self._dao.salon_dao.delete(order=salon_index)
