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
    shortcuts: dict[str, str] = None,
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
    formatter = TableFormatter(
        table_data=table_data, pad_left=pad_left, pad_right=pad_right, cell_sep=cell_sep, line_sep=line_sep
    )
    return formatter.render()


class TableFormatter:
    """Helper class to format text tables."""

    class TableCell:
        """Represents a cell in a text table"""

        def __init__(
            self,
            content: str,
            width: int = 0,
            height: int = 0,
            pad_left: int = 1,
            pad_right: int = 1,
        ):
            self.lines: list[str] = content.splitlines()
            self.min_width: int = width
            self.min_height: int = height
            self.pad_left: int = pad_left
            self.pad_right: int = pad_right

        def width(self) -> int:
            """Computes the width of this cell."""
            return max(self.min_width, max([self.pad_left + len(line) + self.pad_right for line in self.lines]))

        def height(self) -> int:
            """Computes the height of this cell."""
            return max(self.min_height, len(self.lines))

        def render_line(self, line_idx: int, min_width: int = 0) -> str:
            """Renders this cell as a list of text lines with normalized width."""
            width = max(min_width, self.width())
            if line_idx >= len(self.lines):
                return " " * width
            else:
                line_str = " "*self.pad_left
                line_str += self.lines[line_idx]
                line_str += " "*self.pad_right
                return line_str.ljust(width)

    def __init__(
        self,
        table_data: list[list[str]],
        pad_left: int = 1,
        pad_right: int = 1,
        cell_sep="|",
        line_sep="-",
    ):
        self.cellpad_left = pad_left
        self.cellpad_right = pad_right
        self.rows: list[list[TableFormatter.TableCell]] = []
        self.widths: list[int] = []
        self.cell_sep: str = cell_sep
        self.line_sep: str = line_sep
        self.set_table_data(table_data)

    def set_table_data(self, table_data: list[list[str]]):
        self.rows = []
        self.widths = [0 for _ in range(len(table_data[0]))]
        for r, row in enumerate(table_data):
            self.rows.append([])
            for c, cell_str in enumerate(row):
                cell = TableFormatter.TableCell(
                    cell_str, pad_left=self.cellpad_left, pad_right=self.cellpad_right
                )
                self.rows[-1].append(cell)
                self.widths[c] = max(self.widths[c], cell.width())

    def _render_row(self, row: list[TableCell]):
        """renders a single row as a string"""
        height = max([cell.height() for cell in row])
        o_lines = []
        #
        # render the cells line by line
        #
        for l_idx in range(height):
            cells_str = []
            for r, cell in enumerate(row):
                cells_str.append(cell.render_line(l_idx, min_width=self.widths[r]))
            o_lines.append(
                self.cell_sep + self.cell_sep.join(cells_str) + self.cell_sep
            )
        # now join the lines
        return "\n".join(o_lines)

    def render(self) -> str:
        """renders the table as a single string"""
        ruler = self.table_ruler()
        row_str = [ruler] if ruler else []
        for row in self.rows:
            row_str.append(self._render_row(row))
            if ruler:
                row_str.append(ruler)
        return "\n".join(row_str)

    def table_ruler(self) -> str:
        if not self.line_sep:
            return ""
        ruler = (
            "+" + "+".join([self.line_sep * c_width for c_width in self.widths]) + "+"
        )
        return ruler
