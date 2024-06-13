"""Simple Text input with validation
"""
import re
from typing import Callable
from app.helpers import ansi
# ansio: alpha revision
# detect keyboard events.
# see https://github.com/nineteendo/ansio.git
import ansio
import ansio.input

def prompt_v(prompt: str = None, validator: str | Callable = None, not_valid_msg: str = None, skip_blank= False):
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
                valid = validator(user_val) if callable(validator) else (re.match(validator, user_val) is not None)
            else:
                valid = True
            if not valid and not_valid_msg:
                print(ansi.Formatter.format(not_valid_msg, 'yellow'))
        return user_val
    except EOFError:
        print(" (abandon)")
        return None

def proceed_any_key(msg="Press any key to proceed", timeout: float = None):
    print(ansi.Formatter.format(msg, ansi.Formatter.CYAN))
    with ansio.raw_input:
        evt = ansio.input.get_input_event(timeout=timeout)

def confirm(msg="press Y to confirm", timeout: float = None):
    print(ansi.Formatter.format(msg, ansi.Formatter.CYAN))
    evt = None
    with ansio.raw_input:
        evt = ansio.input.get_input_event(timeout=timeout)
    if evt:
        return evt.upper() == 'Y'
    return False
