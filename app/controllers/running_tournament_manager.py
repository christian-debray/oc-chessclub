from datetime import datetime
from app.commands import commands
from app.commands.commands_abc import CommandInterface
from app.controllers.controller_abc import MainController
from app.models.player_model import PlayerRepository
from app.models.tournament_model import TournamentRepository, Turn, Match
from app.controllers import tournament_manager
from app.views.menu import Menu, MenuOption
from app.views.tournament.running_tournament import (
    RunningTournamentMenu,
    RoundView,
    SelectMatchForm,
    StartMatchForm
)
import logging

logger = logging.getLogger()


class StartNextRoundCommand(commands.LaunchManagerCommand):
    def __init__(self, app: commands.CommandManagerInterface, **kwargs) -> None:
        super().__init__(
            app=app,
            cls_or_obj=RunningTournamentManager,
            method=RunningTournamentManager.start_next_round,
            **kwargs,
        )


class ListMatchesCommand(commands.LaunchManagerCommand):
    def __init__(self, app: commands.CommandManagerInterface, **kwargs) -> None:
        super().__init__(
            app=app,
            cls_or_obj=RunningTournamentManager,
            method=RunningTournamentManager.list_matches,
            **kwargs,
        )


class SelectMatchCommand(commands.LaunchManagerCommand):
    def __init__(
        self,
        app: commands.CommandManagerInterface,
        match_idx: int = None,
        round_idx: int = None,
        tournament_id: str = None,
        match_list: list[tuple[int, Match]] = None,
        success_cmd: CommandInterface = None,
        failure_cmd: CommandInterface = None,
    ) -> None:
        super().__init__(
            app,
            cls_or_obj=RunningTournamentManager,
            method=RunningTournamentManager.select_match,
            match_idx=match_idx,
            round_idx=round_idx,
            tournament_id=tournament_id,
            match_list=match_list,
            success_cmd=success_cmd,
            failure_cmd=failure_cmd,
        )


class StartMatchCommand(commands.LaunchManagerCommand):
    def __init__(
        self,
        app: commands.CommandManagerInterface,
        match_idx: int = None,
        start_time: datetime = None,
        tournament_id: str = None,
    ) -> None:
        super().__init__(
            app,
            cls_or_obj=RunningTournamentManager,
            method=RunningTournamentManager.start_match,
            match_idx=match_idx,
            start_time=start_time,
            tournament_id=tournament_id,
        )


