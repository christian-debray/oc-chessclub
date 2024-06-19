from app.commands import commands
from app.controllers.controller_abc import BaseController, MainController
from app.models.tournament_model import TournamentRepository
from app.views.views_abc import SimpleView
from app.views.menu import Menu, MenuOption
from app.views.tournament import tournament_views
import logging

logger = logging.getLogger()


class NewTournamentCommand(commands.LaunchManagerCommand):
    def __init__(self, app: commands.CommandManagerInterface) -> None:
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.new_tournament,
        )


class LoadTournamentCommand(commands.LaunchManagerCommand):
    def __init__(
        self, app: commands.CommandManagerInterface, tournament_id: str = None
    ) -> None:
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.load_tournament,
            tournament_id=tournament_id,
        )


class ListTournamentsCommand(commands.LaunchManagerCommand):
    def __init__(self, app: commands.CommandManagerInterface) -> None:
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.list_tournaments,
        )


class EditTournamentInfoCommand(commands.LaunchManagerCommand):
    def __init__(
        self, app: commands.CommandManagerInterface, tournament_id: str = None
    ) -> None:
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.edit_tournament_info,
            tournament_id=tournament_id,
        )


class TournamentManager(BaseController):
    """Manage Tournaments: create and run tournaments."""

    def __init__(self, tournament_repo: TournamentRepository, main_app: MainController):
        super().__init__()
        self.main_app: MainController = main_app
        self.tournament_repo: TournamentRepository = tournament_repo

    def default(self):
        """Launches the player manager: display the menu."""
        menu_command = commands.DisplayMenuCommand(
            app=self.main_app, cls_or_obj=TournamentManager, cycle=True
        )
        self.main_app.receive(menu_command)

    def menu(self):
        """Load the Tournament manager menu"""
        menu = Menu("Tournament Manager - Menu", cmdManager=self.main_app)
        menu.add_option(
            MenuOption(
                option_text="New Tournament",
                command=NewTournamentCommand(app=self.main_app),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Load Tournament",
                command=LoadTournamentCommand(app=self.main_app),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="List Tournaments",
                command=ListTournamentsCommand(app=self.main_app),
            )
        )
        if current_tournament_id := self.main_app.get_state('current_tournament_id'):
            menu.add_option(
                MenuOption(
                    option_text="Edit Current Tournament Info",
                    command=EditTournamentInfoCommand(
                        app=self.main_app, tournament_id=current_tournament_id
                    ),
                )
            )
        menu.add_option(
            MenuOption(
                option_text="Return to main menu",
                alt_key="X",
                command=commands.ExitCurrentCommand(self.main_app),
            )
        )
        self.main_app.view(menu)

    def new_tournament(self):
        """Creates a new tournament."""
        v = SimpleView(cmd_manager=self.main_app, title="Create a new Tournament")
        self.main_app.view(v)

    def load_tournament(self, tournament_id: str = None):
        """Load a tournament in memory and sets as current tournament
        for other operations.
        """
        if not tournament_id:
            # Come back with a tournament ID...
            v = tournament_views.SelectTournamentIDView(
                cmd_manager=self.main_app,
                confirm_command=LoadTournamentCommand(app=self.main_app),
            )
            self.main_app.view(v)
            return
        else:
            reason = ""
            try:
                tournament_data = self.tournament_repo.find_tournament_by_id(
                    tournament_id=tournament_id
                )
                if not tournament_data:
                    reason = "Tournament ID not found"
                    raise KeyError(reason)
                self.main_app.set_state('current_tournament_id', tournament_id)
                tournament_meta = (
                    tournament_views.TournamentMetaView.tournament_meta_template(
                        tournament_data.metadata.asdict()
                    )
                )
                self.status.notify_success(f"Tournament loaded: {tournament_meta}")
            except Exception as e:
                logger.error(e)
                self.status.notify_failure(
                    f"Failed to load tournament data. {reason}\n\
Please check the tournament ID and files in the tournament data folder."
                )
                return

    def list_tournaments(self):
        """Display a list of all tournaments."""
        tournaments = self.tournament_repo.list_tournament_meta()
        data = [m.asdict() for m in tournaments]
        v = tournament_views.TournamentsListView(
            cmd_manager=self.main_app, title="All Tournaments", tournament_list=data
        )
        self.main_app.view(v)

    def edit_tournament_info(self, tournament_id: str):
        """Edit tournament meta-data."""
        v = SimpleView(
            cmd_manager=self.main_app,
            title="Edit Tournament Info",
            text=f"This would change the metadata of tournament {tournament_id}",
        )
        self.main_app.view(v)
