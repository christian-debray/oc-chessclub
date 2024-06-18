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
):
    """Prompts user for input and validates the input.
    Returns value only if validated.

    If skip_blank is True, skips validation when user input is empty and returns None.
    """
    try:
        valid = False
        user_val = None
        while not valid:
            user_val = input(prompt)
            if skip_blank and not user_val:
                raise EOFError
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
