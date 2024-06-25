from datetime import date
from app.commands import commands
from app.controllers.controller_abc import BaseController, MainController
from app.models.player_model import PlayerRepository
from app.models.tournament_model import (
    Match,
    Round,
    TournamentMetaData,
    Tournament,
    TournamentRepository
)
from app.views.views_abc import SimpleView
from app.views.menu import Menu, MenuOption
from app.views.tournament import tournament_views
from app.views.tournament.register_player_tournament import (
    RegisterTournamentView,
    ConfirmPlayerIDView,
)
from app.views.player.player_views import PlayerListView
from app.controllers import player_manager
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
        self,
        app: commands.CommandManagerInterface,
        tournament_id: str = None,
        confirm_cmd: commands.CommandInterface = None,
    ) -> None:
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.load_tournament,
            tournament_id=tournament_id,
            confirm_cmd=confirm_cmd,
        )


class SelectTournamentCommand(commands.LaunchManagerCommand):
    def __init__(
        self,
        app: commands.CommandManagerInterface,
        tournament_id: str = None,
        confirm_cmd: commands.CommandInterface = None,
    ) -> None:
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.select_tournament,
            tournament_id=tournament_id,
            confirm_cmd=confirm_cmd,
        )


class ListTournamentsCommand(commands.LaunchManagerCommand):
    def __init__(self, app: commands.CommandManagerInterface, sort_by_date: bool = False) -> None:
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.list_tournaments,
            sort_by_date=sort_by_date
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


class StoreNewTournamentCommand(commands.LaunchManagerCommand):
    def __init__(self, app: commands.CommandInterface, form_data: dict = None):
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.store_new_tournament,
            **form_data,
        )


class UpdateTournamentMetaCommand(commands.LaunchManagerCommand):
    def __init__(self, app: commands.CommandInterface, form_data: dict = None):
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.update_tournament_meta,
            **form_data,
        )


class RegisterPlayerCommand(commands.LaunchManagerCommand):
    def __init__(
        self,
        app: commands.CommandInterface,
        tournament_id: str = None,
        player_id: str = None,
    ) -> None:
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.register_player,
            player_id=player_id,
            tournament_id=tournament_id,
        )


class RequirePlayerForRegistrationCommand(commands.LaunchManagerCommand):
    def __init__(
        self,
        app: commands.CommandManagerInterface,
        tournament_id: str = None,
        player_id: str = None,
        confirmed: bool = False,
    ) -> None:
        super().__init__(
            app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.require_player_id_for_registration,
            tournament_id=tournament_id,
            player_id=player_id,
            confirmed=confirmed,
        )


class ListRegisteredPlayersCommand(commands.LaunchManagerCommand):
    def __init__(
        self,
        app: commands.CommandInterface,
        tournament_id: str,
        sorted_by: str = None

    ):
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.list_registered_players,
            tournament_id=tournament_id,
            sorted_by=sorted_by
        )


class ListAvailablePlayersCommand(commands.LaunchManagerCommand):
    def __init__(
        self,
        app: commands.CommandInterface,
        tournament_id: str,
    ):
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.list_available_players,
            tournament_id=tournament_id,
        )


class TournamentInfoCommand(commands.LaunchManagerCommand):
    def __init__(
        self,
        app: commands.CommandInterface,
        tournament_id: str
    ):
        super().__init__(
            app=app,
            cls_or_obj=TournamentManager,
            method=TournamentManager.tournament_info,
            tournament_id=tournament_id
        )


