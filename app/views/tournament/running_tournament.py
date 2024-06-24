from app.commands.commands_abc import CommandManagerInterface
from app.views.menu import Menu, MenuOption
from app.views.tournament.tournament_views import TournamentDetailsView
from app.views.views_abc import BaseView
from app.helpers.string_formatters import format_table, formatdate


class RunningTournamentMenu(Menu):
    def __init__(
        self,
        title: str = None,
        text: str = None,
        options: list[MenuOption] = None,
        cmdManager: CommandManagerInterface = None,
        clear_scr: bool = False,
        **kwargs,
    ):
        super().__init__(title, text, options, cmdManager, clear_scr)
        self.tournament_details = TournamentDetailsView(
            cmd_manager=self.cmd_manager, **kwargs
        )

    def render(self):
        self.text = self.tournament_details.details_template()
        super().render()


class RoundView(BaseView):
    """List all matches and their state in a round."""

    def __init__(self, cmd_manager: CommandManagerInterface, round_data: dict):
        super().__init__(
            cmd_manager=cmd_manager, title=None, text=None, clear_scr=False
        )
        self.round_data = round_data
        self.title = f"Matches in round {round_data.get('name')}"

    def render(self):
        super().render()
        match_list: list[dict] = self.round_data.get("matches", [])
        rows = [["idx", "player 1", "player 2", "status", "started", "ended"]]
        for m_idx, m_data in enumerate(match_list):
            player1: dict[str, str] = m_data.get("player1")
            player2: dict[str, str] = m_data.get("player2")
            player1_str = f"{player1.get("surname").upper()} {player1.get("name").capitalize()}"
            player2_str = f"{player2.get("surname").upper()} {player2.get("name").capitalize()}"
            rows.append(
                [
                    f"{(m_idx+1):>3}",
                    f"{player1_str}\n{player1.get("national_player_id")}\n{m_data.get("score_player1")}",
                    f"{player2_str}\n{player2.get("national_player_id")}\n{m_data.get("score_player2")}",
                    (
                        "pending"
                        if m_data.get("start_time") is None
                        else ("running" if m_data.get("end_time") is None else "ended")
                    ),
                    formatdate(m_data.get("start_time"), "%d/%m/%Y %H:%M:%S", "-"),
                    formatdate(m_data.get("end_time"), "%d/%m/%Y %H:%M:%S", "-"),
                ]
            )
        table = format_table(rows)
        print(table)
