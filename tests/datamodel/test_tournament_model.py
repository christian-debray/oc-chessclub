import unittest
import tests
import app.models.player_model as player_model
import app.models.tournament_model as tournament_model
from datetime import date, datetime
from pathlib import Path
import json
import random

class utils:
    @staticmethod
    def randdigits(n: int, min: int = 0, max: int = 9) -> str:
        """Generates a random numeric string."""
        t = ""
        for _ in range(n):
            t += str(random.randint(min, max))
        return t

    @staticmethod
    def randstring(len: int) -> str:
        """Generates a random string with ASCII capital letters."""
        return "".join([chr(random.randint(65, 90)) for _ in range(len)])

    @staticmethod
    def rand_player_id() -> str:
        """Generates a random national player ID string"""
        return utils.randstring(2) + utils.randdigits(5)
    
    @staticmethod
    def rand_date() -> str:
        """Generates a random date string in ISO format"""
        y = random.randint(1960, 2010)
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        return f"{y}-{m:0>2}-{d:0>2}"
        
    @staticmethod
    def make_random_player() -> player_model.Player:
        return player_model.Player(
            national_player_id= player_model.NationalPlayerID(utils.rand_player_id()),
            name=utils.randstring(8).capitalize(),
            surname=utils.randstring(8).capitalize(),
            birthdate=date.fromisoformat(utils.rand_date()))

    @staticmethod
    def make_matches() -> list[tournament_model.Match]:
        """Makes a list of matches with random players, in various situations:
        match 0 ended with a draw
        match 1 was won by player 1
        match 2 has started but not ended
        match 2 has not started
        """
        matches: list[tournament_model.Match] = [
                    tournament_model.Match(player1 = (utils.make_random_player(), 0.5),
                                            player2 = (utils.make_random_player(), 0.5),
                                            start_time= datetime.fromisoformat("2024-05-02 15:24:30"),
                                            end_time= datetime.fromisoformat("2024-05-02 15:44:30")),
                    tournament_model.Match(player1 = (utils.make_random_player(), 1),
                                            player2 = (utils.make_random_player(), 0),
                                            start_time= datetime.fromisoformat("2024-05-02 15:34:25"),
                                            end_time= datetime.fromisoformat("2024-05-02 15:57:12")),
                    tournament_model.Match(player1 = (utils.make_random_player(), None),
                                            player2 = (utils.make_random_player(), None),
                                            start_time= datetime.fromisoformat("2024-05-02 15:41:02")),
                    tournament_model.Match(player1 = (utils.make_random_player(), None),
                                            player2 = (utils.make_random_player(), None)),
                ]
        return matches

    @staticmethod
    def make_tournament() -> tournament_model.Tournament:
        tournament_meta = tournament_model.TournamentMetaData(
            tournament_id= utils.randstring(5),
            start_date= datetime.fromisoformat("2024-05-02 15:00:00"),
            end_date= None,
            location = utils.randstring(12),
            description= " ".join([utils.randstring(random.randint(2, 12)) for _ in range(10)]),
            data_file= utils.randstring(8) + ".json",
            turn_count= 4
        )
        tournament = tournament_model.Tournament(tournament_meta)
        match_list = utils.make_matches()
        tournament.turns[0] = tournament_model.Turn("test turn", matches= match_list)
        for m in match_list:
            tournament.participants.append(m.player1())
            tournament.participants.append(m.player2())
        return tournament

class TestTournamentJSON(unittest.TestCase):
    """Test JSON encoding and decoding of Tournament entities
    """
    def test_match_as_dict(self):
        """Dump a valid match to dict without failure, and check data is consistent."""
        p1 = utils.make_random_player()
        p2 = utils.make_random_player()
        m = tournament_model.Match(player1= (p1, 0.0),
                                   player2= (p2, 0.0),
                                   start_time=datetime.fromisoformat("2024-05-02 15:45:03"),
                                   end_time=datetime.fromisoformat("2024-05-02 16:17:54"))
        match_dict = m.as_dict()
        self.assertIsInstance(match_dict, dict)
        self.assertEqual(match_dict.get('start_time'), m.start_time.isoformat())
        self.assertEqual(match_dict.get('end_time'), m.end_time.isoformat())
        player_data: tuple[tuple[str, float]] = match_dict.get('players')
        self.assertIsInstance(player_data, list)
        self.assertEqual(player_data[0], [str(m.players[0][0].id()), m.players[0][1]])
        self.assertEqual(player_data[1], [str(m.players[1][0].id()), m.players[1][1]])

    def test_turn_as_dict(self):
        """Dump a valid turn to dict without failure, and check data is consistent."""
        match_list = utils.make_matches()
        turn = tournament_model.Turn("test turn", matches= match_list)

        test_dict = turn.as_dict()
        self.assertIsInstance(test_dict, dict)
        self.assertEqual(test_dict.get('name'), turn.name)
        test_dict_matches = test_dict.get('matches')
        self.assertIsInstance(test_dict_matches, list)
        match_0: dict = test_dict_matches[0]

        self.assertIsInstance(match_0, dict)
        self.assertEqual(match_0.get("start_time"), match_list[0].start_time.isoformat())
        self.assertEqual(match_0.get("end_time"), match_list[0].end_time.isoformat())

        self.assertEqual(len(test_dict_matches), len(turn.matches))
        for m in range(len(turn.matches)):
            dict_match_m: dict = test_dict_matches[m]
            turn_match_m = turn.matches[m]
            match_start_time = turn_match_m.start_time.isoformat() if turn_match_m.start_time is not None else None
            match_end_time = turn_match_m.end_time.isoformat() if turn_match_m.end_time is not None else None
            self.assertEqual(dict_match_m.get('start_time'), match_start_time)
            self.assertEqual(dict_match_m.get('end_time'), match_end_time)
            dict_match_m_players: tuple = dict_match_m.get('players')
            for p in range(len(turn_match_m.players)):
                self.assertEqual(dict_match_m_players[p][0], turn_match_m.players[p][0].id())
                self.assertEqual(dict_match_m_players[p][1], turn_match_m.players[p][1])
    
    def test_tournament_as_dict(self):
        """Export tournament data to a dict object.
        """
        tournament = utils.make_tournament()
        t_data = tournament.as_dict()
        self.assertIsInstance(t_data, dict)
        t_metadata: dict = t_data.get('metadata')
        self.assertIsInstance(t_metadata, dict)
        self.assertEqual(t_metadata.get('location'), tournament.metadata.location)
        self.assertEqual(t_metadata.get('description'), tournament.metadata.description)
        self.assertEqual(t_metadata.get('start_date'),
                         tournament.metadata.start_date.isoformat() if tournament.metadata.start_date is not None else None)
        self.assertEqual(t_metadata.get('end_date'),
                         tournament.metadata.end_date.isoformat() if tournament.metadata.end_date is not None else None)

        self.assertEqual(len(t_data['turns']), len(tournament.turns))
        for t in range(len(tournament.turns)):
            if tournament.turns[t] is None:
                self.assertIsNone(t_data['turns'][t])
            else:
                self.assertDictEqual(t_data['turns'][t], tournament.turns[t].as_dict())
