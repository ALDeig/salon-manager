from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.src.dialogs.keyboards.admin import kb_change_setting
from app.src.services.db.dao.holder import HolderDao
from app.src.services.table_settings import TableSettings

router = Router()


@router.message(Command("table_settings"), flags={"dao": True})
async def cmd_table_settings(msg: Message, dao: HolderDao):
    settings = await TableSettings(dao).get_current_settings()
    for setting in settings:
        await msg.answer(
            f"{setting.verbose}: {setting.label}",
            reply_markup=kb_change_setting(setting),
        )
    # await msg.answer("Добавить новую настройку", reply_markup=kb_add_setting())


@router.callback_query(F.data.startswith("change_setting"))
async def btn_change_setting(call: CallbackQuery, state: FSMContext):
    if not call.data or not isinstance(call.message, Message):
        return
    await call.answer()
    _, value = call.data.split(":")
    await state.update_data(value=value)
    await call.message.answer("Введите новое значение")
    await state.set_state("get_new_value")


@router.message(StateFilter("get_new_value"), flags={"dao": True})
async def get_new_value(msg: Message, state: FSMContext, dao: HolderDao):
    if not msg.text:
        return
    data = await state.get_data()
    await TableSettings(dao).change_setting(data["value"], msg.text)
    await msg.answer("Готово")
    await state.clear()
