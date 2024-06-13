from app.models.player_model import Player, is_valid_national_player_id
from app.adapters.simpleinput import prompt_v
import app.helpers.validation as validation
from datetime import date
from app.views.app_status_view import AppStatusView
import logging
logger = logging.getLogger()

class PlayerEditor:

    def __init__(self, status: AppStatusView = None):
        self.status = status

    def prompt_for_player_data(self, player: Player) -> Player:
        """Player Data editor.

        The edited data will always be returned as a new Player object. The original object remains unchanged.
        """
        print("PLAYER EDITOR")
        print("Please enter Player data.\n(Leave an input blank or hit <ctrl>+<D> to leave field unchanged)\n")

        edited_player = Player.copy(player)

        name_prompt = ("First Name" if not player.name else f"First Name (current= {player.name})") + ":\n"
        if new_name := prompt_v(prompt= name_prompt,
                        validator= validation.is_valid_name,
                        not_valid_msg="Not a valid name. Accepted characters: letters, space, hyphen and apostrophe",
                        skip_blank= True):
            edited_player.name = new_name
        elif player.name:
            self.status.notify_warning(f"Keeping previous value: {player.name}\n")

        surname_prompt = ("Surname" if not player.surname else f"Surname (current= {player.surname})") + ":\n"
        if new_surname := prompt_v(prompt= surname_prompt,
                        validator=validation.is_valid_name,
                        not_valid_msg="Not a valid name. Accepted characters: letters, space, hyphen and apostrophe",
                        skip_blank= True):
            edited_player.surname = new_surname
        elif player.surname:
            self.status.notify_warning(f"Keeping previous value: {player.surname}\n")
        
        id_prompt = ("National Player ID" if not player.national_player_id else f"National Player ID (current= {player.id()})") + ":\n"
        if new_national_player_id := self.player_id_prompt(id_prompt):
            edited_player.set_id(new_national_player_id)
        elif player.national_player_id:
            self.status.notify_warning(f"Keeping previous value: {player.id()}\n")

        birthdate_prompt = ("Birthdate" if not player.birthdate else f"Birthdate (current= {player.birthdate.isoformat()})") + ":\n"
        if new_birthdate := prompt_v(prompt=birthdate_prompt,
                             validator= validation.is_valid_date,
                             not_valid_msg="Not a valid date. Accepted format: YYYY-MM-DD (ex.: 1987-02-23)",
                             skip_blank= True):
            edited_player.birthdate = date.fromisoformat(new_birthdate)
        elif player.birthdate:
            self.status.notify_warning(f"Keeping previous value: {player.birthdate.isoformat()}")

        return edited_player

    def player_id_prompt(self, prompt: str):
        return prompt_v(prompt= prompt,
                        validator= is_valid_national_player_id,
                        not_valid_msg= "Not a valid Player ID. format: LLDDDDD (ex.: AZ12345)",
                        skip_blank= True)