class TournamentManagerBase(BaseController):
    """Manage Tournaments: create and run tournaments."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        tournament_repo: TournamentRepository,
        main_app: MainController,
    ):
        super().__init__()
        self.main_app: MainController = main_app
        self.tournament_repo: TournamentRepository = tournament_repo
        self.player_repo: PlayerRepository = player_repo

    def _curr_tournament_id(self) -> str:
        return self.main_app.get_state("current_tournament_id")

    def _curr_tournament_meta(self) -> TournamentMetaData:
        if curr_id := self._curr_tournament_id():
            return self.tournament_repo.find_tournament_metadata_by_id(curr_id)
        return None

    def _tournament_meta_str(self, meta: TournamentMetaData) -> str:
        """Return a simple string view of a tournament metadata"""
        return tournament_views.TournamentMetaView.tournament_meta_template(
            meta.asdict()
        )

    def _curr_tournament(self) -> Tournament:
        if tournament_id := self._curr_tournament_id():
            return self.tournament_repo.find_tournament_by_id(
                tournament_id=tournament_id
            )
        return None

    def _get_tournament(
        self, tournament_id: str, use_current: bool = True
    ) -> Tournament:
        """Retrieves a tournament from the repository after validating the tournament_id.

        If tournament_id, tries to read the current_tournament_id stored in the app's state.
        This behaviour is controlled by the use_current flag.

        Notify the user when tournament_id is not valid.
        """
        tournament = None
        try:
            if use_current and not tournament_id:
                tournament_id = self._curr_tournament_id()
            if not tournament_id:
                raise Exception("A tournament ID is required")
            tournament = self.tournament_repo.find_tournament_by_id(tournament_id)
            if not tournament:
                raise Exception(f"Tournament not found: {tournament_id}")
        except Exception as e:
            logger.error(e)
            self.status.notify_failure(f"Invalid tournament ID: {e}")
        return tournament

    def _match_data(self, match_list: list[tuple[int, Match]]):
        """returns a view of a list of matches as a dict,
        indexed by the matches index."""
        matches_data = {}
        for m, m_details in match_list:
            matches_data[m] = {
                "idx": m,
                "player1": m_details.player1().asdict(),
                "player2": m_details.player2().asdict(),
                "score_player1": m_details.player_score(m_details.player1().id()),
                "score_player2": m_details.player_score(m_details.player2().id()),
                "start_time": m_details.start_time,
                "end_time": m_details.end_time,
            }
        return matches_data

    def _tournament_round_data(self, round: Round) -> dict:
        """Returns a dict containing a round's data"""
        round_data = {
            "name": round.name,
            "matches": self._match_data(enumerate(round.matches)),
        }
        return round_data


