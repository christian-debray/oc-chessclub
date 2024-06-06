import unittest
import tests
import app.models.player_model as player_model
from datetime import date
from pathlib import Path
import json

class TestNationalPlayerID(unittest.TestCase):
    """Test constraints on National Player ID type
    """
    def test_is_valid_national_player_id(self):
        """is_valid_national_player_id() accepts 1 string and should return:
            - False when string is not in the proper format or None
            - True when string is in the proper format:
                7 characters long, starting with  2 capital letters
                followed by 5 digits
        """
        valid = "AZ12345"
        not_valid = [
            "aa00000",
            "0x00000",
            "AZ-12345",
            "",
            None,
            "Azerty",
            "AZ 12345"
        ]
        self.assertIs(True, player_model.is_valid_national_player_id(valid))
        for v in not_valid:
            self.assertIs(False, player_model.is_valid_national_player_id(v))
    
    def test_wrong_type(self):
        """Should raise a TypeError when input is of invalid type and not None
        """
        bad_type = [1234567, ['A', 'Z', '1', '2', '3', '4', '5'], {'AZ12345': 'AZ12345'}]
        for b in bad_type:
            with self.subTest(b=b):
                self.assertRaises(TypeError, player_model.is_valid_national_player_id, b)

    def test_valid_init(self):
        n_p_id = player_model.NationalPlayerID("AZ12345")
        self.assertEqual(len(str(n_p_id)), 7)
        self.assertEqual(n_p_id, "AZ12345")
    
    @unittest.expectedFailure
    def test_invalid_init(self):
        """Bad string format
        """
        bad_player_id = player_model.NationalPlayerID("BAD1234")

    @unittest.expectedFailure
    def test_invalid_default(self):
        """Default value makes no sense
        """
        bad_player_id = player_model.NationalPlayerID()


class TestPlayerRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.test_player_file = Path(tests.TEST_TMP_DIR, "test_player_repo.json")
        self.test_player_file.touch(mode=0o666)
    
    def tearDown(self) -> None:
        self.test_player_file.unlink(missing_ok= True)

    def test_player_json_encoder(self):
        new_player = player_model.Player(
            national_player_id= player_model.NationalPlayerID("AZ12345"),
            surname= "Doe",
            name= "John",
            birthdate= date(1985, 8, 19)
        )
        dumped = json.dumps(new_player, cls=player_model.PlayerJSONEncoder)
        expected_json = '{"national_player_id": "AZ12345", "surname": "Doe", "name": "John", "birthdate": "1985-08-19"}'
        self.assertEqual(dumped, expected_json)

    def test_player_json_decoder(self):
        json_str = '{"national_player_id": "AZ12345", "surname": "Doe", "name": "John", "birthdate": "1985-08-19"}'
        new_player = json.loads(json_str, cls=player_model.PlayerJSONDecoder)
        self.assertIsInstance(new_player, player_model.Player)

    def test_add_new_player(self):
        repo = player_model.PlayerRepository(self.test_player_file)
        new_player = player_model.Player(
            national_player_id= player_model.NationalPlayerID("AZ12345"),
            surname= "Doe",
            name= "John",
            birthdate= date(1985, 8, 19)
        )
        repo.add(new_player)
        self.assertIsNot(None, repo.find_by_id('AZ12345'))
        repo.commit_changes()

        with open(self.test_player_file, "r") as fh:
            data = fh.read()
            raw_obj = json.loads(data)
            decoded = json.loads(data, cls= player_model.PlayerJSONDecoder)

        self.assertIsInstance(decoded, dict)
        self.assertIn(new_player.id(), decoded)
        self.assertEqual(new_player, decoded[new_player.id()])
