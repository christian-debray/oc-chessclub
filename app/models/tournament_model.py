from dataclasses import dataclass
from datetime import date, datetime
from app.models.model_baseclasses import EntityABC
from app.adapters.json_storage import JSONRepository
from _collections_abc import Hashable
import json
from app.models.player_model import Player, NationalPlayerID, PlayerRepository
import random
import logging
from pathlib import Path
import uuid

logger = logging.getLogger()


class Match:
    """A Match between opposing two players.

    Each player has a score (0, .5 or 1 depending in the outcome).
    Records the match start and end times.
    """

    def __init__(
        self,
        player1: tuple[Player, float],
        player2: tuple[Player, float],
        start_time: datetime = None,
        end_time: datetime = None,
    ):
        if not isinstance(player1[0], Player):
            raise TypeError(
                f"Expecting Player object for player1, got {type(player1[0])}"
            )
        if not isinstance(player2[0], Player):
            raise TypeError(
                f"Expecting Player object for player2, got {type(player1[0])}"
            )
        self.players: tuple[tuple[Player, float]] = (
            (player1[0], player1[1]),
            (player2[0], player2[1]),
        )
        self.start_time: datetime = start_time
        self.end_time: datetime = end_time

    def player1(self) -> Player:
        return self.players[0][0]

    def player2(self) -> Player:
        return self.players[1][0]

    def start(self, start_time: datetime = None) -> bool:
        """Start the match.
        Sets the start_time (defaults to now).
        Fails if the match has already started."""
        if self.start_time is not None:
            raise ValueError("Match has already started")
        if start_time is None:
            self.start_time = datetime.now()
        else:
            self.start_time = start_time
        return True

    def end(
        self, winner: NationalPlayerID = None, end_time: datetime = None
    ) -> tuple[tuple[Player, float], tuple[Player, float]]:
        """Ends the match and set the outcome and returns the player scores.

        To declare a draw, set winner parameter to None.
        Match end time defaults to curren time.

        Sets the scores basing on the outcome:
        - victorious player receives 1 point,
        - defeated player receieves 0 point,
        - in case of a draw, both player receive 0.5 point.

        A match that has not started can't be ended (this raises an Exception),
        but it is still possible to change the outcome of a match that has
        already ended (in order to fix a mistake, for instance).
        """
        if not self.has_started():
            raise Exception("Can't end a match that has not started yet.")
        if end_time is None and self.end_time is None:
            self.end_time = datetime.now()
        elif end_time is not None:
            if end_time <= self.start_time:
                raise ValueError("Trying to end a match with inconsistent end time.")
            self.end_time = end_time

        if winner is None:
            # draw: 0.5 for each player.
            self.players = ((self.player1(), 0.5), (self.player2(), 0.5))
        elif self.player1().id() == winner:
            self.players = ((self.player1(), 1.0), (self.player2(), 0))
        elif self.player2().id() == winner:
            self.players = ((self.player1(), 0.0), (self.player2(), 1.0))
        else:
            raise KeyError("Trying to end a match with wrong Player ID.")

        return self.scores()

    def player_score(self, player_id: NationalPlayerID) -> float:
        """Returns the score of a player for this match,
        or None if the match is still running.
        If parameter is None, returns the score of both players.
        """
        if player_id is None:
            return self.players
        elif player_id == self.player1().id():
            return self.players[0][1]
        elif player_id == self.player2().id():
            return self.players[1][1]
        else:
            raise KeyError("Trying to retrieve match score with a wrong Player ID.")

    def scores(self) -> tuple[tuple[Player, float], tuple[Player, float]]:
        """Returns the score for this match."""
        return self.players

    def has_started(self) -> bool:
        """Returns True if this match has started.
        (it may have also ended if True...)
        """
        return self.start_time is not None

    def has_ended(self) -> bool:
        """Returns True if this match has ended."""
        return self.end_time is not None

    def asdict(self) -> dict:
        """Copies the data of this Macth in a new dict object.
        Useful when dumping to JSON, fo instance.
        Note that only the player_ids gets copied, not the entire player objects.
        """
        return {
            "start_time": (
                self.start_time.isoformat() if self.start_time is not None else None
            ),
            "end_time": (
                self.end_time.isoformat() if self.end_time is not None else None
            ),
            "players": [
                [str(score[0].id()), float(score[1]) if score[1] is not None else None]
                for score in self.players
            ],
        }


