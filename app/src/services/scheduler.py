from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.src.services.shifts.shift_statistic import clear_column, update_statistic
from app.src.services.user import clear_user_cancelled

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


def create_scheduler_tasks():
    scheduler.add_job(update_statistic, "cron", day_of_week=0, hour=12)
    scheduler.add_job(
        clear_column, "cron", day_of_week=0, hour=11, minute=55, args=["shifts_on_week"]
    )
    scheduler.add_job(
        clear_column,
        "cron",
        day_of_week=0,
        hour=11,
        minute=55,
        args=["shifts_on_month"],
    )
    scheduler.add_job(
        clear_column,
        "cron",
        month="2,5,8,11",
        day=1,
        hour=11,
        minute=55,
        args=["total_shifts"],
    )
    scheduler.add_job(clear_user_cancelled, "cron", day_of_week=0, hour=1)
    return scheduler
