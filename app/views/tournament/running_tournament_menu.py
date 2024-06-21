from app.commands.commands_abc import CommandManagerInterface
from app.views.menu import Menu, MenuOption
from app.views.tournament.tournament_views import TournamentDetailsView


class RunningTournamentMenu(Menu):
    def __init__(self,
                 title: str = None,
                 text: str = None,
                 options: list[MenuOption] = None,
                 cmdManager: CommandManagerInterface = None,
                 clear_scr: bool = False,
                 **kwargs):
        super().__init__(title, text, options, cmdManager, clear_scr)
        self.tournament_details = TournamentDetailsView(
            cmd_manager=self.cmd_manager,
            **kwargs
        )

    def render(self):
        self.text = self.tournament_details.details_template()
        super().render()
