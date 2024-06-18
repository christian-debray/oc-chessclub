from dataclasses import dataclass
from datetime import date
from app.models.model_baseclasses import EntityABC
import re
from app.adapters.json_storage import JSONRepository
from _collections_abc import Hashable
import json
from app.helpers import validation

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
        self._val: str = string

    def __str__(self):
        return self._val.__str__()

    def __hash__(self) -> int:
        return self._val.__hash__()

    def __eq__(self, value: object) -> bool:
        return self._val.__eq__(value)

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class Player(EntityABC):
    """Player Entity

    A Player is identified by its unique National Player ID
    and: surname, name and birthdate
    """
    national_player_id: NationalPlayerID = None
    surname: str = None
    name: str = None
    birthdate: date = None

    def id(self) -> NationalPlayerID:
        return self.national_player_id

    def set_id(self, id):
        self.national_player_id = NationalPlayerID(str(id))

    def is_valid(self) -> bool:
        """return True if all data stored by this object is valid.
        """
        return is_valid_national_player_id(str(self.id())) and\
            isinstance(self.birthdate, date) and\
            validation.is_valid_name(self.surname) and\
            validation.is_valid_name(self.name)

    @classmethod
    def copy(cls, other_player: 'Player'):
        """Copies all data from one player ot a new Player object.
        """
        return cls(national_player_id=NationalPlayerID(str(other_player.id())) if other_player.id() else None,
                   surname=other_player.surname,
                   name=other_player.name,
                   birthdate=other_player.birthdate)


class PlayerJSONEncoder(json.JSONEncoder):
    """Encode Player object to JSON
    """
    def default(self, o: Player):
        if isinstance(o, Player):
            return {
                'national_player_id': str(o.national_player_id),
                'surname': o.surname,
                'name': o.name,
                'birthdate': o.birthdate.isoformat()
            }
        else:
            return super().default(o)


class PlayerJSONDecoder(json.JSONDecoder):
    """Decode Player object from JSON
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.obj_hook, *args, **kwargs)

    def obj_hook(self, dct):
        if 'national_player_id' not in dct:
            return dct
        return Player(
            national_player_id=dct['national_player_id'],
            surname=dct['surname'],
            name=dct['name'],
            birthdate=date.fromisoformat(dct['birthdate'])
        )


class PlayerRepository(JSONRepository[Player]):
    """Store player data to a JSON file.
    """
    def __init__(self, filename):
        super().__init__(file=filename, encoder=PlayerJSONEncoder, decoder=PlayerJSONDecoder)

    def find_by_id(self, id: NationalPlayerID | str) -> Player:
        """Finds a player by his National Player ID.
        If parameter is a string, performs a format check first.
        """
        if isinstance(id, NationalPlayerID):
            id_str = str(id)
        elif not is_valid_national_player_id(id):
            # first check ID is valid
            raise ValueError("Invalid ID - expecting Player National ID Format")
        else:
            id_str = id
        return super().find_by_id(id_str)
