"""Toolkit providing simple controls to use in a text-based app.
"""

import re
from typing import Callable
import os
from app.helpers import ansi
import app


def prompt_v(
    prompt: str = None,
    validator: str | Callable = None,
    not_valid_msg: str = None,
    skip_blank=False,
    shortcuts: dict[str, str] = None
):
    """Prompts user for input and validates the input, with a basic support for shortcuts.
    Returns value only if validated, or the value associated with a shortuct if the shortcut is
    entered by the user.

    If skip_blank is True, skips validation when user input is empty and returns None.
    """
    keymap = {}
    if shortcuts:
        # shortcuts are case-insensitive
        for k, v in shortcuts.items():
            keymap[k] = v
            keymap[k.upper()] = v
            keymap[k.lower()] = v
    try:
        valid = False
        user_val = None
        while not valid:
            user_val = input(prompt)
            if skip_blank and not user_val:
                raise EOFError
            if user_val in keymap:
                return keymap[user_val]
            if validator is not None:
                valid = (
                    validator(user_val)
                    if callable(validator)
                    else (re.match(validator, user_val) is not None)
                )
            else:
                valid = True
            if not valid and not_valid_msg:
                print(ansi.Formatter.format(not_valid_msg, "yellow"))
        return user_val
    except EOFError:
        print(" (abandon)")
        return None


def form_field(
    field: str,
    form_data: dict,
    label: str = None,
    validator: str | Callable = None,
    not_valid_msg: str = None,
    skip_blank: bool = False,
    frozen_fields: list[str] = None,
    display_current: bool = True,
) -> str:
    """Template to render either an input or displaying a frozen field.

    form_data holds a view of the data where field can be found.

    If the field name is found in the frozen_fields param, then don't prompt for a value.
    Display and return the current value found in form_data instead.

    Otherwise, prompt the user for a value for field, using the prompt_v function,
    and return the user value.
    When prompting for a new value, the function can also display the current value found
    in form_data.
    """
    frozen_fields = frozen_fields or []
    label = label or f"{field}"
    if field in frozen_fields:
        print(f"{label}: {form_data.get(field)}")
        return form_data.get(field)
    else:
        if display_current:
            label = f"{label} (current={form_data.get(field)}): "
        else:
            label += ": "
        return prompt_v(
            prompt=label,
            validator=validator,
            not_valid_msg=not_valid_msg,
            skip_blank=skip_blank,
        )


def clear():
    """Clears the console screen.

    (makes a call to the OS system)
    """
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")


if app.KEYBOARD_MODULE == "ansio":
    # define alternative methods to promt for confirmation
    import app.helpers.ansio_ui as ansio_ui

    proceed_any_key = ansio_ui.proceed_any_key
    confirm = ansio_ui.confirm
else:
    # provide default functions

    def proceed_any_key(msg="Press enter to proceed", timeout: float = None):
        """Default implementation of a proceed msg."""
        input(ansi.Formatter.format(msg, ansi.Formatter.CYAN))

    def confirm(msg="enter Y to confirm", timeout: float = None) -> bool:
        """Prompts user to confirm an action y entering a specific key ('y').

        Returns True if user confirmed, False otherwise."""
        confirm = input(ansi.Formatter.format(msg, ansi.Formatter.CYAN))
        return confirm.upper() == "Y"


def format_table(
    table_data: list[list[str]],
    pad_left: int = 1,
    pad_right: int = 1,
    cell_sep: str = "|",
    line_sep: str = "-",
) -> str:
    """Formats a list of string cells as a table."""
    # first evaluate the dimensions: row lines and  column widths
    if len(table_data) == 0:
        return ""
    table: list[list[list[str]]] = []
    heights = [0 for _ in range(len(table_data))]
    widths = [0 for _ in range(len(table_data[0]))]
    for r in range(len(table_data)):
        row = table_data[r]
        table.append([])
        for c in range(len(row)):
            cell = row[c].splitlines() if row[c] else []
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
        if r > len(table):
            continue
        for rl in range(heights[r]):
            line_inner = []
            # columns
            for c in range(len(widths)):
                if c > len(table[r]):
                    continue
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
