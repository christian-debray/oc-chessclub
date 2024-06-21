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
    try:
        valid = False
        user_val = None
        while not valid:
            user_val = input(prompt)
            if skip_blank and not user_val:
                raise EOFError
            if shortcuts and user_val in shortcuts:
                return shortcuts[user_val]
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
