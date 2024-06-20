from datetime import date
from app.models.player_model import PlayerRepository, Player
from app.controllers.controller_abc import BaseController, MainController
from app.commands import commands_abc, commands
from app.views.menu import Menu, MenuOption
from app.views.player.player_views import PlayerEditor, PlayerListView, PlayerIDPrompt
import logging

logger = logging.getLogger()


class RegisterPlayerCommand(commands.LaunchManagerCommand):
    def __init__(self, app=commands_abc.CommandManagerInterface) -> None:
        super().__init__(
            app=app, cls_or_obj=PlayerManager, method=PlayerManager.register_new_player
        )


class EditPlayerCommand(commands.LaunchManagerCommand):
    def __init__(
        self, app=commands_abc.CommandManagerInterface, player_id: str = None
    ) -> None:
        super().__init__(
            app=app, cls_or_obj=PlayerManager, method=PlayerManager.edit_player
        )
        self.set_command_params(player_id=player_id)


class ListAllPlayersCommand(commands.LaunchManagerCommand):
    def __init__(self, app=commands_abc.CommandManagerInterface) -> None:
        super().__init__(
            app=app, cls_or_obj=PlayerManager, method=PlayerManager.list_all_players
        )


class NewPlayerDataCommand(commands.LaunchManagerCommand):

    def __init__(self, app: commands_abc.CommandManagerInterface):
        super().__init__(
            app=app, cls_or_obj=PlayerManager, method=PlayerManager.add_new_player
        )
        self.params = Player().asdict()


class UpdatePlayerDataCommand(commands.LaunchManagerCommand):

    def __init__(self, app: commands_abc.CommandManagerInterface, player_data: dict):
        super().__init__(
            app=app,
            cls_or_obj=PlayerManager,
            method=PlayerManager.update_player,
            **player_data,
        )


class PlayerManager(BaseController):
    def __init__(self, player_repo: PlayerRepository, app: MainController):
        super().__init__()
        self.main_app: MainController = app
        self.player_repo: PlayerRepository = player_repo

    def default(self):
        """Launches the player manager: display the menu."""
        menu_command = commands.DisplayMenuCommand(
            app=self.main_app, cls_or_obj=PlayerManager, cycle=True
        )
        self.main_app.receive(menu_command)

    def menu(self):
        """Loads the Player Manager Menu"""
        menu = Menu(title="Manage Players - Menu", cmdManager=self.main_app)
        menu.add_option(
            MenuOption(
                option_text="Register New Player",
                command=RegisterPlayerCommand(app=self.main_app),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Edit Player", command=EditPlayerCommand(app=self.main_app)
            )
        )
        menu.add_option(
            MenuOption(
                option_text="List all players",
                command=ListAllPlayersCommand(app=self.main_app),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Return to previous menu",
                alt_key="X",
                command=commands.ExitCurrentCommand(self.main_app),
            )
        )
        self.main_app.view(menu)

    def register_new_player(self):
        """Register a new player in the database."""
        editor = PlayerEditor(
            cmd_manager=self.main_app,
            player_data=Player().asdict(),
            status=self.status,
            cancel_command=None,
            update_player_command=NewPlayerDataCommand(app=self.main_app),
        )
        self.main_app.view(editor)

    def edit_player(self, player_id: str | Player = None):
        """Edit player identified by player ID."""
        if not player_id:
            # Try again with a player ID...
            prompt_view = PlayerIDPrompt(
                cmd_mgr=self.main_app,
                prompt="Please enter the ID of the player to edit > ",
                cancelCommand=None,
                confirmCommand=EditPlayerCommand(app=self.main_app),
            )
            self.main_app.view(prompt_view)
            return
        try:
            player = self.player_repo.find_by_id(player_id)
            if not player:
                raise ValueError("Unknown player ID")
        except ValueError as e:
            self.status.notify_failure("Player not found: " + str(e))
            return
        editor = PlayerEditor(
            cmd_manager=self.main_app,
            player_data=player.asdict(),
            status=self.status,
            update_player_command=UpdatePlayerDataCommand(
                app=self.main_app, player_data=player.asdict()
            ),
            cancel_command=None,
        )
        self.main_app.view(editor)

    def add_new_player(
        self, national_player_id: str, name: str, surname: str, birthdate: date
    ) -> bool:
        """Register a new player to the database"""
        try:
            player = Player(
                national_player_id=national_player_id,
                surname=surname,
                name=name,
                birthdate=birthdate,
            )
            if player.is_valid():
                self.player_repo.add(player)
                self.player_repo.commit_changes()
                self.status.notify_success(
                    f"New player registered with ID: {player.id()}"
                )
                return True
            else:
                self.status.notify_failure(
                    "Can't register player with invalid or incomplete data. Abandon."
                )
        except KeyError as e:
            logger.exception(e)
            self.status.notify_failure(
                "Failed to register player: Duplicate or invalid Player ID. Abandon."
            )
        except Exception as e:
            logger.exception(e)
            self.status.notify_failure(
                "Failed to register player because of an unexpected error. Abandon."
            )
        return False

    def update_player(
        self, national_player_id: str, name: str, surname: str, birthdate: date
    ) -> bool:
        """Updates an existing player in the database.

        First compares old player data with new player data.

        - If nothing has changed, send a notificaiton to the user and return.
        - If the player ID has changed, first remove the old ID from the repository,
        then update or create the new one.
        - In all other cases update the existing player data in the repository.
        Notify user and returns True on success.
        """
        player_data = self.player_repo.find_by_id(national_player_id)
        if not player_data:
            self.add_new_player(national_player_id, name, surname, birthdate)
        try:
            new_player_data = Player(
                national_player_id, surname=surname, name=name, birthdate=birthdate
            )

            if player_data == new_player_data:
                self.status.notify_warning("No changes to record")
                return

            if not new_player_data.is_valid():
                self.status.notify_failure(
                    "Can't update player with invalid or incomplete data. Abandon."
                )
                return False
            if player_data.id() != new_player_data.id():
                # We must delete the existing player data first
                # Then check if the new ID already exists,
                # in which case we just udpate a player
                # otherwise we must register a new player
                self.status.notify("Changing player ID: deleting old record...")
                self.player_repo.delete(player_data.id())
                if not self.player_repo.find_by_id(new_player_data.id()):
                    return self.add_new_player(
                        player_id=national_player_id,
                        name=name,
                        surname=surname,
                        birthdate=birthdate,
                    )

            self.player_repo.update(new_player_data)
            self.player_repo.commit_changes()
            self.status.notify_success(f"Updated player: {new_player_data.id()}")
            return True
        except Exception as e:
            logger.exception(e)
            self.status.notify_failure(
                "Failed to update player because of an unexpected error. Abandon."
            )
        return False

    def list_all_players(self):
        player_list = list(self.player_repo.find_many())
        if len(player_list) == 0:
            self.status.notify_warning("No players to display.")
            return
        # alphabetic order:
        player_list.sort(key=lambda x: (x.surname.lower() + x.name.lower()))
        view = PlayerListView(player_list=[p.asdict() for p in player_list])
        self.main_app.view(view)