class Round:
    """A Round in a tournament."""

    def __init__(self, name: str = "", matches: list[Match] = None):
        self.name: str = name
        self.matches: list[Match] = matches or []

    def setup(self, match_list: list[tuple[Player, Player]]):
        """Setup a Round that has not started yet.
        Parameter is a list of pairs of players.
        """
        self.matches = []
        for pair in match_list:
            self.matches.append(Match(player1=(pair[0], 0.0), player2=(pair[1], 0.0)))

    def has_started(self) -> bool:
        """A Round has started if all matches are set up."""
        return len(self.matches) > 0

    def has_ended(self) -> bool:
        """Returns True if all matches have ended."""
        return 0 == len(list(filter(lambda x: x.has_ended() is False, self.matches)))

    def find_player_match(self, player_id: NationalPlayerID) -> Match:
        """Finds match with player player_id"""
        for m in self.matches:
            if player_id in [m.player1().id(), m.player2().id()]:
                return m
        return None

    def asdict(self) -> dict:
        """Copies the data of this Round in a new dict object.
        Useful when dumping to JSON, fo instance.
        """
        return {"name": str(self.name), "matches": [m.asdict() for m in self.matches]}


@dataclass
class TournamentMetaData(EntityABC):
    """Tournament meta data"""

    tournament_id: str = None
    start_date: date = None
    end_date: date = None
    location: str = ""
    description: str = ""
    data_file: str = ""
    round_count: int = 4
    status: str = "open"

    def set_id(self, id: Hashable):
        self.tournament_id = id

    def id(self) -> Hashable:
        return self.tournament_id

    def asdict(self) -> dict:
        return {
            "tournament_id": str(self.tournament_id),
            "start_date": (
                self.start_date.isoformat() if self.start_date is not None else None
            ),
            "end_date": (
                self.end_date.isoformat() if self.end_date is not None else None
            ),
            "location": str(self.location),
            "description": str(self.description),
            "data_file": str(self.data_file),
            "round_count": self.round_count,
            "status": self.status,
        }


