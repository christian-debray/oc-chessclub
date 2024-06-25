from app.commands.commands_abc import CommandInterface, CommandManagerInterface
from app.views.views_abc import AbstractView
from app.views.player.player_views import PlayerIDPrompt, PlayerView
from app.views.dialogs import Dialog


class RegisterTournamentView(AbstractView):
    """Prompt the user to enter the national player ID of a player
    registering into a tournament.

    Optionnally help the user by displaying a list of players who already
    joined the tournament and a list of available player IDs.
    """

    def __init__(
        self,
        cmd_manager: CommandManagerInterface,
        title: str = None,
        list_available_players_cmd: CommandInterface = None,
        list_registered_players_cmd: CommandInterface = None,
        confirm_cmd: CommandInterface = None,
        new_player_cmd: CommandInterface = None,
        cancel_cmd: CommandInterface = None,
    ):
        super().__init__(cmd_manager=cmd_manager)
        self.title = title or "Register a player to a tournament"
        self.cancel_cmd: CommandInterface = cancel_cmd
        self.confirm_cmd: CommandInterface = confirm_cmd
        self.new_player_cmd: CommandInterface = new_player_cmd
        self.list_available_players_cmd = list_available_players_cmd
        self.list_registered_players_cmd = list_registered_players_cmd
        self.list_available_key = "A"
        self.list_registered_key = "R"
        self.new_player_key = "N"

    def render(self):
        print("\n")
        if self.title:
            print(f"*** {self.title.upper()} ***\n")

        keys = ["<ctrl>+D or <enter> to abort"]
        shortcuts = {}
        if self.list_available_players_cmd:
            keys.append(
                f"'{self.list_available_key}' then <enter> to display a list of available players"
            )
            shortcuts[self.list_available_key] = self.list_available_key
        if self.list_available_players_cmd:
            keys.append(
                f"'{self.list_registered_key}' then <enter> to display current participants list"
            )
            shortcuts[self.list_registered_key] = self.list_registered_key
        if self.new_player_cmd:
            keys.append(f"'{self.new_player_key}' then <enter> to create a new player")
            shortcuts[self.new_player_key] = self.new_player_key
        print("Enter the National Player ID to register.\n" + "\n  ".join(keys))
        player_id = PlayerIDPrompt.getinput(prompt="Player ID > ", shortcuts=shortcuts)

        if not player_id:
            self.issuecmd(self.cancel_cmd)
        elif player_id.upper() == self.list_available_key:
            self.issuecmd(self.list_available_players_cmd)
        elif player_id.upper() == self.list_registered_key:
            self.issuecmd(self.list_registered_players_cmd)
        elif player_id.upper() == self.new_player_key:
            self.issuecmd(self.new_player_cmd)
        elif self.confirm_cmd:
            self.confirm_cmd.set_command_params(player_id=player_id)
            self.issuecmd(self.confirm_cmd)


class ConfirmPlayerIDView(Dialog):
    """Confirm Player ID before registration to a tournament."""

    def __init__(
        self,
        cmd_manager: CommandManagerInterface,
        playerdata: dict,
        tournament_id: str,
        confirm_cmd: CommandInterface = None,
        abandon_cmd: CommandInterface = None,
    ):
        super().__init__(
            cmd_manager=cmd_manager,
            title=None,
            confirm_cmd=confirm_cmd,
            abandon_cmd=abandon_cmd
            )
        self.playerdata = playerdata
        self.tournament_id = tournament_id
        self.text = f"This player will be registered in tournament {self.tournament_id}:\n"
        self.text += PlayerView.player_template(self.playerdata)
