import time
from datetime import datetime, timedelta


def get_timestamp() -> datetime:
    return datetime.utcnow()


def get_timestamp_from_now(seconds) -> datetime:
    return get_timestamp() + timedelta(seconds=seconds)


def seconds_elapsed(t1: datetime, t2: datetime) -> float:
    return (t2-t1).total_seconds()