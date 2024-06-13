"""Simple Text input with validation
"""
import re
from typing import Callable

def prompt_v(prompt: str = None, validator: str | Callable = None, not_valid_msg: str = None):
    """Prompts user for input and validates the input.
    Returns value only if validated.
    """
    try:
        valid = False
        user_val = None
        while not valid:
            user_val = input(prompt)
            if validator is not None:
                valid = validator(user_val) if callable(validator) else (re.match(validator, user_val) is not None)
            else:
                valid = True
            if not valid and not_valid_msg:
                print(not_valid_msg)
        return user_val
    except EOFError:
        print(" (abandon)")
        return None