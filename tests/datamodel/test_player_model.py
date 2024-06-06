import unittest
import tests
import app.models.player_model as player_model
from datetime import date

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
