from itertools import zip_longest

USER_NOT_FOUND = "Вы не являетесь пользователем"
SHIFT_IS_WRITE = "Смена записана.\n<b>{day}</b>\n{salon}: {time}"
SHIFT_IS_EXIST = "У вас есть смена в этот день"
SHIFT_IS_REMOVE = "Смена была удалена"
SHIFT_IS_NOT_AVALIBALE = (
    "Выбрать смену нельзя, смены назначаются только по пятницам и субботам"
)


def shift_is_write(day: str, salon: str, shift_time: str) -> str:
    return f"Смена записана.\n<b>{day}</b>\n{salon}: {shift_time}"


def all_shifts_2(shifts: dict[str, dict[str, dict[str, int]]]) -> list[str]:
    texts = []
    for day, salons in shifts.items():
        text = f"📆 <b>{day}</b>\n\n"
        for salon, shifts_count in salons.items():
            text += f"🏡{salon}\n" + "\n".join(
                f"{shift}: {count}" for shift, count in shifts_count.items()
            )
            text += "\n\n"
        texts.append(text)
    return texts


# a = {
#     "23.02": {
#         "Soxo": {"10-00": 2, "11-00": 1, "12-00": 3},
#         "Xiaomi": {"10-01": 1, "11-01": 1},
#     },
#     "24.02": {
#         "Soxo": {"10:00": 2, "11:00": 1},
#         "Xiaomi": {"10:00": 1, "11:00": 1, "13:00": 2, "14:00": 5},
#     },
# }


def all_shifts(shifts: dict[str, dict[str, dict[str, int]]]) -> str:
    texts = ""
    for day, salons in shifts.items():
        salons_text = "".join([f"{salon:<10}" for salon in salons])
        salon_shifts = [
            [f"{shift:>5}: {count:<3}" for shift, count in shifts_count.items()]
            for shifts_count in salons.values()
        ]
        for s in zip_longest(*salon_shifts, fillvalue=f"{"":<10}"):
            row = "".join(s)
            salons_text += f"\n{row}"

        texts += f"<b>{day}</b>\n<pre>{salons_text}</pre>\n\n"
    return texts


# all_shifts_2(a)
# for text in all_shifts_2(a):
#     print(text)
