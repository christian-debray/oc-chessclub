from app.commands import commands
from app.controllers.controller_abc import BaseController, MainController
from app.models.player_model import PlayerRepository
from app.models.tournament_model import (
    TournamentRepository,
    TournamentMetaData,
    Tournament,
)
from app.controllers.tournament_manager import TournamentManagerBase
from app.views.menu import Menu, MenuOption
from app.views.tournament.running_tournament_menu import RunningTournamentMenu
import logging

logger = logging.getLogger()


class RunningTournamentManager(TournamentManagerBase):
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
                **tournament_data
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
                tournament_data["current_turn_idx"] = current_tournament.current_turn_idx + 1
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

