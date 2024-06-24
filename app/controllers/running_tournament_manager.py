from app.commands import commands
from app.controllers.controller_abc import MainController
from app.models.player_model import PlayerRepository
from app.models.tournament_model import TournamentRepository
from app.controllers import tournament_manager
from app.views.menu import Menu, MenuOption
from app.views.tournament.running_tournament import RunningTournamentMenu, RoundView
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

    def list_matches(self):
        tournament = self._curr_tournament()
        round = tournament.current_turn()

        matches_data = []
        for m, m_details in enumerate(round.matches):
            matches_data.append(
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
        round_data = {"name": round.name, "matches": matches_data}
        v = RoundView(cmd_manager=self.main_app, round_data=round_data)
        self.main_app.view(v)
