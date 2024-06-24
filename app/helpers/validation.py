"""Validator functions.
"""

import re
from datetime import date, datetime
import time


def is_valid_name(val: str):
    """Returns True if given value is accepted as a name
    accept o'hara mà-cNe'ùê'l
    reject o'h4ra mà_cNe'ùê'1
    """
    patt_alphanum_dash = r"^[\w \-']+$"
    patt_nodigits = r"^[^0-9_]+$"
    #
    # TODO: missing the \p{L} character class...
    # workaround: split in two patterns:
    #  first alphanumeric + hyphen + apostrophe
    #  then no digits and no underscore
    #
    if (
        re.match(patt_alphanum_dash, val) is None
        or re.match(patt_nodigits, val) is None
    ):
        return False
    return True


def is_valid_date(val: str) -> bool:
    """Returns True if given value is a valid string representation.
    Currently accepts only ISO-format (YYYY-MM-DD or YYYYMMDD)
    """
    try:
        date.fromisoformat(val)
        return True
    except ValueError:
        return False


def is_valid_time(val: str) -> bool:
    """Returns True if argument is a valid time string
    (HH:MM:SS)"""
    try:
        time.strptime(val, "%H:%M:%S")
        return True
    except ValueError:
        return False


def is_valid_datetime(val: str) -> bool:
    """Returns True if string is a valid datetime in ISO Format
    """
    try:
        datetime.fromisoformat(val)
        return True
    except ValueError:
        return False
