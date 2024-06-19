from datetime import date
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


class UpdateTournamentMetaCommand(commands.LaunchManagerCommand):
    def __init__(
            self, app: commands.CommandInterface,
            form_data: dict = None):
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.update_tournament_meta,
            **form_data
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

    def _tournament_meta(
        self, tournament_id: str = None, notify_failure: bool = True
    ) -> TournamentMetaData:
        """Gets tournament metadata.

        If tournament_id is omitted,
        searches for the metadata of the current tournament, if any.
        Optionnaly notifies failure to user.
        """
        tournament_metadata = None
        if not tournament_id:
            tournament_metadata = self._curr_tournament_meta()
        else:
            tournament_metadata = self.tournament_repo.find_tournament_metadata_by_id(
                tournament_id
            )
        if not tournament_metadata and notify_failure:
            self.status.notify_failure("Tournament not found.")
        return tournament_metadata

    def _tournament_meta_str(self, meta: TournamentMetaData) -> str:
        """Return a simple string view of a tournament metadata"""
        return tournament_views.TournamentMetaView.tournament_meta_template(
            meta.asdict()
        )

    def menu(self):
        """Load the Tournament manager menu"""
        current_tournament_str = None
        if curr_tournament_meta := self._curr_tournament_meta():
            current_tournament_str = (
                f"Current tournament: {self._tournament_meta_str(curr_tournament_meta)}"
            )

        menu = Menu(
            title="Tournament Manager - Menu",
            cmdManager=self.main_app,
            text=current_tournament_str,
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
        if current_tournament_id := self.main_app.get_state("current_tournament_id"):
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
                self.main_app.set_state("current_tournament_id", tournament_id)
                tournament_meta_str = self._tournament_meta_str(tournament.metadata)
                self.status.notify_success(f"Tournament loaded: {tournament_meta_str}")
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

    def edit_tournament_info(self, tournament_id: str = None):
        """Edit tournament meta-data.
        Some fields may be editable or frozen, depending on the tournament's current status.
        """
        tournament_metadata = self._tournament_meta(tournament_id)
        if not tournament_metadata:
            return

        frozen_fields = self._tournament_meta_frozen_fields(tournament_metadata)

        v = tournament_views.TournamentMetaEditor(
            cmd_manager=self.main_app,
            title="Tournament Editor",
            data=tournament_metadata.asdict(),
            frozen_fields=frozen_fields,
            text=f"Edit tournament {self._tournament_meta_str(tournament_metadata)}",
            confirm_command=UpdateTournamentMetaCommand(app=self.main_app,
                                                        form_data=tournament_metadata.asdict())
        )
        self.main_app.view(v)

    def _tournament_meta_frozen_fields(
        self, tournament_metadata: TournamentMetaData
    ) -> list[str]:
        """Returns a list of fields that can't change in a tournament metadata."""
        frozen_fields = ["tournament_id", "data_file", "status", "end_date"]
        if tournament_metadata.status in ("running", "ended"):
            frozen_fields += ["start_date", "location", "turn_count"]
        return frozen_fields

    def update_tournament_meta(self, tournament_id: str, **kwargs):
        """Update tournament Metadata."""
        try:
            tournament_id = tournament_id or self._curr_tournament_id()
            tournament = self.tournament_repo.load_tournament(tournament_id)
            if not tournament:
                raise Exception("Not found")
        except Exception:
            self.status.notify_failure("Can't update: tournament data not found.")
            return
        if len(kwargs) == 0:
            self.status.notify_failure("Can't update: form data is empty.")

        frozen_fields = self._tournament_meta_frozen_fields(tournament.metadata)
        try:
            # start_date, "location", "turn_count", "description"
            if "start_date" not in frozen_fields:
                u_start_date = date.fromisoformat(kwargs.get("start_date"))
                tournament.set_start_date(u_start_date)
            if "location" not in frozen_fields:
                u_location = kwargs.get("location")
                tournament.set_location(u_location)
            if "turn_count" not in frozen_fields:
                u_turn_count = int(kwargs.get("turn_count"))
                tournament.set_turns(u_turn_count)
            if "description" not in frozen_fields:
                u_description = kwargs.get("description")
                tournament.set_description(u_description)
            if self.tournament_repo.store_tournament(tournament):
                t_str = self._tournament_meta_str(tournament.metadata)
                self.status.notify_success(f"Updated tournament: {t_str}")
        except ValueError:
            self.status.notify_failure("Failed to store changes: invalid data.")
            return
        except Exception as e:
            logger.error(e)
            self.status.notify_failure("Failed to store changes: unexpected error.")
