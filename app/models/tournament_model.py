from dataclasses import dataclass
from datetime import date, datetime
from app.models.model_baseclasses import EntityABC
import re
from app.adapters.json_storage import JSONRepository
from _collections_abc import Hashable
import json
from app.helpers import validation
from app.models.player_model import Player, NationalPlayerID

class Match:
    """A Match between opposing two players.

    Each player has a score (0, .5 or 1 depending in the outcome).
    Records the match start and end times.
    """
    def __init__(self,
                 player1: tuple[Player, float],
                 player2: tuple[Player, float],
                 start_time: datetime = None,
                 end_time: datetime= None):
        if not isinstance(player1[0], Player):
            raise TypeError(f"Expecting Player object for player1, got {type(player1[0])}")
        if not isinstance(player2[0], Player):
            raise TypeError(f"Expecting Player object for player2, got {type(player1[0])}")
        self.players: tuple[tuple[Player, float]] = ((player1[0], player1[1]), (player2[0], player2[1]))
        self.start_time: datetime = start_time
        self.end_time: datetime = end_time

    def start(self, start_time: datetime = None) -> bool:
        """Start the match.
        Sets the start_time (defaults to now)."""
        pass

    def end(self, winner: NationalPlayerID = None, end_time: datetime = None) -> tuple[tuple[Player, float]]:
        """Ends the match and set the outcome and returns the player scores.
        
        To declare a draw, set winner parameter to None.
        Match end time defaults to curren time.

        Sets the scores basing on the outcome:
        - victorious player receives 1 point,
        - defeated player receieves 0 point,
        - in case of a draw, both player receive 0.5 point.
        """
        pass

    def player_score(self, player_id: NationalPlayerID) -> float:
        """Returns the score of a player for this match,
        or None if the match is still running.
        """
        pass

    def has_ended(self) -> bool:
        """Returns True if this match has ended.
        """
        pass

    def as_dict(self) -> dict:
        """Copies the data of this Macth in a new dict object.
        Useful when dumping to JSON, fo instance.
        Note that only the player_ids gets copied, not the entire player objects. 
        """
        return {
            'start_time': self.start_time.isoformat() if self.start_time is not None else None,
            'end_time': self.end_time.isoformat() if self.end_time is not None else None,
            'players': [[str(score[0].id()), float(score[1]) if score[1] is not None else None] for score in self.players]
        }
    
class Turn:
    """A turn in a tournament.
    """
    def __init__(self, name: str = '', matches: list[Match] = None):
        self.name: str = name
        self.matches: list[Match] = matches

    def setup(self, match_list: list[tuple[Player, Player]]):
        """Setup a turn that has not started yet.
        Parameter is a list of pairs of players.
        """
        pass
    
    def has_started(self) -> bool:
        """A turn has started if all matches are set up and if at least one match has started.
        """
        pass

    def has_ended(self) -> bool:
        """Returns True if all matches have ended.
        """

    def as_dict(self) -> dict:
        """Copies the data of this Turn in a new dict object.
        Useful when dumping to JSON, fo instance.
        """
        return {
            'name': str(self.name),
            'matches': [m.as_dict() for m in self.matches]
        }

class Tournament(EntityABC):
    def __init__(self):
        self.dates: tuple[datetime, datetime] = (None, None)# start and end datetimes
        self.location: str = ''
        self.turns: list[Turn] = []
        self.current_turn: int = None
        self.description: str = ''
        self.participants: list[Player] = []
        self.player_scores: dict[NationalPlayerID, float] = {}

    def add_participant(self, player: Player) -> bool:
        """Adds a player to the tournament.

        Fails if the tournament has already started.
        """
        pass

    def set_turns(self, turn_count: int = 4) -> bool:
        """Sets how many turns this torunament will last (the default is 4).

        Fails if the tournament has already started or ended.
        """
        pass

    def player_score(self, player_id: NationalPlayerID) -> float:
        """Returns the score of one player
        """
        return self.player_scores.get(player_id)

    def ranking_list(self) -> list[tuple[Player, float]]:
        """Returns the current ranking list
        """
        return [(p_id, s) for p_id, s in self.player_scores.items()].sort(key= lambda x: x[1])

    def start_next_turn(self) -> Turn:
        """Starts next Turn.
        
        Returns None on failure.
        Fails if the current Turn is still open or if all turns for this tournament
        have been started.
        """
        pass

    def _make_player_pairs(self) -> list[tuple[Player, Player]]:
        """Makes the player pairs for the next turn, basing on their current scores.
        """
        pass

    def start_date(self) -> datetime:
        return self.dates[0]
    
    def end_date(self) -> datetime:
        return self.dates[1]
    
    def as_dict(self) -> dict:
        """Copies all the data of this tournament into a new dict object.
        Useful when exporting to JSON."""
        return {
            'participants': [str(p.id()) for p in self.participants], # convert players to their National Player ID
            'dates': [(d.isoformat() if d is not None else None) for d in self.dates],
            'location': str(self.location),
            'turns': [t.as_dict() for t in self.turns],
            'current_turn': int(self.current_turn) if self.current_turn is not None else None,
            'description': str(self.description),
            'player_scores': {str(score[0]): float(score[1]) for score in self.player_scores.items()}
        }


###################### JSON Encoders and Decoders ######################

class TournamentJSONEncoder(json.JSONEncoder):
    """Encode Tournament object to JSON
    """
    def default(self, o: Tournament) -> dict:
        if isinstance(o, Tournament):
            return o.as_dict()
        else:
            return super().default(o)

class TournamentJSONDecoder(json.JSONDecoder):
    """Decode Tournament object from JSON
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.obj_hook, *args, **kwargs)

    def obj_hook(self, dct):
        raise NotImplementedError