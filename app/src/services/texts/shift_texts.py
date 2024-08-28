from itertools import zip_longest

USER_NOT_FOUND = "Вы не являетесь пользователем"
SHIFT_IS_WRITE = "Смена записана.\n<b>{day}</b>\n{salon}: {time}"
SHIFT_IS_EXIST = "У вас есть смена в этот день"
SHIFT_WRITE_ERROR = "Неудалось записать смену"
SHIFT_IS_REMOVE = "Смена была удалена"
SHIFT_IS_NOT_AVALIBALE = (
    "Выбрать смену нельзя, смены назначаются только по пятницам и субботам"
)
SALON_TIMES_ERROR = "Не удалось получить данные о времени смен"


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


a = {
    "23.02": {
        "Soxo": {"10-00": 2, "11-00": 1, "12-00": 3},
        "Xiaomi": {"10-01": 1, "11-01": 1},
        "Xiaomi2": {"10-01": 1, "11-01": 1},
        "Xiaomi3": {"10-01": 1, "11-01": 1},
        "Xiaomi4": {"10-01": 1, "11-01": 1},
        "Xiaomi5": {"10-01": 1, "11-01": 1},
        "Xiaomi6": {"10-01": 1, "11-01": 1},
        "Xiaomi7": {"10-01": 1, "11-01": 1},
    },
    "24.02": {
        "Soxo": {"10:00": 2, "11:00": 1},
        "Xiaomi": {"10:00": 1, "11:00": 1, "13:00": 2, "14:00": 5},
        "Xiaomi2": {"10-01": 1, "11-01": 1},
        "Xiaomi3": {"10-01": 1, "11-01": 1},
        "Xiaomi4": {"10-01": 1, "11-01": 1},
        "Xiaomi5": {"10-01": 1, "11-01": 1},
        "Xiaomi6": {"10-01": 1, "11-01": 1},
    },
    "25.02": {
        "Soxo": {"10:00": 2, "11:00": 1},
        "Xiaomi": {"10:00": 1, "11:00": 1, "13:00": 2, "14:00": 5},
        "Xiaomi2": {"10-01": 1, "11-01": 1},
        "Xiaomi3": {"10-01": 1, "11-01": 1},
        "Xiaomi4": {"10-01": 1, "11-01": 1},
        "Xiaomi5": {"10-01": 1, "11-01": 1},
        "Xiaomi6": {"10-01": 1, "11-01": 1},
        "Xiaomi7": {"10-01": 1, "11-01": 1},
        "Xiaomi8": {"10-01": 1, "11-01": 1},
        "Xiaomi9": {"10-01": 1, "11-01": 1},
    },
}


def all_shifts(shifts: dict[str, dict[str, dict[str, int]]]) -> list[str]:
    texts = []
    for day, salons in shifts.items():
        max_cols = 3
        block = f"<b>{day}</b>\n"
        start = 0
        for block_cnt in range(max_cols, len(salons) + max_cols, max_cols):
            salons_text = "".join(
                [
                    f"{salon:^14}|"
                    for cnt, salon in enumerate(salons)
                    if start <= cnt < block_cnt
                ]
            )
            salons_text += "\n" + "".join([f"{'-':->14}+" for _ in range(max_cols)])
            salon_shifts = [
                [f"{shift:>9}: {count:<3}|" for shift, count in shifts_count.items()]
                for index, shifts_count in enumerate(salons.values())
                if start <= index < block_cnt
            ]
            for s in zip_longest(*salon_shifts, fillvalue=f"{"":<14}|"):
                row = "".join(s)
                salons_text += f"\n{row}"

            block += f"<pre>{salons_text}</pre>\n\n"
            start += max_cols

        texts.append(block)
    return texts


def all_shifts1(shifts: dict[str, dict[str, dict[str, int]]]) -> str:
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


# print(all_shifts3(a))
# all_shifts3(a)
# for text in all_shifts(a):
#     print(text)
#     print("---" * 20)
