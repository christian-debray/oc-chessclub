from app.controllers.controller_abc import MainController
from app.commands.commands_abc import CommandManagerInterface
from app.commands.commands import (
    LaunchManagerCommand,
    DisplayMenuCommand,
    ExitCurrentCommand,
)
from app.views.menu import Menu, MenuOption
from app.models.player_model import PlayerRepository
from app.models.tournament_model import TournamentRepository
from app.controllers import player_manager, tournament_manager
from app.views.reports.tournament_reports import TournamentReportView


class TournamentReportCommand(LaunchManagerCommand):
    def __init__(self, app: CommandManagerInterface,
                 tournament_id: str) -> None:
        super().__init__(app=app,
                         cls_or_obj=ReportsManager,
                         method=ReportsManager.tournament_rounds_report,
                         tournament_id=tournament_id)


class ReportsManager(tournament_manager.TournamentManagerBase):
    """Compile reports related to the chess club activity:

    liste de tous les joueurs par ordre alphabétique ;
    liste de tous les tournois ;
    nom et dates d’un tournoi donné ;
    liste des joueurs du tournoi par ordre alphabétique ;
    liste de tous les tours du tournoi et de tous les matchs du tour.
    """

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
        """Launches the Reports manager: display the menu."""
        menu_command = DisplayMenuCommand(
            app=self.main_app, cls_or_obj=ReportsManager, cycle=True
        )
        self.main_app.receive(menu_command)

    def menu(self):
        """Display the reports menu."""
        menu = Menu(title="Chess Club Reports", cmdManager=self.main_app)
        menu.add_option(
            MenuOption(
                option_text="List all players",
                command=player_manager.ListAllPlayersCommand(app=self.main_app),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="List all tournaments",
                command=tournament_manager.ListTournamentsCommand(
                    app=self.main_app, sort_by_date=True
                ),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Tournament Info",
                command=tournament_manager.TournamentInfoCommand(
                    app=self.main_app, tournament_id=None
                ),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Tournament Participants",
                command=tournament_manager.ListRegisteredPlayersCommand(
                    app=self.main_app, tournament_id=None, sorted_by="alpha"
                ),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Tournament Full Report",
                command=TournamentReportCommand(
                        app=self.main_app,
                        tournament_id=None
                    )
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Return to previous menu",
                alt_key="X",
                command=ExitCurrentCommand(self.main_app),
            )
        )

        self.main_app.view(menu)

    def tournament_rounds_report(self, tournament_id: str = None):
        """View details of all rounds in a tournament"""
        if not tournament_id:
            self.main_app.receive(
                tournament_manager.SelectTournamentCommand(
                    app=self.main_app,
                    tournament_id=None,
                    confirm_cmd=TournamentReportCommand(
                        app=self.main_app,
                        tournament_id=None
                    )
                )
            )
            return
        tournament = self._get_tournament(tournament_id)
        if not tournament:
            return
        tournament_data = {
            "metadata": tournament.metadata.asdict(),
            "rounds": []
        }
        if tournament.has_started():
            for round in tournament.rounds:
                if round is not None:
                    tournament_data["rounds"].append(self._tournament_round_data(round))
        v = TournamentReportView(tournament_data=tournament_data)
        self.main_app.view(v)
