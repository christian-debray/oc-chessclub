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
    
class Turn:

    def __init__(self):
        self.name: str
        self.matches: list[Match] = None

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

class Tournament(EntityABC):
    def __init__(self):
        self.dates: tuple[datetime, datetime] = (None, None)# start and end datetimes
        self.location: str = ''
        self.turns: list = []
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


###################### JSON Encoders and Decoders ######################

class MatchJSONEncoder(json.JSONEncoder):
    """Encode Turn data to JSON"""
    def default(self, o: Match) -> dict:
        """Encode a Match object to JSON.
        """
        if isinstance(o, Match):
            return {
                'start_time': o.start_time.isoformat() if o.start_time is not None else None,
                'end_time': o.end_time.isoformat() if o.end_time is not None else None,
                'players': [[str(score[0].id()), float(score[1])] for score in o.players]
            }
        else:
            return super().default(o)


class MatchJSONDecoder(json.JSONDecoder):
    """Decode Turn data from JSON"""
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.obj_hook, *args, **kwargs)

    def obj_hook(self, dct):
        raise NotImplementedError

class TurnJSONEncoder(json.JSONEncoder):
    """Encode Turn data to JSON"""
    def default(self, o: Turn) -> dict:
        if isinstance(o, Turn):
            return {
                'name': str(o.name) ,#str
                'matches': [json.dumps(m, cls=MatchJSONEncoder) for m in o.matches] #list[Match] = None
            }
        else:
            return super().default()

class TurnJSONDecoder(json.JSONDecoder):
    """Decode Turn data from JSON"""
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.obj_hook, *args, **kwargs)

    def obj_hook(self, dct):
        raise NotImplementedError

class TournamentJSONEncoder(json.JSONEncoder):
    """Encode Tournament object to JSON
    """
    def default(self, o: Tournament) -> dict:
        if isinstance(o, Tournament):
            return {
                'participants': [str(p.id()) for p in o.participants], # convert players to their National Player ID
                'dates': [(d.isoformat() if d is not None else None) for d in o.dates],
                'location': str(o.location),
                'turns': [json.dumps(t, cls= TurnJSONEncoder) for t in o.turns],
                'current_turn': int(o.current_turn) if o.current_turn is not None else None,
                'description': str(o.description),
                'player_scores': {str(score[0]): float(score[1]) for score in o.player_scores.items()}
            }
        else:
            return super().default(o)

class TournamentJSONDecoder(json.JSONDecoder):
    """Decode Tournament object from JSON
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.obj_hook, *args, **kwargs)

    def obj_hook(self, dct):
        raise NotImplementedError