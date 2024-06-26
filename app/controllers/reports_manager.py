from app.controllers.controller_abc import MainController
from app.commands.commands_abc import CommandManagerInterface, CommandInterface
from app.views.views_abc import RenderToFileContext
from app.commands.commands import (
    LaunchManagerCommand,
    DisplayMenuCommand,
    ExitCurrentCommand,
)
from app.views.menu import Menu, MenuOption
from app.models.player_model import PlayerRepository
from app.models.tournament_model import TournamentRepository
from app.controllers import player_manager, tournament_manager
from app.views.reports.tournament_reports import TournamentReportView, ExportToHTMLDialog
from app.views.html.reports import html_reports
from pathlib import Path
import logging

logger = logging.getLogger()


class TournamentReportCommand(LaunchManagerCommand):
    def __init__(self, app: CommandManagerInterface,
                 tournament_id: str = None,
                 export_as: str = None,
                 export_to: Path = None
                 ) -> None:
        super().__init__(app=app,
                         cls_or_obj=ReportsManager,
                         method=ReportsManager.tournament_rounds_report,
                         tournament_id=tournament_id,
                         export_as=export_as,
                         export_to=export_to)


class PlayersReportCommand(LaunchManagerCommand):
    def __init__(self,
                 app: CommandManagerInterface = None,
                 export_as: str = None,
                 export_to: Path = None
                 ) -> None:
        super().__init__(app=app,
                         cls_or_obj=ReportsManager,
                         method=ReportsManager.players_report,
                         export_as=export_as,
                         export_to=export_to)


class TournamentListReportCommand(LaunchManagerCommand):
    def __init__(self,
                 app: CommandManagerInterface = None,
                 export_as: str = None,
                 export_to: Path = None
                 ) -> None:
        super().__init__(app=app,
                         cls_or_obj=ReportsManager,
                         method=ReportsManager.tournament_list_report,
                         export_as=export_as,
                         export_to=export_to)


class TournamentInfoCommand(LaunchManagerCommand):
    def __init__(self,
                 tournament_id: str = None,
                 app: CommandManagerInterface = None,
                 export_as: str = None,
                 export_to: Path = None
                 ) -> None:
        super().__init__(app=app,
                         cls_or_obj=ReportsManager,
                         method=ReportsManager.tournament_info_report,
                         tournament_id=tournament_id,
                         export_as=export_as,
                         export_to=export_to)


class TournamentParticipantsReportCommand(LaunchManagerCommand):
    def __init__(self,
                 tournament_id: str = None,
                 app: CommandManagerInterface = None,
                 export_as: str = None,
                 export_to: Path = None
                 ) -> None:
        super().__init__(app=app,
                         cls_or_obj=ReportsManager,
                         method=ReportsManager.tournament_participants_report,
                         tournament_id=tournament_id,
                         export_as=export_as,
                         export_to=export_to)


