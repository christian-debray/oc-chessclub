from app.models.player_model import is_valid_national_player_id, Player
from app.commands import commands, player_commands
from app.helpers.text_ui import prompt_v, confirm, clear, proceed_any_key
from app.helpers.string_formatters import format_cols
import app.helpers.validation as validation
from datetime import date
from app.views.app_status_view import AppStatusView
import logging

logger = logging.getLogger()


class PlayerView:
    """View a player's data
    """
    def __init__(self, player_data: Player):
        self.player_data = player_data

    def render(self):
        print(self.player_template(player=self.player_data, as_cells=False))

    @staticmethod
    def player_template(player: Player, as_cells: bool = False) -> str | list[str]:
        id_tpl = f"{player.national_player_id}"
        name_tpl = f"{player.surname.upper()} {player.name.capitalize()}"
        date_tpl = f"(born {player.birthdate.strftime("%d/%m/%Y")})"
        cells = [id_tpl, name_tpl, date_tpl]
        return cells if as_cells else " - ".join(cells)


class PlayerListView:
    """View a list of players
    """
    def __init__(self, player_list: list[Player]):
        self.player_list = player_list

    def render(self):
        print("*** Players List ***")
        print(self.player_list_str(self.player_list))
        proceed_any_key()

    @staticmethod
    def player_list_str(players: list[Player]) -> str:
        p_lines = [PlayerView.player_template(p, as_cells=True) for p in players]
        return format_cols(p_lines, ["Player ID", "Name", "Birthdate"])


class PlayerEditor:
    """Display a form to edit or create a Player.
    """
    def __init__(self,
                 player_data: Player = None,
                 status: AppStatusView = None,
                 update_player_command: player_commands.UpdatePlayerDataCommand = None,
                 cancel_command: commands.AbortCommand = None):
        self.old_player_data = player_data or Player()
        self.new_player_data = Player()
        self.status = status
        self.update_player_command = update_player_command
        self.cancel_command = cancel_command

    def render(self):
        self.new_player_data = self.prompt_for_player_data(self.old_player_data)
        if self.new_player_data is None and self.cancel_command:
            self.cancel_command.execute()
        elif self.update_player_command:
            self.update_player_command.new_player_data = self.new_player_data
            self.update_player_command.execute()

    def prompt_for_player_data(self, player: Player) -> Player:
        """Player Data editor.

        The edited data will always be returned as a new Player object. The original object remains unchanged.
        """
        clear()
        print("*** PLAYER EDITOR ***")
        print(
            "Please enter Player data.\n(Leave an input blank or hit <ctrl>+<D> to leave field unchanged)\n"
        )
        if player is not None and player.id():
            print("Editing player:")
            print(PlayerView.player_template(player=player))

        edited_player = Player.copy(player)

        name_prompt = (
            "First Name" if not player.name else f"First Name (current= {player.name})"
        ) + ":\n"
        if new_name := prompt_v(
            prompt=name_prompt,
            validator=validation.is_valid_name,
            not_valid_msg="Not a valid name. Accepted characters: letters, space, hyphen and apostrophe",
            skip_blank=True,
        ):
            edited_player.name = new_name
        elif player.name:
            self.status.notify_warning(f"Keeping previous value: {player.name}\n")

        surname_prompt = (
            "Surname" if not player.surname else f"Surname (current= {player.surname})"
        ) + ":\n"
        if new_surname := prompt_v(
            prompt=surname_prompt,
            validator=validation.is_valid_name,
            not_valid_msg="Not a valid name. Accepted characters: letters, space, hyphen and apostrophe",
            skip_blank=True,
        ):
            edited_player.surname = new_surname
        elif player.surname:
            self.status.notify_warning(f"Keeping previous value: {player.surname}\n")

        id_prompt = (
            "National Player ID"
            if not player.national_player_id
            else f"National Player ID (current= {player.id()})"
        ) + ":\n"
        if new_national_player_id := self.player_id_prompt(id_prompt):
            edited_player.set_id(new_national_player_id)
        elif player.national_player_id:
            self.status.notify_warning(f"Keeping previous value: {player.id()}\n")

        birthdate_prompt = (
            "Birthdate"
            if not player.birthdate
            else f"Birthdate (current= {player.birthdate.isoformat()})"
        ) + ":\n"
        if new_birthdate := prompt_v(
            prompt=birthdate_prompt,
            validator=validation.is_valid_date,
            not_valid_msg="Not a valid date. Accepted format: YYYY-MM-DD (ex.: 1987-02-23)",
            skip_blank=True,
        ):
            edited_player.birthdate = date.fromisoformat(new_birthdate)
        elif player.birthdate:
            self.status.notify_warning(
                f"Keeping previous value: {player.birthdate.isoformat()}"
            )

        if confirm(msg="Store changes ? (Press Y to confirm)"):
            return edited_player
        else:
            self.status.notify_warning("Discarding changes.")
        return None

    def player_id_prompt(self, prompt: str):
        return PlayerIDPrompt(prompt=prompt).getinput()


class PlayerIDPrompt:
    """Prompt user form player ID.
    """
    def __init__(
        self,
        prompt: str = None,
        cancelCommand: commands.AbortCommand = None,
        confirmCommand: commands.ConfirmValueCommand = None,
    ):
        self.prompt = prompt
        self.cancelcommand: commands.AbortCommand = cancelCommand
        self.confirmcommand: commands.ConfirmValueCommand = confirmCommand

    def render(self):
        if val := self.getinput() and self.confirmcommand:
            self.confirmcommand.set_value(val)
            self.confirmcommand.execute()
        elif self.cancelcommand:
            self.cancelcommand.execute()

    def getinput(self):
        return prompt_v(
            prompt=self.prompt,
            validator=is_valid_national_player_id,
            not_valid_msg="Not a valid Player ID. format: LLDDDDD (ex.: AZ12345)",
            skip_blank=True,
        )
