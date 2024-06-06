from dataclasses import dataclass
from datetime import date
from app.models.model_baseclasses import EntityABC
import re
from app.adapters.json_storage import JSONRepository
from _collections_abc import Hashable
import json

NATIONAL_PLAYER_ID_PATTERN = re.compile(r"^[A-Z]{2}[0-9]{5}$")

def is_valid_national_player_id(val: str):
    """Check if a string is a valid national player ID:
    2 letters followed by 5 digits.
    """
    try:
        return False if not NATIONAL_PLAYER_ID_PATTERN.fullmatch(val) else True
    except TypeError as e:
        if val is None:
            return False
        else:
            raise e

class NationalPlayerID(Hashable):
    """Subset of the str type specific to national player ID format
    """
    def __init__(self, string):
        if not is_valid_national_player_id(string):
            raise ValueError('Invalid player ID')
        self._val:str = string

    def __str__(self):
        return self._val.__str__()
    
    def __hash__(self) -> int:
        return self._val.__hash__()
    
    def __eq__(self, value: object) -> bool:
        return self._val.__eq__(value)
