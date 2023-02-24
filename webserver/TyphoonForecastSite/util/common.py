from typing import List
import arrow
from datetime import datetime


def inter(a: [], b: []) -> []:
    return list(set(a) & set(b))


def convert_str_2_utc_dt(dt_str: str, is_to_utc=True) -> datetime:
    """
        将字符串类型的dt -> datetime.datetime (utc)

    """
    return arrow.get(dt_str).shift(hours=-8).datetime if is_to_utc else arrow.get(dt_str).datetime