class ExportToHTMLCommand(LaunchManagerCommand):
    def __init__(self,
                 app: CommandManagerInterface,
                 confirm_cmd: CommandInterface = None,
                 cancel_cmd: CommandInterface = None):
        super().__init__(app=app,
                         cls_or_obj=ReportsManager,
                         method=ReportsManager.export_to_html,
                         confirm_cmd=confirm_cmd,
                         cancel_cmd=cancel_cmd)


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
                command=PlayersReportCommand(app=self.main_app),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="List all tournaments",
                command=TournamentListReportCommand(
                    app=self.main_app
                ),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Tournament Info",
                command=TournamentInfoCommand(
                    app=self.main_app, tournament_id=None
                ),
            )
        )
        menu.add_option(
            MenuOption(
                option_text="Tournament Participants",
                command=TournamentParticipantsReportCommand(
                    app=self.main_app, tournament_id=None
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

    def export_to_html(self,
                       output_file: Path = None,
                       confirm_cmd: CommandInterface = None,
                       cancel_cmd: CommandInterface = None):
        """Prompts user if he wishes to export the current report to an HTML file.
        """
        if not output_file:
            v = ExportToHTMLDialog(cmd_manager=self.main_app,
                                   confirm_cmd=confirm_cmd,
                                   abandon_cmd=cancel_cmd)
            self.main_app.view(v)

    def tournament_list_report(self, export_to: Path = None, export_as: str = None):
        """Produce a report listing all tournaments registered in the database.
        Sorted by start date order.
        """
        if export_as == "html":
            #
            # Produce the html view and write to file
            try:
                tournaments = self.tournament_repo.list_tournament_meta()
                tournaments.sort(key=lambda x: x.start_date)
                data = [m.asdict() for m in tournaments]
                v = html_reports.TournamentListHTML(
                    title="All Tournaments",
                    tournament_list=data,
                    cmd_manager=self.main_app,
                    standalone=True
                )
                with RenderToFileContext(ofile=Path(export_to)):
                    v.render()
                self.status.notify_success(f"Wrote report to {export_to}")
            except Exception as e:
                logger.error(e, stack_info=True)
                self.status.notify_failure(f"Failed to write report: {e}")
        else:
            # first display the text report produced by the tournament_manager
            # then offer to export to an HTML file
            self.main_app.receive(
                ExportToHTMLCommand(
                    app=self.main_app,
                    confirm_cmd=TournamentListReportCommand(
                        app=self.main_app,
                        export_as="html"
                    )
                ))
            self.main_app.receive(
                tournament_manager.ListTournamentsCommand(app=self.main_app, sort_by_date=True)
            )

    def players_report(self, export_to: Path = None, export_as: str = None):
        """Produce a report listing all players registered in the database,
        sorted by alphabetic order.
        """
        if export_as == "html":
            #
            # Produce the html view and write to file
            try:
                player_data = [p.asdict() for p in self.player_repo.list_all()]
                player_data.sort(key=lambda x: x.get("surname", "").upper() + x.get("name", "").upper())
                v = html_reports.PlayersReportHTML(
                    title="Players List",
                    player_list=player_data,
                    cmd_manager=self.main_app,
                    standalone=True
                )
                with RenderToFileContext(ofile=Path(export_to)):
                    v.render()
                self.status.notify_success(f"Wrote report to {export_to}")
            except Exception as e:
                logger.error(e, stack_info=True)
                self.status.notify_failure(f"Failed to write report: {e}")
        else:
            # first display the text report produced by the tournament_manager
            # then offer to export to an HTML file
            self.main_app.receive(
                ExportToHTMLCommand(
                    app=self.main_app,
                    confirm_cmd=PlayersReportCommand(
                        app=self.main_app,
                        export_as="html"
                    )
                ))
            self.main_app.receive(
                player_manager.ListAllPlayersCommand(app=self.main_app)
            )

    def tournament_info_report(self, tournament_id: str = None, export_to: Path = None, export_as: str = None):
        """Output tournament Info, optionnally export as HTML"""
        if not tournament_id:
            # a tournament_id is required...
            self.main_app.receive(
                tournament_manager.SelectTournamentCommand(
                    app=self.main_app,
                    confirm_cmd=TournamentInfoCommand(app=self.main_app,
                                                      tournament_id=None,
                                                      export_as=export_as,
                                                      export_to=export_to)
                )
            )
            return
        if export_as == "html":
            #
            # Produce the html view and write to file
            try:
                tournament = self._get_tournament(tournament_id=tournament_id, use_current=False)

                v = html_reports.TournamentInfoHTML(
                    title="Tournament Info",
                    tournament_data=tournament.metadata.asdict(),
                    cmd_manager=self.main_app,
                    standalone=True
                )
                with RenderToFileContext(ofile=Path(export_to)):
                    v.render()
                self.status.notify_success(f"Wrote report to {export_to}")
            except Exception as e:
                logger.error(e, stack_info=True)
                self.status.notify_failure(f"Failed to write report: {e}")
        else:
            # first display the text report produced by the tournament_manager
            # then offer to export to an HTML file
            self.main_app.receive(
                ExportToHTMLCommand(
                    app=self.main_app,
                    confirm_cmd=TournamentInfoCommand(
                        tournament_id=tournament_id,
                        app=self.main_app,
                        export_as="html"
                    )
                ))
            self.main_app.receive(
                tournament_manager.TournamentInfoCommand(app=self.main_app, tournament_id=tournament_id)
            )

    def tournament_participants_report(self, tournament_id: str = None, export_to: Path = None, export_as: str = None):
        """Produce a report with participants of a tournament.
        """
        if not tournament_id:
            # come back with a valid tournament ID...
            self.main_app.receive(
                tournament_manager.SelectTournamentCommand(
                    app=self.main_app,
                    tournament_id=None,
                    confirm_cmd=TournamentParticipantsReportCommand(
                        app=self.main_app,
                        tournament_id=None
                    )
                )
            )
            return
        if export_as == "html":
            #
            # Produce the html view and write to file
            try:
                tournament = self._get_tournament(tournament_id=tournament_id, use_current=False)
                player_data = [p.asdict() for p in tournament.participants]
                player_data.sort(key=lambda x: x.get("surname", "").upper() + x.get("name", "").upper())
                title = f"Registered Players - tournament in {tournament.metadata.location}"
                v = html_reports.PlayersReportHTML(
                    title=title,
                    player_list=player_data,
                    cmd_manager=self.main_app,
                    standalone=True
                )
                with RenderToFileContext(ofile=Path(export_to)):
                    v.render()
                self.status.notify_success(f"Wrote report to {export_to}")
            except Exception as e:
                logger.error(e, stack_info=True)
                self.status.notify_failure(f"Failed to write report: {e}")
        else:
            # first display the text report produced by the tournament_manager
            # then offer to export to an HTML file
            self.main_app.receive(
                ExportToHTMLCommand(
                    app=self.main_app,
                    confirm_cmd=TournamentParticipantsReportCommand(
                        app=self.main_app,
                        export_as="html",
                        tournament_id=tournament_id
                    )
                ))
            self.main_app.receive(
                tournament_manager.ListRegisteredPlayersCommand(app=self.main_app, tournament_id=tournament_id)
            )

    def tournament_rounds_report(self, tournament_id: str = None, export_to: Path = None, export_as: str = None):
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
