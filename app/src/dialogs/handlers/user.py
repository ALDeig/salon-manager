from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.src.dialogs.keyboards.user import kb_user_menu
from app.src.services.db.dao.holder import HolderDao
from app.src.services.texts import shift_texts
from app.src.services.user import check_user

router = Router()


@router.message(Command("start"), flags={"dao": True})
async def cmd_start(msg: Message, state: FSMContext, dao: HolderDao):
    await state.clear()
    if not await check_user(dao, msg.chat.username):
        await msg.answer(shift_texts.USER_NOT_FOUND)
        return
    await msg.answer("Меню", reply_markup=kb_user_menu())
