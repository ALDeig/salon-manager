from collections.abc import Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class DbSessionMiddleware(BaseMiddleware):
    """Инициализирует сессию с БД и добавляет ее в хендлер.

    В хендлере сессию можно получить аргументом db
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self.session_factory = session_factory

    async def __call__(
        self, handler: Callable, event: TelegramObject, data: dict
    ) -> None:
        session_flag = get_flag(data, "db")
        if not session_flag:
            return await handler(event, data)
        async with self.session_factory() as session:
            data["db"] = session
            return await handler(event, data)
