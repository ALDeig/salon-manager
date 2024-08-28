"""Commands for admin.

add_salon
update_users
all_shifts
"""

from typing import cast

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.src.dialogs.keyboards.admin import kb_remove_salon
from app.src.dialogs.states import AdminStates
from app.src.services.db.dao.holder import HolderDao
from app.src.services.exceptions import (
    BadRangeError,
    CancellationNotAvailableError,
    NotUniqueUsersError,
)
from app.src.services.salons import SalonsManager
from app.src.services.shifts.shift_manager import ShiftManager
from app.src.services.texts import admin_texts, shift_texts
from app.src.services.user import update_user_list

router = Router()


@router.message(Command("add_salon"))
async def cmd_add_salon(msg: Message, state: FSMContext):
    await msg.answer(admin_texts.GET_SALON_NAME)
    await state.set_state(AdminStates.get_salon_name)


@router.message(AdminStates.get_salon_name)
async def get_salon_name(msg: Message, state: FSMContext):
    await state.update_data(salon_name=msg.text)
    await msg.answer(admin_texts.GET_SALON_SHIFTS)
    await state.set_state(AdminStates.get_salon_shifts)


@router.message(AdminStates.get_salon_shifts)
async def get_salon_shifts(msg: Message, state: FSMContext):
    if not msg.text:
        return
    shifts = [shift.strip() for shift in msg.text.split(",") if shift.strip()]
    await state.update_data(salon_shifts=shifts)
    await msg.answer(admin_texts.GET_SALON_INDEX)
    await state.set_state(AdminStates.get_salon_index)


@router.message(AdminStates.get_salon_index, flags={"dao": True})
async def get_salon_index(msg: Message, state: FSMContext, dao: HolderDao):
    if msg.text is None or not msg.text.isdigit():
        await msg.answer(admin_texts.SALON_INDEX_ERROR)
        return
    data = await state.get_data()
    await SalonsManager(dao).add_salon(
        data["salon_name"], data["salon_shifts"], int(msg.text)
    )
    await msg.answer("Готово")
    await state.clear()


@router.message(Command("update_users"))
async def cmd_update_users(msg: Message, state: FSMContext):
    await msg.answer(admin_texts.GET_ALL_USERS)
    await state.set_state("get_all_users")


@router.message(StateFilter("get_all_users"), flags={"dao": True})
async def get_all_users(msg: Message, state: FSMContext, dao: HolderDao):
    if not msg.text:
        return
    try:
        await update_user_list(dao, msg.text)
    except NotUniqueUsersError as er:
        await msg.answer(f"Не уникальный пользователь: {er.user}")
    except BadRangeError as er:
        await msg.answer(f"Некорректный диапазон: {er.ranges}")
    else:
        await msg.answer("Готово")
    await state.clear()


@router.message(Command("salons"), flags={"dao": True})
async def cmd_show_salons(msg: Message, dao: HolderDao, state: FSMContext):
    await state.clear()
    salons = await SalonsManager(dao).get_salons()
    if not salons:
        await msg.answer("Салонов нет")
    for salon in salons:
        shifts = ", ".join(salon.shifts)
        await msg.answer(
            f"{salon.order}. {salon.name}: {shifts}",
            reply_markup=kb_remove_salon(salon.order),
        )


@router.callback_query(
    F.data.startswith("remove_salon:"), F.message.as_("msg"), flags={"dao": True}
)
async def btn_remove_salon(call: CallbackQuery, msg: Message, dao: HolderDao):
    await call.answer()
    if not call.data:
        return
    try:
        await SalonsManager(dao).remove_salon(int(call.data.split(":")[1]))
    except CancellationNotAvailableError:
        await msg.answer("У вас уже две отмены.")
    else:
        await msg.answer("Готово")


@router.message(Command("all_shifts"), flags={"dao": True})
async def btn_all_shifts(msg: Message, dao: HolderDao, state: FSMContext):
    await msg.answer("Собираю данные")
    await state.clear()
    shift_manager = ShiftManager(cast(str, msg.chat.username), dao)
    shifts = await shift_manager.get_all_shifts()
    texts = shift_texts.all_shifts(shifts)
    if not texts:
        await msg.answer("Смен нет")
        return
    for text in texts:
        await msg.answer(text)
