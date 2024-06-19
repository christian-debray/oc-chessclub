from datetime import date, datetime


def format_cols(data: list[list[str]], headers: list[str] = None) -> str:
    """Formats a list of strings into columns"""
    if len(data) == 0:
        return ""
    # pretty print in colmuns
    # first evaluate all lines to compute the cells widths
    if headers:
        cells_widths = [len(c) for c in headers]
    else:
        cells_widths = [0 for _ in range(len(data[0]))]
    for line in data:
        for c in range(len(cells_widths)):
            if len(line[c]) > cells_widths[c]:
                cells_widths[c] = len(line[c])
    cols = []
    if headers is not None:
        cols.append(
            " | ".join(
                [headers[c].ljust(cells_widths[c]) for c in range(len(cells_widths))]
            )
        )
        cols.append(" | ".join("-" * cells_widths[c] for c in range(len(cells_widths))))

    for line in data:
        cols.append(
            " | ".join(
                [line[c].ljust(cells_widths[c]) for c in range(len(cells_widths))]
            )
        )
    return "\n".join(cols)


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
