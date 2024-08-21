from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.src.dialogs.keyboards.user import kb_user_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await msg.answer("Меню", reply_markup=kb_user_menu())
    await state.clear()