class Tournament:
    def __init__(
        self,
        metadata: TournamentMetaData,
        participants: list[Player] = None,
        rounds: list[Round] = None,
        current_round: int = None,
    ):
        """Create a Tournament.

        - metadata:
        - particpants:
        - rounds:
        - current_round:
        """
        if rounds is not None and len(rounds) != metadata.round_count:
            raise ValueError("Round count mismatch.")
        self.metadata: TournamentMetaData = metadata
        self.rounds: list[Round] = rounds or [None for _ in range(metadata.round_count)]
        self.current_round_idx: int = current_round
        self.participants: list[Player] = participants or []

        # utility: keep track of oppenents met during the tournament to avoid
        # repetitive matches.
        self._player_opponents: dict[NationalPlayerID, list[NationalPlayerID]] = {}
        for p in self.participants:
            self._player_opponents[p.id()] = []
        # utility
        self.player_ranks: dict[NationalPlayerID, tuple[int, float]] = {}

        # update _player_opponents_data
        for rnd in self.rounds:
            if rnd is None:
                continue
            for mtch in rnd.matches:
                self._player_opponents[mtch.player1().id()].append(mtch.player2().id())
                self._player_opponents[mtch.player2().id()].append(mtch.player1().id())

        self.update_score_board()
        self.update_end_date()
        if participants and self.has_started() and len(participants) % 2 > 0:
            raise ValueError(
                "Running or Ended Tournament require even number of participants; uneven list given."
            )

    def id(self) -> str:
        return self.metadata.id()

    def set_id(self, new_id: str):
        self.metadata.set_id(new_id)

    def add_participant(self, player: Player) -> bool:
        """Adds a player to the tournament.

        Fails if the tournament has already started.
        """
        if self.has_started():
            raise Exception(
                "Trying to add a participant when tournament has already started."
            )
        if player not in self.participants:
            self.participants.append(player)
            self._player_opponents[player.id()] = []
            return True
        else:
            return False

    def player_is_registered(self, player_id: str) -> bool:
        """Checks if a player is already registered in this tournament."""
        return player_id in self._player_opponents

    def set_rounds(self, round_count: int = 4) -> bool:
        """Sets how many rounds this tournament will last (the default is 4).

        Fails if the tournament has already started or ended.
        """
        if self.has_started():
            raise Exception(
                "Trying to changing Round count when tournament has aldready started."
            )
        round_count = int(round_count)
        if round_count <= 0:
            raise ValueError("Invalid rounds count.")
        self.metadata.round_count = round_count
        self.rounds = [None for _ in range(self.metadata.round_count)]

    def set_start_date(self, new_date: date):
        """Sets the start date. Fails if the tournament has started."""
        if self.has_started():
            raise Exception(
                "Trying to change start date when tournament has aldready started."
            )
        self.metadata.start_date = new_date

    def set_location(self, new_location: str):
        """Set the location. Fails if the tournament has already started."""
        if self.has_started():
            raise Exception(
                "Trying to change location when tournament has aldready started."
            )
        self.metadata.location = new_location

    def set_description(self, new_description: str):
        """Sets the description."""
        self.metadata.description = new_description

    def has_started(self) -> bool:
        """Return True if tournament has started."""
        return self.rounds[0] is not None and self.rounds[0].has_started()

    def has_ended(self) -> bool:
        """Return True if tournament has ended."""
        return self.rounds[-1] is not None and self.rounds[-1].has_ended()

    def status(self) -> str:
        """Returns a string representation of this tournament's current status:
        'open', 'started', 'ended'.
        """
        if not self.has_started():
            return "open"
        if self.has_started and not self.has_ended():
            return "running"
        if self.has_ended():
            return "ended"
        return "(status unknown)"

    def update_end_date(self):
        """Update the end date of this tournament."""
        if self.has_ended() and self.metadata.end_date is None:
            # find latest endtime in last Round
            end_datetime = min([m.end_time for m in self.rounds[-1].matches])
            self.metadata.end_date = date(
                year=end_datetime.year, month=end_datetime.month, day=end_datetime.day
            )
        self.metadata.status = self.status()

    def player_score(self, player_id: NationalPlayerID) -> float:
        """Returns the score of one player"""
        total = 0.0
        for t in self.rounds:
            if t is not None and t.has_started():
                m = t.find_player_match(player_id=player_id)
                total += m.player_score(player_id) or 0.0
        return total

    def ranking_list(self) -> list[tuple[NationalPlayerID, int, float]]:
        """Returns the current ranking list"""
        if self.has_started():
            return [
                (pid, rank, score) for (pid, (rank, score)) in self.player_ranks.items()
            ]
        else:
            return [(p, 1, 0.0) for p in self.participants]

    def can_start(self) -> bool:
        """Return True if calling the start_next_round is valid."""
        if self.current_round_idx == len(self.rounds) - 1:
            # Tournament reached the last Round
            return False
        if self.current_round() is not None and not self.current_round().has_ended():
            # Current Round has not ended
            return False
        if self.has_ended():
            # Tournament has ended.
            return False
        if len(self.participants) % 2 > 0:
            # Even participant number required.
            return False
        return True

    def start_next_round(self, player_pairs: list[tuple[Player, Player]] = None) -> Round:
        """Fails if the current Round is still open or if the last Round
        has started or ended.
        """
        if self.current_round_idx == len(self.rounds) - 1:
            raise Exception("Trying to start new Round after last Round.")
        if (self.current_round_idx or 0) > 0 and not self.rounds[
            self.current_round_idx
        ].has_ended():
            raise Exception("Trying to start new Round when current Round has not ended.")
        if self.has_ended():
            raise Exception("Trying to start new Round after tournament has ended.")
        if len(self.participants) % 2 > 0:
            raise ValueError("Even participant number required.")

        self.current_round_idx = (
            self.current_round_idx + 1 if self.current_round_idx is not None else 0
        )

        # update start date with actual date where first Round got started.
        if self.current_round_idx == 0:
            self.metadata.start_date = date.today()
        self.rounds[self.current_round_idx] = Round(
            name=f"Round {self.current_round_idx + 1}"
        )
        if player_pairs is None:
            player_pairs = self._make_player_pairs()
        self.rounds[self.current_round_idx].setup(player_pairs)
        for p1, p2 in player_pairs:
            self._player_opponents[p1.id()].append(p2.id())
            self._player_opponents[p2.id()].append(p1.id())
        return self.current_round()

    def current_round(self) -> Round:
        """Returns the current Round, if any.
        Returns None if tournament has ended or not started.
        """
        if self.has_ended() or not self.has_started():
            return None
        return self.rounds[self.current_round_idx]

    def pending_matches(self) -> list[tuple[int, Match]]:
        """Returns a list of pending matches and their index in the current round."""
        if current_round := self.current_round():
            if not current_round.has_started():
                return None
            if current_round.has_ended():
                return None
            return [
                (m, match)
                for m, match in enumerate(current_round.matches)
                if not match.has_started()
            ]
        else:
            return None

    def has_pending_matches(self) -> bool:
        """Returns True if matches are still waiting to be started
        in this tournament's current round.
        """
        if current_round := self.current_round():
            if not current_round.has_started():
                return False
            if current_round.has_ended():
                return False
            for m in current_round.matches:
                if not m.has_started():
                    return True
        return False

    def start_a_match(self, match_index: int, start_time: datetime = None) -> Match:
        """Starts a match in the current Round.
        Returns the started match if succesful, None otherwise.
        """
        if current_round := self.current_round():
            if not current_round.has_started():
                return None
            if current_round.has_ended():
                return None
            current_round.matches[match_index].start(start_time=start_time)
            #
            # if the tournament just started, also update the start date
            #
            if self.current_round_idx == 0:
                if self.start_date().strftime("%Y-%m-%d") != start_time.strftime("%Y-%m-%d"):
                    self.metadata.start_date = date.fromisoformat(start_time.strftime("%Y-%m-%d"))
            return current_round.matches[match_index]
        else:
            return None

    def running_matches(self) -> list[tuple[int, Match]]:
        """Returns a list of pending matches and their index in the current round."""
        if current_round := self.current_round():
            if not current_round.has_started():
                return None
            if current_round.has_ended():
                return None
            return [
                (m, match)
                for m, match in enumerate(current_round.matches)
                if (match.has_started() and not match.has_ended())
            ]
        else:
            return None

    def has_running_matches(self) -> bool:
        """Returns True if macthes are waiting to be ended in this tournament's curren round."""
        if current_round := self.current_round():
            if not current_round.has_started():
                return False
            if current_round.has_ended():
                return False
            for match in current_round.matches:
                if match.has_started() and not match.has_ended():
                    return True
        else:
            return False

    def end_a_match(
        self, match_index: int, winner_id: str, end_time: datetime = None
    ) -> tuple[tuple[Player, float], tuple[Player, float]]:
        """Ends a match in the current Round.
        Returns the result, None otherwise.
        """
        if current_round := self.current_round():
            if not current_round.has_started():
                return None
            if current_round.has_ended():
                return None
            match = current_round.matches[match_index]
            result = match.end(winner=winner_id, end_time=end_time)
            self.update_end_date()
            self.update_score_board()
            return result
        else:
            return None

    def update_score_board(self) -> list[tuple[Player, int, float]]:
        """Maintain a scores board and score ranks."""
        score_board: dict[float, list[Player]] = {}
        scores: list[float] = []
        player_scores = {}
        for p in self.participants:
            score = self.player_score(p.id())
            player_scores[p.id()] = score
            if score not in score_board:
                score_board[score] = [p]
                scores.append(score)
            else:
                score_board[score].append(p)

        scores.sort(reverse=True)
        rank_list = []
        for s_idx in range(len(scores)):
            score = scores[s_idx]
            for p in score_board[score]:
                self.player_ranks[p.id()] = (s_idx + 1, score)
                rank_list.append((p, s_idx + 1, score))
        return rank_list

    def player_rank(self, player_id: NationalPlayerID) -> int:
        """Rank start from 1 (highest scores).
        The higher the rank, the lower the score.
        """
        return self.player_ranks.get(player_id, (None, None))[0]

    def _make_player_pairs(self) -> list[tuple[Player, Player]]:
        """Makes the player pairs for the next Round, basing on their current scores.

        - Avoid repeated matches between rounds.
        - Randomize pairs whenever possible.
        """
        if not self.has_started():
            player_order = [p for p in self.participants]
            random.shuffle(player_order)
            return [
                (player_order[p], player_order[p + 1])
                for p in range(0, len(player_order), 2)
            ]

        logger.debug(f"Making player pairs for Round {self.current_round_idx}...")
        # we just base on ranking list to start with
        ranking_list = self.update_score_board()
        recurring_matches: list[int] = []
        pairs: list[tuple[Player, Player]] = []
        # make the pairs using a naive approach first,
        # simply by following the ranking list.
        for r in range(len(ranking_list)):
            player = ranking_list[r][0]
            if r % 2 == 0:
                matching_player = ranking_list[r + 1][0]
                logger.debug(
                    f"Match {len(pairs)}: {player.id()} vs {matching_player.id()}, \
                             quality = {self._can_play(player.id(), matching_player.id())}"
                )
                pairs.append((player, matching_player))
                if matching_player.id() in self._player_opponents.get(player.id()):
                    # these two players already met before, we'll try to fix this later
                    # (see below)
                    recurring_matches.append(len(pairs) - 1)
                    logger.debug(
                        f"  ! Recurring pair at match {len(pairs) - 1}: ({player.id()}, \
                                 {matching_player.id()})"
                    )

        if len(recurring_matches) > 0:
            logger.debug(f"Try to solve {len(recurring_matches)} recurring matches...")

            # try to solve recurring matches by swaping participants of compatible matches
            # given the player pairs (a,b) and (c,d)
            # check if ((a,d), (b,c)) or ((a,c), (b,d)) are acceptable solutions.
            while len(recurring_matches) > 0:
                i = recurring_matches.pop()
                player1 = pairs[i][0]
                player2 = pairs[i][1]
                current_quality = self._can_play(player1.id(), player2.id())
                if current_quality == 1:
                    logger.debug(f"Match {i} is already resolved, skip.")
                    continue
                logger.debug(
                    f"Try to solve match {i} ({player1.id()} vs {player2.id()}, \
                             quality={round(current_quality, 2)})"
                )
                # limit search to immediate vicinity
                for alt_i in [
                    j
                    for j in [i - 1, i + 1, i - 2, i + 2]
                    if j != i and j > 0 and j < len(pairs)
                ]:
                    player3 = pairs[alt_i][0]
                    player4 = pairs[alt_i][1]
                    logger.debug(f"   try {alt_i} ({player3.id()} vs {player4.id()})")
                    # (player1, player3) + (player2, player4)
                    if (
                        self._can_play(player1.id(), player3.id()) > current_quality
                        and self._can_play(player2.id(), player4.id()) > current_quality
                    ):
                        # we can safely swap players
                        pairs[i] = (player1, player3)
                        pairs[alt_i] = (player2, player4)
                        logger.debug(
                            f" => Found a solution: swap with match {alt_i}, \
                                    (player1, player3) + (player2, player4)"
                        )
                        break
                    # (player1, player4) + (player2, player3)
                    elif (
                        self._can_play(player1.id(), player4.id()) > current_quality
                        and self._can_play(player2.id(), player3.id()) > current_quality
                    ):
                        pairs[i] = (player1, player4)
                        pairs[alt_i] = (player2, player3)
                        logger.debug(
                            f" => Found a solution: swap with match {alt_i}, \
                                    (player1, player4) + (player2, player3)"
                        )
                        break
        logger.debug(
            "Pairs = " + ", ".join([f"({p1.id()}, {p2.id()})" for p1, p2 in pairs])
        )
        return pairs

    def _can_play(
        self, player1_id: NationalPlayerID, player2_id: NationalPlayerID
    ) -> float:
        """Check if two players may play together.
        Return 0 if the players ranks ar incompatible.
        returns an float value above 0 otherwise.
        value is below 0 if both players have already played before.
        """
        player1_rank = self.player_rank(player1_id)
        player2_rank = self.player_rank(player2_id)

        if player1_rank in [player2_rank - 1, player2_rank, player2_rank + 1]:
            encounters = len(
                [
                    i
                    for i, x in enumerate(self._player_opponents.get(player2_id, []))
                    if x == player1_id
                ]
            )
            return 1 / (1 + encounters)
        else:
            return 0

    def start_date(self) -> date:
        return self.metadata.start_date

    def end_date(self) -> date:
        return self.metadata.end_date

    def asdict(self) -> dict:
        """Copies all the data of this tournament into a new dict object.
        Useful when exporting to JSON.
        Player objects are converted to their National Player ID.
        """
        self.update_end_date()
        return {
            "tournament_id": self.id(),
            "metadata": self.metadata.asdict(),
            "participants": [str(p.id()) for p in self.participants],
            "current_round_idx": (
                int(self.current_round_idx)
                if self.current_round_idx is not None
                else None
            ),
            "rounds": [t.asdict() if t is not None else None for t in self.rounds],
        }


