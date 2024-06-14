import unittest
import tests
import app.models.player_model as player_model
import app.models.tournament_model as tournament_model
from datetime import date, datetime
from pathlib import Path
import json

class TestTournamentJSON(unittest.TestCase):
    """Test JSON encoding and decoding of Tournament entities
    """
    def test_match_json_encoder(self):
        """Dump a valid match to JSON string without failure,
        loading the dump using the default JSONDecoder should produce a dict
        with match data.
        """
        p1 = player_model.Player(
            national_player_id= player_model.NationalPlayerID('FR12345'),
            name="Dummy",
            surname="Player 1",
            birthdate= date.fromisoformat("1981-01-01"))
        p2 = player_model.Player(            
            national_player_id= player_model.NationalPlayerID('FR23456'),
            name="Dummy",
            surname="Player 2",
            birthdate= date.fromisoformat("1982-02-02"))

        m = tournament_model.Match(player1= (p1, 0.0),
                                   player2= (p2, 0.0),
                                   start_time=datetime.fromisoformat("2024-05-02 15:45:03"),
                                   end_time=datetime.fromisoformat("2024-05-02 16:17:54"))
        dump_str = json.dumps(m, cls= tournament_model.MatchJSONEncoder)
        self.assertIsInstance(dump_str, str)
        match_dict: dict = json.loads(dump_str)
        self.assertIsInstance(match_dict, dict)
        self.assertEqual(match_dict.get('start_time'), m.start_time.isoformat())
        self.assertEqual(match_dict.get('end_time'), m.end_time.isoformat())
        player_data: tuple[tuple[str, float]] = match_dict.get('players')
        self.assertIsInstance(player_data, list)
        self.assertEqual(player_data[0], [str(m.players[0][0].id()), m.players[0][1]])
        self.assertEqual(player_data[1], [str(m.players[1][0].id()), m.players[1][1]])
