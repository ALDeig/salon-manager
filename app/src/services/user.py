from collections import Counter

from app.src.services.db.base import session_factory
from app.src.services.db.dao.holder import HolderDao
from app.src.services.db.models import User
from app.src.services.exceptions import BadRangeError, NotUniqueUsersError
from app.src.services.gsheet.creds import get_worksheet
from app.src.services.gsheet.sheet import GSheet
from app.src.services.table_settings import TableSettings

# async def save_user(
#     session: AsyncSession, user_id: int, full_name: str, username: str | None
# ):
#     await UserDao(session).insert_or_nothing(
#         index_element="id", id=user_id, full_name=full_name, username=username
#     )


async def update_user_list(dao: HolderDao, ranges: str):
    try:
        users_start, users_end = ranges.split(":")
    except IndexError as er:
        raise BadRangeError(ranges=ranges) from er
    gs = GSheet(await get_worksheet())
    users = await gs.get_values_by_columns(ranges)
    # убрать из списка пустые значения
    users = list(filter(bool, users[0]))
    users_counter = Counter(users)
    for user, count in users_counter.items():
        if count > 1:
            raise NotUniqueUsersError(user=user)

    await dao.user_dao.delete()
    for user in users:
        await dao.user_dao.add(User(username=user.replace("@", "")))
    settings = TableSettings(dao)
    await settings.change_setting("users_start", users_start)
    await settings.change_setting("users_end", users_end)


async def check_user(dao: HolderDao, username: str | None) -> bool:
    user = await dao.user_dao.find_one_or_none(username=str(username))
    return bool(user)


async def clear_user_cancelled():
    async with session_factory() as session:
        dao = HolderDao(session)
        await dao.user_dao.update({"cancellations": 0})