class TournamentMetaDataJSONEncoder(json.JSONEncoder):
    """Encode Tournament metadata object to JSON"""

    def default(self, o: TournamentMetaData) -> dict:
        if isinstance(o, TournamentMetaData):
            return o.asdict()
        else:
            return super().default(o)


class TournamentMetaDataJSONDecoder(json.JSONDecoder):
    """Decode a Tournament metadata"""

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.obj_hook, *args, **kwargs)

    def obj_hook(self, dct):
        if "tournament_id" not in dct:
            return dct
        return TournamentMetaData(
            tournament_id=dct["tournament_id"],
            start_date=(
                date.fromisoformat(dct["start_date"])
                if dct["start_date"] is not None
                else None
            ),
            end_date=(
                date.fromisoformat(dct["end_date"])
                if dct["end_date"] is not None
                else None
            ),
            location=dct["location"],
            description=dct["description"],
            data_file=dct["data_file"],
            round_count=int(dct["round_count"]),
            status=dct["status"],
        )


class TournamentRepository:
    """Tournament metadata is stored in data/tournaments/metadata.json,
    which stores an index of all known tournaments and the json files with tournament data.
    data/tournaments/tournament_<tournament_id>.json stores the participants,
    Round and match data for tournament tournament_id.

    """

    def __init__(self, metadata_file: str | Path, player_repo: PlayerRepository):
        self._tournament_dir = Path(Path(metadata_file).parent).resolve()
        self._metadata_repo = JSONRepository(
            file=metadata_file,
            encoder=TournamentMetaDataJSONEncoder,
            decoder=TournamentMetaDataJSONDecoder,
        )
        # link to json file storing tournament details
        self.player_repo: PlayerRepository = player_repo
        self._tournament_data: dict[str, Tournament] = {}

    def list_tournament_meta(self) -> list[TournamentMetaData]:
        return self._metadata_repo.list_all()

    def find_tournament_metadata(self, **filters) -> list[TournamentMetaData]:
        return self._metadata_repo.find_many(**filters)

    def find_tournament_metadata_by_id(self, tournament_id) -> TournamentMetaData:
        return self._metadata_repo.find_by_id(tournament_id)

    def add_tournament_metadata(self, metadata: TournamentMetaData):
        if not metadata.id():
            metadata.set_id(self.gen_tournament_id())
        self._metadata_repo.add(metadata)

    def store_tournament(self, tournament: Tournament) -> bool:
        """Store a tournament.
        Tournament metadata is stored in a unique file with all other tournament metadata objects,
        while tournament rounds data is stored in separate files in the data/tournaments folder.
        Tournament Round data files are named after the tournament id.
        """
        if not tournament.id() or not tournament.metadata.id():
            tournament.set_id(self.gen_tournament_id())
        if not tournament.metadata.data_file:
            tournament.metadata.data_file = tournament.id() + ".json"
        if not tournament.id() in self._tournament_data:
            self._tournament_data[tournament.id()] = tournament
        if not self.find_tournament_metadata_by_id(tournament.metadata.id()):
            self._metadata_repo.add(tournament.metadata)
        else:
            self._metadata_repo.update(tournament.metadata)
        self._metadata_repo.commit_changes()
        tournament_dump_data = tournament.asdict()
        o_file = Path(self._tournament_dir, tournament.metadata.data_file)
        with open(o_file, "w", encoding="utf8") as json_file:
            json.dump(tournament_dump_data, json_file, indent=True)
        return True

    def gen_tournament_id(self) -> str:
        """Generates a UUID to identify a tournament."""
        return str(uuid.uuid4())

    def find_tournament_by_id(self, tournament_id) -> Tournament:
        """Find a tournament with full data by its id."""
        if tournament_id in self._tournament_data:
            return self._tournament_data.get(tournament_id)
        else:
            return self.load_tournament(tournament_id)

    def load_tournament(self, tournament_id) -> Tournament:
        """Loads a tournament from file (if found)"""
        meta = self.find_tournament_metadata_by_id(tournament_id=tournament_id)
        if not meta:
            return None
        tournament_file = Path(self._tournament_dir, meta.data_file)
        if not tournament_file.exists():
            # Empty tournament
            self._tournament_data[tournament_id] = Tournament(metadata=meta)
            return self._tournament_data[tournament_id]

        # load data from a JSON:
        with open(tournament_file, "r", encoding="utf8") as json_file:
            data: dict = json.load(json_file)
        if data.get("tournament_id") != tournament_id:
            raise KeyError(
                "Unexpected or missing tournament id while loading tournament data file."
            )
        current_round = (
            int(data.get("current_round_idx"))
            if data.get("current_round_idx") is not None
            else None
        )
        # otherwise, load participants and Round data:
        participants_index = self._load_participants(data.get("participants"))
        rounds = []
        for t in data.get("rounds"):
            if t is None:
                rounds.append(None)
            else:
                rounds.append(
                    self._load_round(data=t, participants_index=participants_index)
                )
        self._tournament_data[tournament_id] = Tournament(
            metadata=meta,
            participants=list(participants_index.values()),
            rounds=rounds,
            current_round=current_round,
        )
        return self._tournament_data[tournament_id]

    def _load_round(self, data: dict, participants_index: dict[str, Player]):
        """Load a Round data from a dict."""
        if not data:
            return None
        round_name = data.get("name", "")
        matches_data: list[dict] = data.get("matches", [])
        matches: list[Match] = []
        for m_d in matches_data:
            start_time = None
            if d := m_d.get("start_time"):
                start_time = datetime.fromisoformat(d)
            end_time = None
            if d := m_d.get("end_time"):
                end_time = datetime.fromisoformat(d)
            player_data = m_d.get("players")
            player1 = participants_index.get(player_data[0][0])
            player1_score = float(player_data[0][1])
            player2 = participants_index.get(player_data[1][0])
            player2_score = float(player_data[1][1])
            matches.append(
                Match(
                    player1=(player1, player1_score),
                    player2=(player2, player2_score),
                    start_time=start_time,
                    end_time=end_time,
                )
            )
        return Round(name=round_name, matches=matches)

    def _load_participants(self, data: list[str]) -> dict[NationalPlayerID, Player]:
        """Load participants data from a dict."""
        player_list = {}
        for player_id_str in data:
            if pl := self.player_repo.find_by_id(player_id_str):
                if player_id_str in player_list:
                    raise KeyError("Duplicate Player ID in participants data")
                player_list[player_id_str] = pl
            else:
                raise KeyError(f"Player ID not found in repository: '{player_id_str}'")
        return player_list


