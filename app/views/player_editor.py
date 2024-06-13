from app.models.player_model import Player, is_valid_national_player_id
from app.adapters.simpleinput import prompt_v
import app.helpers.validation as validation
from datetime import date
import logging
logger = logging.getLogger()

class PlayerEditor:

    def prompt_for_player_data(self, player: Player) -> Player:
        player_data = {}
        player_data['name'] = prompt_v(prompt= "First Name: ",
                        validator= validation.is_valid_name,
                        not_valid_msg="Not a valid name. Accepted characters: letters, space, hyphen and apostrophe")
        player_data['surname'] = prompt_v(prompt= "Surname: ",
                        validator=validation.is_valid_name,
                        not_valid_msg="Not a valid name. Accepted characters: letters, space, hyphen and apostrophe")
        player_data['national_player_id'] = prompt_v(prompt= "National Player ID: ",
                             validator= is_valid_national_player_id,
                             not_valid_msg= "Not a valid Player ID. format: LLDDDDD (ex.: AZ12345)")
        player_data['birthdate'] = prompt_v(prompt="Birthdate: ",
                             validator= validation.is_valid_date,
                             not_valid_msg="Not a valid date. Accepted format: YYYY-MM-DD (ex.: 1987-02-23)")

        if player_data['name']:
            player.name = player_data['name']
        if player_data['surname']:
            player.surname = player_data['surname']
        if player_data['birthdate']:
            player.birthdate = date.fromisoformat(player_data['birthdate'])
        if player_data['national_player_id']:
            player.set_id(player_data['national_player_id'])
        return player