class TournamentManager(TournamentManagerBase):
    """Manage Tournaments: create and run tournaments."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        tournament_repo: TournamentRepository,
        main_app: MainController,
    ):
        super().__init__(
            player_repo=player_repo, tournament_repo=tournament_repo, main_app=main_app
        )

    def default(self):
        """Launches the player manager: display the menu."""
        menu_command = commands.DisplayMenuCommand(
            app=self.main_app, cls_or_obj=TournamentManager, cycle=True
        )
        self.main_app.receive(menu_command)

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
                option_text="List Tournaments",
                command=ListTournamentsCommand(app=self.main_app),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Load Tournament",
                command=LoadTournamentCommand(app=self.main_app),
            )
        )
        if current_tournament_id := self._curr_tournament_id():
            menu.add_option(
                MenuOption(
                    option_text="View Tournament Info",
                    command=TournamentInfoCommand(app=self.main_app,
                                                  tournament_id=current_tournament_id)
                )
            )
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
                    option_text="List Current Participants",
                    command=ListRegisteredPlayersCommand(
                        app=self.main_app, tournament_id=current_tournament_id
                    ),
                )
            )
            if self._curr_tournament_meta().status == "open":
                menu.add_option(
                    MenuOption(
                        option_text="Register Player",
                        command=RegisterPlayerCommand(
                            app=self.main_app, tournament_id=current_tournament_id
                        ),
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

    def load_tournament(
        self, tournament_id: str = None, confirm_cmd: commands.CommandInterface = None
    ):
        """Load a tournament in memory and sets as current tournament
        for other operations.
        Doesn't change the confirm_cmd argument.
        """
        if not tournament_id:
            # Come back with a tournament ID...
            v = tournament_views.SelectTournamentIDView(
                cmd_manager=self.main_app,
                confirm_command=LoadTournamentCommand(
                    app=self.main_app, confirm_cmd=confirm_cmd
                ),
                list_command=[
                    LoadTournamentCommand(app=self.main_app, confirm_cmd=confirm_cmd),
                    ListTournamentsCommand(app=self.main_app),
                ],
            )
            self.main_app.view(v)
            return
        else:
            tournament = self._get_tournament(tournament_id=tournament_id)
            if not tournament:
                msg = "Failed to load tournament data."
                msg += "Please check the tournament ID and files in the tournament data folder."
                self.status.notify_failure(msg)
                return
            else:
                self.main_app.set_state("current_tournament_id", tournament_id)
                tournament_meta_str = self._tournament_meta_str(tournament.metadata)
                self.status.notify_success(f"Tournament loaded: {tournament_meta_str}")
                if confirm_cmd:
                    self.main_app.receive(confirm_cmd)

    def select_tournament(
        self, tournament_id: str = None, confirm_cmd: commands.CommandInterface = None
    ):
        """Select a tournament_id, but don't change the app's state current tournament_id.

        Instead, the selected tournament is passed to the confirm_cmd argument
        by setting a tournament_id parameter:
        `confirm_cmd.set_command_params(tournament_id=tournament_id)`
        """
        if not tournament_id:
            # Come back with a tournament ID...
            v = tournament_views.SelectTournamentIDView(
                cmd_manager=self.main_app,
                confirm_command=SelectTournamentCommand(
                    app=self.main_app, confirm_cmd=confirm_cmd
                ),
                list_command=[
                    SelectTournamentCommand(app=self.main_app, confirm_cmd=confirm_cmd),
                    ListTournamentsCommand(app=self.main_app),
                ],
            )
            self.main_app.view(v)
            return
        # validate the tournament id: try to load it
        tournament = self._get_tournament(tournament_id=tournament_id, use_current=False)
        if not tournament:
            # failure: try again
            self.main_app.receive(
                SelectTournamentCommand(app=self.main_app, confirm_cmd=confirm_cmd)
            )
        elif confirm_cmd:
            confirm_cmd.set_command_params(tournament_id=tournament.id())
            self.main_app.receive(confirm_cmd)

    def list_tournaments(self, sort_by_date: bool = False):
        """Display a list of all tournaments."""
        tournaments = self.tournament_repo.list_tournament_meta()
        if sort_by_date:
            tournaments.sort(key=lambda x: x.start_date)
        data = [m.asdict() for m in tournaments]
        v = tournament_views.TournamentsListView(
            cmd_manager=self.main_app, title="All Tournaments", tournament_list=data
        )
        self.main_app.view(v)

    def tournament_info(self, tournament_id: str):
        """Display info view on selected tournament
        """
        if not tournament_id:
            self.main_app.receive(
                SelectTournamentCommand(
                    app=self.main_app,
                    confirm_cmd=TournamentInfoCommand(app=self.main_app, tournament_id=None)
                )
            )
            return
        tournament_metadata = self._tournament_meta(tournament_id)
        if not tournament_metadata:
            return
        title = "Tournament Info"
        if tournament_id == self._curr_tournament_id():
            title = "Current Tournament Info"
        v = tournament_views.TournamentInfoView(
            title=title,
            tournament_data=tournament_metadata.asdict(),
            cmd_manager=self.main_app
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
            confirm_command=UpdateTournamentMetaCommand(
                app=self.main_app, form_data=tournament_metadata.asdict()
            ),
        )
        self.main_app.view(v)

    def _tournament_meta_frozen_fields(
        self, tournament_metadata: TournamentMetaData
    ) -> list[str]:
        """Returns a list of fields that can't change in a tournament metadata."""
        frozen_fields = ["tournament_id", "data_file", "status", "end_date"]
        if tournament_metadata.status in ("running", "ended"):
            frozen_fields += ["start_date", "location", "round_count"]
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
            # start_date, "location", "round_count", "description"
            if "start_date" not in frozen_fields:
                if d_str := kwargs.get("start_date"):
                    u_start_date = date.fromisoformat(d_str)
                    tournament.set_start_date(u_start_date)
            if "location" not in frozen_fields:
                u_location = kwargs.get("location")
                tournament.set_location(u_location)
            if "round_count" not in frozen_fields:
                u_round_count = int(kwargs.get("round_count"))
                tournament.set_rounds(u_round_count)
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

    def new_tournament(self):
        """Creates a new tournament."""
        v = SimpleView(cmd_manager=self.main_app, title="Create a new Tournament")
        frozen_fields = []
        v = tournament_views.TournamentMetaEditor(
            cmd_manager=self.main_app,
            title="Create a new Tournament",
            data=TournamentMetaData().asdict(),
            frozen_fields=frozen_fields,
            confirm_command=StoreNewTournamentCommand(
                app=self.main_app, form_data=TournamentMetaData().asdict()
            ),
        )
        self.main_app.view(v)

    def store_new_tournament(self, **kwargs):
        """Fills a new tournament instance with form data passed in the parameters,
        and stores in the repository.
        If successfull, the new tournament becomes the active tournament.
        """
        if len(kwargs) == 0:
            self.status.notify_failure("Can't update: form data is empty.")

        try:
            # start_date, "location", "round_count", "description"
            if d_str := kwargs.get("start_date"):
                u_start_date = date.fromisoformat(d_str)
            else:
                u_start_date = None
            u_location = kwargs.get("location") or None
            u_round_count = int(kwargs.get("round_count")) or None
            u_description = kwargs.get("description") or None
            tournament_meta = TournamentMetaData(
                start_date=u_start_date,
                location=u_location,
                description=u_description,
                round_count=u_round_count,
            )
            tournament = Tournament(metadata=tournament_meta)
            if self.tournament_repo.store_tournament(tournament):
                t_str = self._tournament_meta_str(tournament.metadata)
                self.status.notify_success(f"New tournament created: {t_str}")
                self.main_app.set_state("current_tournament_id", tournament.id())
        except ValueError:
            self.status.notify_failure("Failed to store changes: invalid data.")
            return
        except Exception as e:
            logger.error(e)
            self.status.notify_failure("Failed to store changes: unexpected error.")

    def register_player(self, tournament_id: str = None, player_id: str = None):
        """Register a player in a tournament.

        Tournament_id defaults to the current tournament.

        """
        player = None
        tournament = self._get_tournament(tournament_id=tournament_id)
        if tournament is None:
            return

        if tournament.status() != "open":
            self.status.notify_failure(
                f"This tournament is {tournament.status()} and does not accept new players."
            )
            return

        if not player_id:
            self.require_player_id_for_registration(tournament_id=tournament_id)
            return

        # Validate the player ID:
        # when validation fails, display an error message
        # and issue a command to try again with a different Player ID

        try:
            if player_id:
                player = self.player_repo.find_by_id(player_id)
            if not player:
                raise KeyError(f"Player not found ({player_id})")
            if tournament.player_is_registered(player.id()):
                raise ValueError(
                    f"Player {player} is already registered in tournament {tournament.id()}"
                )
        except Exception as e:
            self.status.notify_failure(f"Invalid player: {e}")
            fail_cmd = RegisterPlayerCommand(
                app=self.main_app, tournament_id=tournament.id()
            )
            self.main_app.receive(fail_cmd)
            return

        # At this stage, the player_id and tournament_id are validated,
        # and the user confirmed his choice.
        # Let's proceed with the actual registration
        reason = None
        try:
            if not tournament.add_participant(player):
                reason = f"Failed to add player {player.id()} to participants list in tournament {tournament.id()}."
                raise Exception(reason)
            # all checks passed, store the tournament,
            # display success message
            # and offer to register a new player.
            if self.tournament_repo.store_tournament(tournament=tournament):
                self.status.notify_success(
                    f"Player {player} joined tournament {tournament.id()}."
                )
                self.main_app.receive(
                    RegisterPlayerCommand(
                        app=self.main_app, tournament_id=tournament.id()
                    )
                )
                return
        except Exception as e:
            logger.error(f"Failed to update tournament after registering player: {e}")
            reason = str(e)
        reason = reason or "for an unexpected reason"
        self.status.notify_failure(f"Failed to register player {reason}.")

    def require_player_id_for_registration(
        self, tournament_id: str, player_id: str = None, confirmed: bool = False
    ):
        """Get a Player ID to register to a tournament.

        Asks for confirmation once a valid player ID has been selected,
        then proceeds to registration.
        """
        tournament = self._get_tournament(tournament_id or self._curr_tournament_id())
        if not player_id:
            # request a player ID.
            # help the user a bit:
            #
            # provide the list of players already registered,
            # and the list of available player IDs (ie not registered yet)

            player_id_form = RegisterTournamentView(
                cmd_manager=self.main_app,
                confirm_cmd=RequirePlayerForRegistrationCommand(
                    app=self.main_app, tournament_id=tournament.id()
                ),
                list_available_players_cmd=[
                    RequirePlayerForRegistrationCommand(
                        app=self.main_app, tournament_id=tournament.id()
                    ),
                    ListAvailablePlayersCommand(
                        app=self.main_app, tournament_id=tournament.id()
                    ),
                ],
                list_registered_players_cmd=[
                    RequirePlayerForRegistrationCommand(
                        app=self.main_app, tournament_id=tournament.id()
                    ),
                    ListRegisteredPlayersCommand(
                        app=self.main_app, tournament_id=tournament.id()
                    ),
                ],
                new_player_cmd=[
                    RequirePlayerForRegistrationCommand(
                        app=self.main_app, tournament_id=tournament.id()
                    ),
                    player_manager.RegisterPlayerCommand(app=self.main_app),
                ],
                cancel_cmd=None,
            )
            self.main_app.view(player_id_form)
            return

        player = None
        try:
            if player_id:
                player = self.player_repo.find_by_id(player_id)
            if not player:
                raise KeyError(f"Player not found: {player_id}")
            if tournament.player_is_registered(player.id()):
                raise ValueError(f"Player {player} is already registered.")

        except Exception as e:
            self.status.notify_failure(f"Can't register this player: {e}")
            self.main_app.receive(
                RequirePlayerForRegistrationCommand(
                    app=self.main_app, tournament_id=tournament.id()
                )
            )
            return

        if not confirmed:
            # Player ID is valid, still we'll ask the user to confirm the player
            # by displaying it's full details
            # if the user does not validate the player, ask for a new player ID
            v = ConfirmPlayerIDView(
                cmd_manager=self.main_app,
                playerdata=player.asdict(),
                tournament_id=tournament.id(),
                confirm_cmd=RegisterPlayerCommand(
                    app=self.main_app,
                    tournament_id=tournament.id(),
                    player_id=player.id(),
                ),
                abandon_cmd=RequirePlayerForRegistrationCommand(
                    app=self.main_app, tournament_id=tournament.id()
                ),
            )
            self.main_app.view(v)
            return

    def list_registered_players(self, tournament_id: str = None, sorted_by: str = None):
        """Display a list of players registered in a tournament.

        sorted_by: sort key (currently only 'alpha' is supported to sort by ascending player name)
        """
        if not tournament_id:
            # tournament ID is required.
            self.main_app.receive(
                SelectTournamentCommand(
                    app=self.main_app,
                    confirm_cmd=ListRegisteredPlayersCommand(
                        app=self.main_app,
                        tournament_id=None,
                        sorted_by=sorted_by
                    )
                )
            )
            return
        tournament = self._get_tournament(tournament_id=tournament_id)
        if not tournament:
            return
        registered_players_datalist = [p.asdict() for p in tournament.participants]
        if sorted_by == "alpha":
            registered_players_datalist.sort(
                key=lambda x: x.get("surname", "").upper() + x.get("name", "").capitalize()
                )
        v = PlayerListView(
            player_list=registered_players_datalist,
            title=f"Registered Players - tournament in {tournament.metadata.location}",
        )
        self.main_app.view(v)

    def list_available_players(self, tournament_id: str = None):
        """Display a list of players who are NOT registered yest in a tournament,
        and available for registration."""
        tournament_id = tournament_id or self._curr_tournament_id()
        tournament = self._get_tournament(tournament_id=tournament_id)
        available_players = self.player_repo.find_many(
            where=lambda pl: not tournament.player_is_registered(pl.id())
        )
        available_players_datalist = [p.asdict() for p in available_players]
        v = PlayerListView(
            player_list=available_players_datalist,
            title="Players available for registration",
        )
        self.main_app.view(v)
