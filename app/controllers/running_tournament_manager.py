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
                option_text="Return to previous menu",
                alt_key="X",
                command=commands.ExitCurrentCommand(self.main_app),
            )
        )
        self.main_app.view(menu)
