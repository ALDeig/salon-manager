from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.src.dialogs.keyboards.shift import kb_select_item
from app.src.dialogs.states import ShiftEntry
from app.src.services.dates import get_dates_next_week, write_is_avalibale
from app.src.services.db.dao.holder import HolderDao
from app.src.services.exceptions import ShiftIsExistError
from app.src.services.salons import SalonsManager
from app.src.services.shifts.shift_manager import ShiftManager
from app.src.services.texts import dates_text, salon_texts, shift_texts
from app.src.services.user import check_user

router = Router()


@router.callback_query(F.data == "add_shift", F.message.as_("msg"), flags={"dao": True})
async def btn_add_shift(
    call: CallbackQuery, msg: Message, dao: HolderDao, state: FSMContext
):
    """Начинает запись смены. Делает запрос на выбор салона."""
    await call.answer()
    if not await check_user(dao, call.from_user.username):
        await msg.answer(shift_texts.USER_NOT_FOUND)
        return
    if not write_is_avalibale():
        await msg.answer(shift_texts.SHIFT_IS_NOT_AVALIBALE)
        return
    salons = await SalonsManager(dao).get_salons()
    text = salon_texts.select_salon
    kb = kb_select_item([salon.name for salon in salons])
    await msg.answer(text, reply_markup=kb)
    await state.set_state(ShiftEntry.salon)


@router.callback_query(ShiftEntry.salon, F.message.as_("msg"))
async def btn_select_salon(call: CallbackQuery, msg: Message, state: FSMContext):
    """Сохраняет выбранный салон. Делает запросы для выбора дня."""
    await call.answer()
    await state.update_data(salon=call.data)
    text = dates_text.select_day
    await msg.answer(text, reply_markup=kb_select_item(get_dates_next_week()))
    await state.set_state(ShiftEntry.day)


@router.callback_query(ShiftEntry.day, F.message.as_("msg"), flags={"dao": True})
async def btn_select_day(
    call: CallbackQuery, msg: Message, state: FSMContext, dao: HolderDao
):
    """Сохраняет выбранный день. Делает запросы для выбора времени."""
    await call.answer()
    data = await state.get_data()
    await state.update_data(day=call.data)
    times = await SalonsManager(dao).get_salon_times(data["salon"])
    await msg.answer(dates_text.select_time, reply_markup=kb_select_item(times))
    await state.set_state(ShiftEntry.time)


@router.callback_query(ShiftEntry.time, F.message.as_("msg"), flags={"dao": True})
async def btn_select_time(
    call: CallbackQuery, msg: Message, state: FSMContext, dao: HolderDao
):
    """Записывает смену."""
    if call.data is None:
        return
    await call.answer()
    await msg.answer("Записываю смену...")
    data = await state.get_data()
    salon, day, shift_time = data["salon"], data["day"], call.data
    shift_manager = ShiftManager(cast(str, call.from_user.username), dao)
    try:
        await shift_manager.add_entry(salon, day, shift_time)
    except ShiftIsExistError:
        await msg.answer(shift_texts.SHIFT_IS_EXIST)
    else:
        await msg.answer(shift_texts.shift_is_write(day, salon, shift_time))
    await state.clear()


@router.callback_query(F.data == "my_shifts", F.message.as_("msg"), flags={"dao": True})
async def btn_show_my_shifts(call: CallbackQuery, msg: Message, dao: HolderDao):
    """Кнопка показа своих смен."""
    await call.answer()
    if not await check_user(dao, call.from_user.username):
        await msg.answer(shift_texts.USER_NOT_FOUND)
        return
    await msg.answer("Собираю данные")
    shifts = await ShiftManager(cast(str, call.from_user.username), dao).get_my_shifts()
    if not shifts:
        await msg.answer("Смен нет")
        return
    text = ""
    for day, shift in shifts.items():
        text += f"<b>{day}</b>\n{shift.salon}: {shift.time}\n\n"
    await msg.answer(text)


@router.callback_query(
    F.data.startswith("shift_remove"), F.message.as_("msg"), flags={"dao": True}
)
async def btn_shift_remove(call: CallbackQuery, msg: Message, dao: HolderDao):
    await call.answer()
    if call.data is None:
        return
    _, row, col, label = call.data.split(":")
    await ShiftManager(cast(str, call.from_user.username), dao).remove_shift(
        int(row), int(col), label
    )
    await msg.answer(shift_texts.SHIFT_IS_REMOVE)


@router.callback_query(
    F.data == "all_shifts", F.message.as_("msg"), flags={"dao": True}
)
async def btn_all_shifts(call: CallbackQuery, msg: Message, dao: HolderDao):
    await call.answer()
    shift_manager = ShiftManager(cast(str, call.from_user.username), dao)
    shifts = await shift_manager.get_all_shifts()
    texts = shift_texts.all_shifts(shifts)
    if not texts:
        await msg.answer("Смен нет")
    for text in texts:
        await msg.answer(text)
