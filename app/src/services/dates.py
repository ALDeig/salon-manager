from datetime import date, timedelta


def get_dates_next_week() -> list[str]:
    """Возвращает список дат следующей недели."""
    next_monday = get_monday_next_week()
    return [(next_monday + timedelta(days=cnt)).strftime("%d.%m") for cnt in range(7)]


def get_monday_next_week() -> date:
    """Находит число следующего понедельника и возвращает его."""
    next_week = date.today() + timedelta(days=7)  # noqa: DTZ011
    return next_week - timedelta(days=next_week.weekday())


def get_days_month() -> list[str]:
    """Возвращает список дат в текущем месяце."""
    today = date.today()  # noqa: DTZ011
    return [(today + timedelta(days=cnt)).strftime("%d.%m") for cnt in range(30)]


def write_is_avalibale() -> bool:
    """Проверяет, доступна ли запись.
    Запись доступна в пятницу и субботу.
    """
    week_day = date.today().weekday()  # noqa: DTZ011
    return week_day in {4, 5}