class RunningTournamentManager(tournament_manager.TournamentManagerBase):
    """Manage turns and matches of a running tournament."""

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
            app=self.main_app, cls_or_obj=RunningTournamentManager, cycle=True
        )
        self.main_app.receive(menu_command)

    def menu(self):
        """Load the Tournament manager menu"""
        current_tournament = self._curr_tournament()
        if not current_tournament:
            menu = Menu(
                title="Run a Tournament - Menu",
                cmdManager=self.main_app,
                text="No current tournament selected.",
            )
        else:
            tournament_data = self._curr_tournament_data()
            menu = RunningTournamentMenu(
                title="Run a Tournament - Menu",
                cmdManager=self.main_app,
                **tournament_data,
            )
            menu.add_option(
                MenuOption(
                    option_text="List participants",
                    command=tournament_manager.ListRegisteredPlayersCommand(
                        app=self.main_app, tournament_id=current_tournament.id()
                    ),
                )
            )
            if current_tournament.can_start() and current_tournament.status == "open":
                menu.add_option(
                    MenuOption(
                        option_text="Start this tournament",
                        command=StartNextRoundCommand(app=self.main_app),
                    )
                )
            elif current_tournament.can_start():
                menu.add_option(
                    MenuOption(
                        option_text="Start next round",
                        command=StartNextRoundCommand(app=self.main_app),
                    )
                )
            elif current_tournament.status() == "running":
                menu.add_option(
                    MenuOption(
                        option_text="list matches",
                        command=ListMatchesCommand(app=self.main_app),
                    )
                )
                if current_tournament.has_pending_matches():
                    menu.add_option(
                        MenuOption(
                            option_text="Start a match",
                            command=StartMatchCommand(
                                app=self.main_app,
                                match_idx=None,
                                start_time=None,
                                tournament_id=current_tournament.id(),
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

    def _curr_tournament_data(self) -> dict:
        """Returns a view of the current tournament as dict
        with an overview of the tournament's current state."""
        if current_tournament := self._curr_tournament():
            tournament_data = current_tournament.metadata.asdict()
            tournament_data["participants_count"] = len(current_tournament.participants)
            if current_turn := current_tournament.current_turn():
                tournament_data["current_turn_idx"] = (
                    current_tournament.current_turn_idx + 1
                )
                tournament_data["current_turn_name"] = current_turn.name
                if current_turn.has_ended():
                    tournament_data["current_turns_status"] = "Ended"
                elif current_turn.has_started():
                    tournament_data["current_turns_status"] = "Running"
                else:
                    tournament_data["current_turns_status"] = "Pending"
            return tournament_data
        else:
            return {}

    def start_next_round(self):
        tournament = self._curr_tournament()
        if new_turn := tournament.start_next_turn():
            self.status.notify_success(f"Round {new_turn} has started !")
        else:
            self.status.notify_failure("Couldn't start next round !")

    def list_matches(self, round_idx: int = None, tournament_id: str = None):
        try:
            tournament = (
                self._curr_tournament()
                if tournament_id is None
                else self._get_tournament(tournament_id)
            )
            round = (
                tournament.current_turn()
                if round_idx is None
                else tournament.turns[round_idx]
            )
        except Exception as e:
            logger.log(e)
            self.status.notify_failure(f"Can't list matches: {e}")
            return
        round = tournament.current_turn()
        v = RoundView(
            cmd_manager=self.main_app, round_data=self._tournament_round_data(round)
        )
        self.main_app.view(v)

    def _match_data(self, match_list: list[tuple[int, Match]]):
        """returns a view of a list of matches as a dict,
        indexed by the matches index."""
        matches_data = {}
        for m, m_details in match_list:
            matches_data[m] = (
                {
                    "idx": m,
                    "player1": m_details.player1().asdict(),
                    "player2": m_details.player2().asdict(),
                    "score_player1": m_details.player_score(m_details.player1().id()),
                    "score_player2": m_details.player_score(m_details.player2().id()),
                    "start_time": m_details.start_time,
                    "end_time": m_details.end_time,
                }
            )
        return matches_data

    def _tournament_round_data(self, round: Turn) -> dict:
        """Returns a dict containing a round's data"""
        round_data = {"name": round.name, "matches": self._match_data(enumerate(round.matches))}
        return round_data

    def start_match(
        self,
        match_idx: int = None,
        start_time: datetime = None,
        tournament_id: str = None,
    ):
        """Starts a pending match."""
        tournament_id = tournament_id or self._curr_tournament_id()
        tournament = self._get_tournament(tournament_id)
        if not tournament:
            logger.error(f"Tournament not found: id={tournament_id}")
            return
        if match_idx is None:
            logger.debug("Match index is required, redirect to selectMatch")
            form = StartMatchForm(
                cmd_manager=self.main_app,
                pending_matches_data=self._match_data(tournament.pending_matches()),
                confirm_cmd=StartMatchCommand(
                    app=self.main_app,
                    tournament_id=tournament.id()
                )
            )
            self.main_app.view(form)
            return
        logger.debug(f"Starting match {match_idx}")
        try:
            match_idx = int(match_idx)
            if match := tournament.start_a_match(match_index=match_idx, start_time=start_time):
                if self.tournament_repo.store_tournament(tournament):
                    self.status.notify_success(
                        f"Started match {match_idx+1}: {match.player1()} vs {match.player2()}"
                    )
                else:
                    raise Exception("Failed to start match for an unexpected reason.")
        except Exception as e:
            logger.error(e)
            self.status.notify_failure(f"Can't start match {match_idx+1}: {e}")

    def select_match(
        self,
        match_idx: int,
        round_idx: int,
        tournament_id: str = None,
        match_list: list[tuple[int, Match]] = None,
        success_cmd: CommandInterface = None,
        failure_cmd: CommandInterface = None
    ):
        """Selects a match in a round"""
        if not tournament_id:
            tournament = self._curr_tournament()
        else:
            tournament = self._get_tournament(tournament_id)

        # get the tournament object
        if not tournament:
            logger.error(
                f"Can't select a match when no current tournament is set (tournament_id='{tournament_id}')"
            )
            self.status.notify_failure(
                "Can't select a match when no current tournament is set."
            )
            if failure_cmd:
                self.main_app.receive(failure_cmd)
            return

        # get the round object
        try:
            round = (
                tournament.turns[round_idx]
                if round_idx is not None
                else tournament.current_turn()
            )
        except Exception as e:
            logger.error(e, stack_info=True)
            self.status.notify_failure(f"Failed to select a match: {e}")
            if failure_cmd:
                self.main_app.receive(failure_cmd)

        if match_list is None:
            round_data = self._tournament_round_data(round)
        else:
            round_data = {"name": round.name, "matches": self._match_data(match_list)}
        if match_idx is None:
            logger.debug("Match idx is required, send form to promt user")
            # send form to select a match index
            form = SelectMatchForm(
                cmd_manager=self.main_app,
                round_data=round_data,
                confirm_cmd=SelectMatchCommand(
                    app=self.main_app,
                    match_idx=None,
                    round_idx=round_idx,
                    tournament_id=tournament.id(),
                    match_list=match_list,
                    success_cmd=success_cmd,
                    failure_cmd=failure_cmd,
                ),
                # confirm_cmd=success_cmd,
                abandon_cmd=failure_cmd,
            )
            self.main_app.view(form)
            return

        # check match index is valid
        logger.debug(f"Received Match idx = {match_idx}")
        if (str(match_idx)).isnumeric() and int(match_idx) in range(
            0, len(round.matches)
        ):
            match_idx = int(match_idx)
            logger.debug(f"   Match idx = {match_idx}, is valid.")
            self.status.display_status_message(f"Selected match {match_idx+1}")
            if success_cmd:
                logger.debug("dispatch to success_cmd")
                success_cmd.set_command_params(match_idx=match_idx)
                self.main_app.receive(success_cmd)
            return
        else:
            logger.debug(f"   Match idx = {match_idx}, is NOT valid.")
            # require a new, valid match index from user
            self.status.notify_failure("Not a valid match index")
            self.main_app.receive(
                SelectMatchCommand(
                    app=self.main_app,
                    match_idx=None,
                    round_idx=round_idx,
                    tournament_id=tournament.id(),
                    match_list=match_list,
                    success_cmd=success_cmd,
                    failure_cmd=failure_cmd,
                )
            )
