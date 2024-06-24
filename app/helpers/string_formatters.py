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
    for row in data:
        # row cells may contain several lines
        for c in range(len(cells_widths)):
            line_length = max([len(lc) for lc in row[c].splitlines()]) if row[c] else 0
            if line_length > cells_widths[c]:
                cells_widths[c] = line_length
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


def format_table(
    table_data: list[list[str]],
    pad_left: int = 1,
    pad_right: int = 1,
    cell_sep: str = "|",
    line_sep: str = "-",
) -> str:
    """Formats a list of string cells as a table."""
    # first evaluate the dimensions: row lines and  column widths
    table: list[list[list[str]]] = []
    heights = [0 for _ in range(len(table_data))]
    widths = [0 for _ in range(len(table_data[0]))]
    for r in range(len(table_data)):
        row = table_data[r]
        table.append([])
        for c in range(len(row)):
            cell = row[c].splitlines()
            if cell:
                cell_w = max([len(lc) for lc in cell])
            else:
                cell_w = 0
                cell = []
            if cell_w > widths[c]:
                widths[c] = cell_w
            if len(cell) > heights[r]:
                heights[r] = len(cell)
            table[-1].append(cell)

    lines = []

    if line_sep:
        ruler = (
            "+"
            + "+".join(
                [line_sep * (pad_left + pad_right + c_width) for c_width in widths]
            )
            + "+"
        )
    for r in range(len(heights)):
        row_str = []
        if line_sep:
            row_str.append(ruler)
        # row line
        for rl in range(heights[r]):
            line_inner = []
            # columns
            for c in range(len(widths)):
                empty_cell_line = " " * (pad_left + widths[c] + pad_right)
                if rl < len(table[r][c]):
                    line_inner.append(
                        " " * pad_left
                        + table[r][c][rl].ljust(widths[c])
                        + " " * pad_right
                    )
                else:
                    line_inner.append(empty_cell_line)
            if cell_sep:
                row_str.append(cell_sep + cell_sep.join(line_inner) + cell_sep)
            else:
                row_str.append("".join(line_inner))
        lines.append("\n".join(row_str))
    if line_sep:
        lines.append(ruler)
    return "\n".join(lines)

    # then output the table


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


if __name__ == "__main__":
    lorem_ipsum = """Lorem ipsum dolor sit amet,
    consectetur adipiscing elit. Suspendisse ut consequat lectus.
    Aenean maximus est eget magna volutpat, in dignissim."""

    table_data = [
        [
            "Lorem Ipsum",
            "dolor sit amet,\nconsectetur adipiscing elit.",
            "Suspendisee\n\nut consequat",
            "lectus.",
        ],
        ["", "Aenean\nmaximus\nest", "\neget", "magna\voluptat, in dignissim"],
        [
            "Lorem Ipsum",
            "dolor sit amet,",
            "consectetur adipiscing elit.",
            "Suspendisse",
        ],
        ["ut consequat lectus.", "", "", "Aenean maximus est"],
        ["magna volutpat,", "in dignissim.", "", ""],
    ]

    table_str = format_table(table_data, pad_left=1, pad_right=1)
    print(table_str)
