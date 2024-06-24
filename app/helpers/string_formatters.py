from datetime import date, datetime


def formatdate(d: str | date, fmt: str = "%Y-%m-%d", empty: str = "") -> str:
    """Formats a date, whatever the input format.
    returns empty string if the input is empty or if no formatting is possible
    """
    if not d:
        return empty
    if isinstance(d, date) or isinstance(d, datetime):
        return d.strftime(fmt)
    if isinstance(d, str):
        try:
            return datetime.fromisoformat(d).strftime(fmt)
        except Exception:
            return empty
    return empty
