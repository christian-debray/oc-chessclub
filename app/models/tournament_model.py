from dataclasses import dataclass, asdict
from datetime import date, datetime
from app.models.model_baseclasses import EntityABC
import re
from app.adapters.json_storage import JSONRepository
from _collections_abc import Hashable
import json
from app.helpers import validation
from app.models.player_model import Player, NationalPlayerID, PlayerRepository

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

    def player1(self) -> Player:
        return self.players[0][0]
    
    def player2(self) -> Player:
        return self.players[1][0]

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

    def find_player_match(self, player_id: NationalPlayerID) -> Match:
        """Finds match with player player_id
        """
        pass

    def as_dict(self) -> dict:
        """Copies the data of this Turn in a new dict object.
        Useful when dumping to JSON, fo instance.
        """
        return {
            'name': str(self.name),
            'matches': [m.as_dict() for m in self.matches]
        }
    
@dataclass
class TournamentMetaData(EntityABC):
    """Tournament meta data
    """
    tournament_id: str = None
    start_date: date = None
    end_date: date = None
    location: str = ''
    description: str = ''
    data_file: str = ''
    turn_count: int = 4

    def set_id(self, id: Hashable):
        self.tournament_id = id

    def id(self) -> Hashable:
        return self.tournament_id

    def asdict(self) -> dict:
        return {
            "tournament_id": str(self.tournament_id),
            "start_date": self.start_date.isoformat() if self.start_date is not None else None,
            "end_date": self.end_date.isoformat() if self.end_date is not None else None,
            "location": str(self.location),
            "description": str(self.description),
            "data_file": str(self.data_file)
        }

class Tournament():
    def __init__(self, metadata: TournamentMetaData):
        self.metadata: TournamentMetaData = metadata
        self.turns: list[Turn] = [None for _ in range(metadata.turn_count)]
        self.current_turn: int = None
        self.participants: list[Player] = []
   
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
        total = 0
        for t in self.turns:
            if t is not None:
                m = t.find_player_match(player_id=player_id)
                total += (m.player_score(player_id) or 0)
        return total

    def ranking_list(self) -> list[tuple[Player, float]]:
        """Returns the current ranking list
        """
        return [(p, self.player_score(p.id())) for p in self.participants].sort(key= lambda x: x[1])

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

    def start_date(self) -> date:
        return self.metadata.start_date
    
    def end_date(self) -> date:
        return self.metadata.end_date
    
    def as_dict(self) -> dict:
        """Copies all the data of this tournament into a new dict object.
        Useful when exporting to JSON."""
        return {
            'metadata': self.metadata.asdict(),
            'participants': [str(p.id()) for p in self.participants], # convert players to their National Player ID
            'turns': [t.as_dict() if t is not None else None for t in self.turns],
            'current_turn': int(self.current_turn) if self.current_turn is not None else None
        }

class TournamentJSONEncoder(json.JSONEncoder):
    """Encode Tournament object to JSON
    """
    def default(self, o: Tournament) -> dict:
        if isinstance(o, Tournament):
            return o.as_dict()
        else:
            return super().default(o)

class TournamentRepository(JSONRepository):
    def __init__(self, file, player_repo: PlayerRepository):
        super().__init__(file, TournamentJSONEncoder, json.JSONDecoder)
        self.player_repo: PlayerRepository = player_repo