if __name__ == "__main__":
    from pathlib import Path
    from app import APPDIR

    logging.basicConfig(filename=Path(APPDIR, "debug.log"), level=logging.DEBUG)
    test_path = Path(APPDIR.parent, "tests").resolve()
    import sys

    sys.path.append(str(test_path.resolve()))
    from tests.datamodel.test_tournament_model import utils

    test_datadir = Path(test_path, "tmp", "data")
    test_p_file = Path(test_datadir, "players.json")
    test_t_data_dir = Path(test_datadir, "tournaments")
    test_meta_file = Path(test_t_data_dir, "test_tournament_metadata.json")

    player_repo = PlayerRepository(test_p_file)
    tournament_repo = TournamentRepository(
        metadata_file=test_meta_file, player_repo=player_repo
    )
    tournament_id = random.choice(["tournament_test", None, None])
    tournament = None
    if tournament_id:
        tournament = tournament_repo.find_tournament_by_id(tournament_id=tournament_id)
        logger.info(f"Re-using tournament id {tournament_id}")
    else:
        logger.info("New tournament")
    if tournament is None:
        tournament = Tournament(
            TournamentMetaData(
                tournament_id=tournament_id,
                start_date=date.fromisoformat("2024-01-01"),
                location="paris",
                round_count=6,
            )
        )
        logger.info("Storing Tournament data...")
        tournament_repo.store_tournament(tournament)
        logger.info(f"Tournament data stored with id = {tournament.id()}")
        tournament_id = tournament.id()
        for _ in range(10):
            player = utils.make_random_player()
            player_repo.add(player)
            tournament.add_participant(player)
            tournament_repo.store_tournament(tournament)
        logger.info("Storing particpants data...")
        player_repo.commit_changes()

    if not tournament.has_started():
        for t in range(tournament.metadata.round_count - 1):
            logger.debug("starting next Round...")
            current_round = tournament.start_next_round()
            print(f"starting {current_round.name}...")
            logger.debug(f"  Round {current_round.name} matches:")
            for m in current_round.matches:
                winner = random.choice([None, m.player1().id(), m.player2().id()])
                logger.debug(
                    f"    playing match {m.player1().id()} vs {m.player2().id()}..."
                )
                m.start()
                logger.debug(f"      => winner: {winner}")
                scores = m.end(
                    end_time=datetime.fromtimestamp(m.start_time.timestamp() + 1800),
                    winner=winner,
                )
            logger.debug(f"Round {current_round.name} ended.")
            tournament.update_score_board()
            ranking = tournament.ranking_list()
            ranking.sort(key=lambda x: x[1])
            ranking_str = ", ".join(
                [f"[{str(x[0])}: #{x[1]} ({x[2]})]" for x in ranking]
            )
            logger.debug("Ranking after Round: ", ranking_str)
            logger.debug("Ranking after Round:\n" + ranking_str)
            logger.debug("Write to file...")
            tournament.update_end_date()
            tournament_repo.store_tournament(tournament)
        print("Done")
        assert tournament.has_ended() is False
        del tournament_repo
        del tournament

    tournament_repo2 = TournamentRepository(
        metadata_file=test_meta_file, player_repo=player_repo
    )
    tournament2 = tournament_repo2.find_tournament_by_id(tournament_id=tournament_id)
    assert tournament2 is not None
    assert tournament2.has_started()
    assert not tournament2.has_ended()
    tournament2.metadata.description = f"some random description: {utils.randstring(20)}\n\
        inserted at {datetime.now().isoformat()}"
    tournament_repo2.store_tournament(tournament2)
    if not tournament2.current_round().has_started():
        tournament2.start_next_round()
