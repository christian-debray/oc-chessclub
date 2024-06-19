from app.commands import commands
from app.controllers.controller_abc import BaseController, MainController
from app.models.tournament_model import TournamentRepository, TournamentMetaData
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

    def _curr_tournament_id(self) -> str:
        return self.main_app.get_state("current_tournament_id")

    def _curr_tournament_meta(self) -> TournamentMetaData:
        if curr_id := self._curr_tournament_id():
            return self.tournament_repo.find_tournament_metadata_by_id(curr_id)
        return None

    def menu(self):
        """Load the Tournament manager menu"""
        current_tournament_str = None
        if curr_tournament_meta := self._curr_tournament_meta():
            current_tournament_str = f"Current tournament: {self._tournament_meta_str(curr_tournament_meta)}"

        menu = Menu(title="Tournament Manager - Menu",
                    cmdManager=self.main_app,
                    text=current_tournament_str
                    )
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
                tournament = self.tournament_repo.find_tournament_by_id(
                    tournament_id=tournament_id
                )
                if not tournament:
                    reason = "Tournament ID not found"
                    raise KeyError(reason)
                self.main_app.set_state('current_tournament_id', tournament_id)
                tournament_meta_str = self._tournament_meta_str(tournament.metadata)
                self.status.notify_success(f"Tournament loaded: {tournament_meta_str}")
            except Exception as e:
                logger.error(e)
                self.status.notify_failure(
                    f"Failed to load tournament data. {reason}\n\
Please check the tournament ID and files in the tournament data folder."
                )
                return

    def _tournament_meta_str(self, meta: TournamentMetaData) -> str:
        """Return a simple string view of a tournament metadata
        """
        return tournament_views.TournamentMetaView.tournament_meta_template(meta.asdict())

    def list_tournaments(self):
        """Display a list of all tournaments."""
        tournaments = self.tournament_repo.list_tournament_meta()
        data = [m.asdict() for m in tournaments]
        v = tournament_views.TournamentsListView(
            cmd_manager=self.main_app, title="All Tournaments", tournament_list=data
        )
        self.main_app.view(v)

    def edit_tournament_info(self, tournament_id: str = None):
        """Edit tournament meta-data.
        Some fields may be editable or froze, depending on the tournament's current status.
        """
        if not tournament_id:
            tournament_metadata = self._curr_tournament_meta()
        else:
            tournament_metadata = self.tournament_repo.find_tournament_metadata_by_id(tournament_id)
            if not tournament_metadata:
                self.status.notify_failure("Tournament not found.")
                return

        frozen_fields = ['tournament_id', 'data_file', 'status', 'end_date']
        if tournament_metadata.status in ('running', 'ended'):
            frozen_fields += ['start_date', 'location', 'turn_count']

        v = tournament_views.TournamentMetaEditor(
            cmd_manager=self.main_app,
            title="Tournament Editor",
            data=tournament_metadata.asdict(),
            frozen_fields=frozen_fields,
            text=f"Edit tournament {self._tournament_meta_str(tournament_metadata)}"
        )
        self.main_app.view(v)
