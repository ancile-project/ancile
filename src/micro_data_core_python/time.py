import time
from datetime import datetime, timedelta
from tzlocal import get_localzone


def get_timestamp() -> datetime:
    tz = get_localzone()
    return datetime.now(tz=tz)


def get_timestamp_from_now(seconds) -> datetime:
    return get_timestamp() + timedelta(seconds=seconds)


def seconds_elapsed(t1: datetime, t2: datetime) -> float:
    return (t2-t1).total_seconds()


def day_to_num(day):
    _day = day.strip().lower()
    if _day in ['mon', 'monday', 'mo']: return 0
    elif _day in ['tu', 'tue', 'tues', 'tuesday']: return 1
    elif _day in ['wed', 'wednesday', 'we']: return 2
    elif _day in ['th', 'thu', 'thur', 'thurs', 'thursday']: return 3
    elif _day in ['fri', 'friday', 'fr']: return 4
    elif _day in ['sat', 'saturday', 'sa']: return 5
    elif _day in ['sun', 'sunday', 'su']: return 6


def today_in_list(day_list) -> bool:
    return datetime.today().weekday() in (day_to_num(day) for day in day_list)


def today_in_time_window(lower: str, upper: str) -> bool:
    lower_hour, lower_min = map(int, lower.split(':'))
    upper_hour, upper_min = map(int, upper.split(':'))

    today = datetime.today()

    lower_stamp = datetime(today.year, today.month, today.day, hour=lower_hour,
                           minute=lower_min, tzinfo=get_localzone())

    if upper_hour < lower_hour:
        following_day = lower_stamp + timedelta(days=1)
        upper_stamp = datetime(following_day.year, following_day.month,
                               following_day.day, hour=upper_hour,
                               minute=upper_min, tzinfo=get_localzone())
    else:
        upper_stamp = datetime(today.year, today.month,
                               today.day, hour=upper_hour,
                               minute=upper_min, tzinfo=get_localzone())

    now = get_timestamp()

    return lower_stamp <= now and now <= upper_stamp