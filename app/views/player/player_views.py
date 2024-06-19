from app.models.player_model import is_valid_national_player_id
from app.commands.commands_abc import CommandInterface, CommandManagerInterface
from app.helpers.text_ui import prompt_v, confirm, clear, proceed_any_key
from app.helpers.string_formatters import format_cols
import app.helpers.validation as validation
from datetime import date
from app.views.views_abc import AbstractView
from app.views.app_status_view import AppStatusView
import logging

logger = logging.getLogger()


class PlayerView(AbstractView):
    """View a player's data
    """
    def __init__(self, playerdata: dict):
        self.playerdata = playerdata

    def render(self):
        print(self.player_template(player=self.playerdata, as_cells=False))

    @staticmethod
    def player_template(playerdata: dict, as_cells: bool = False) -> str | list[str]:
        id_tpl = f"{playerdata['national_player_id']}"
        name_tpl = f"{playerdata['surname'].upper()} {playerdata['name'].capitalize()}"
        date_tpl = f"(born {playerdata['birthdate'].strftime("%d/%m/%Y")})"
        cells = [id_tpl, name_tpl, date_tpl]
        return cells if as_cells else " - ".join(cells)


class PlayerListView:
    """View a list of players
    """
    def __init__(self, player_list: list[dict]):
        self.player_list = player_list

    def render(self):
        print("*** Players List ***")
        print(self.player_list_str(self.player_list))
        proceed_any_key()

    @staticmethod
    def player_list_str(players: list[dict]) -> str:
        p_lines = [PlayerView.player_template(p, as_cells=True) for p in players]
        return format_cols(p_lines, ["Player ID", "Name", "Birthdate"])


class PlayerEditor(AbstractView):
    """Display a form to edit or create a Player.
    """
    def __init__(self,
                 cmd_manager: CommandManagerInterface,
                 player_data: dict,
                 status: AppStatusView = None,
                 update_player_command: CommandInterface = None,
                 cancel_command: CommandInterface = None):
        super().__init__(cmd_manager=cmd_manager)
        self.player_data = player_data
        self.status = status
        self.update_player_command = update_player_command
        self.cancel_command = cancel_command

    def render(self):
        self.player_data = self.prompt_for_player_data(self.player_data)
        if self.player_data is None and self.cancel_command:
            self.issuecmd(self.cancel_command)
        elif self.player_data is not None and self.update_player_command:
            self.update_player_command.set_command_params(**self.player_data)
            self.issuecmd(self.update_player_command)

    def prompt_for_player_data(self, playerdata: dict) -> dict:
        """Player Data editor.

        The edited data will always be returned as a new Player object. The original object remains unchanged.
        """
        clear()
        print("*** PLAYER EDITOR ***")
        print(
            "Please enter Player data.\n(Leave an input blank or hit <ctrl>+<D> to leave field unchanged)\n"
        )

        if playerdata.get('national_player_id'):
            print(f"Editing player: {PlayerView.player_template(playerdata=playerdata)}\n")

        edited_player = playerdata.copy()

        name_prompt = (
            "First Name" if not playerdata.get('name') else f"First Name (current= {playerdata.get('name')})"
        ) + ":\n"
        if new_name := prompt_v(
            prompt=name_prompt,
            validator=validation.is_valid_name,
            not_valid_msg="Not a valid name. Accepted characters: letters, space, hyphen and apostrophe",
            skip_blank=True,
        ):
            edited_player['name'] = new_name
        elif playerdata['name']:
            self.status.notify_warning(f"Keeping previous value: {playerdata['name']}\n")

        surname_prompt = (
            "Surname" if not playerdata['surname'] else f"Surname (current= {playerdata['surname']})"
        ) + ":\n"
        if new_surname := prompt_v(
            prompt=surname_prompt,
            validator=validation.is_valid_name,
            not_valid_msg="Not a valid name. Accepted characters: letters, space, hyphen and apostrophe",
            skip_blank=True,
        ):
            edited_player['surname'] = new_surname
        elif playerdata['surname']:
            self.status.notify_warning(f"Keeping previous value: {playerdata['surname']}\n")

        id_prompt = (
            "National Player ID"
            if not playerdata.get('national_player_id')
            else f"National Player ID (current= {playerdata.get('national_player_id')})"
        ) + ":\n"
        if new_national_player_id := PlayerIDPrompt.getinput(prompt=id_prompt):
            edited_player['national_player_id'] = new_national_player_id
        elif playerdata['national_player_id']:
            self.status.notify_warning(f"Keeping previous value: {playerdata['national_player_id']}\n")

        birthdate_prompt = (
            "Birthdate"
            if not playerdata['birthdate']
            else f"Birthdate (current= {playerdata['birthdate'].isoformat()})"
        ) + ":\n"
        if new_birthdate := prompt_v(
            prompt=birthdate_prompt,
            validator=validation.is_valid_date,
            not_valid_msg="Not a valid date. Accepted format: YYYY-MM-DD (ex.: 1987-02-23)",
            skip_blank=True,
        ):
            edited_player['birthdate'] = date.fromisoformat(new_birthdate)
        elif playerdata['birthdate']:
            self.status.notify_warning(
                f"Keeping previous value: {playerdata['birthdate'].isoformat()}"
            )

        if confirm(msg="Store changes ? (Press Y to confirm)"):
            return edited_player
        else:
            self.status.notify_warning("Discarding changes.")
        return None


class PlayerIDPrompt(AbstractView):
    """Prompt user form player ID.
    """
    def __init__(
        self,
        cmd_mgr: CommandManagerInterface,
        prompt: str = None,
        cancelCommand: CommandInterface = None,
        confirmCommand: CommandInterface = None,
    ):
        super().__init__(cmd_manager=cmd_mgr)
        self.prompt = prompt
        self.cancelcommand: CommandInterface = cancelCommand
        self.confirmcommand: CommandInterface = confirmCommand

    def render(self):
        val = self.getinput(self.prompt)
        if val is not None and self.confirmcommand:
            self.confirmcommand.set_command_params(val)
            self.issuecmd(self.confirmcommand)
        elif self.cancelcommand:
            self.issuecmd(self.cancelcommand)

    @staticmethod
    def getinput(prompt):
        return prompt_v(
            prompt=f"{prompt}",
            validator=is_valid_national_player_id,
            not_valid_msg="Not a valid Player ID. format: LLDDDDD (ex.: AZ12345)",
            skip_blank=True,
        )