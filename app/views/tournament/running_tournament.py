from datetime import datetime, date
from app.commands.commands_abc import CommandManagerInterface, CommandInterface
from app.views.menu import Menu, MenuOption
from app.views.tournament.tournament_views import TournamentDetailsView
from app.views.views_abc import BaseView
from app.helpers.string_formatters import format_table, formatdate
from app.helpers.text_ui import prompt_v
from app.helpers.validation import is_valid_datetime, is_valid_time
import logging

logger = logging.getLogger()


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
        match_list: dict[int, dict] = self.round_data.get("matches", {})
        print(self.matches_table_template(match_list))

    @staticmethod
    def matches_table_template(match_list: dict[int, dict]) -> str:
        rows = [["idx", "player 1", "player 2", "status", "started", "ended"]]
        for m_idx, m_data in match_list.items():
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
        return table


class SelectMatchForm(BaseView):
    """Prompts the user for a match index.
    """
    def __init__(self,
                 cmd_manager: CommandManagerInterface,
                 round_data: dict,
                 confirm_cmd: CommandInterface = None,
                 abandon_cmd: CommandInterface = None):
        super().__init__(
            cmd_manager=cmd_manager, title=None, text=None, clear_scr=False
        )
        self.round_data = round_data
        self.title = f"Select a Match in round {round_data.get('name')}"
        self.round_view = RoundView(cmd_manager=self.cmd_manager, round_data=round_data)
        self.confirm_cmd = confirm_cmd
        self.abandon_cmd = abandon_cmd

    def render(self):
        super().render()
        print(RoundView.matches_table_template(self.round_data.get('matches', {})))
        indexes = [int(i)+1 for i in self.round_data.get("matches", {}).keys()]
        choice = prompt_v(prompt="To select a match enter its index\nMatch index > ",
                          validator=lambda x: str(x).isdecimal() and int(x) in indexes,
                          skip_blank=True)
        logger.debug(f"User selected {choice}")
        if choice is None:
            self.issuecmd(self.abandon_cmd)
        elif self.confirm_cmd:
            self.confirm_cmd.set_command_params(match_idx=int(choice) - 1)
            self.issuecmd(self.confirm_cmd)


class StartMatchForm(BaseView):
    def __init__(self,
                 cmd_manager: CommandManagerInterface,
                 pending_matches_data: dict,
                 confirm_cmd: CommandInterface = None,
                 cancel_cmd: CommandInterface = None):
        super().__init__(cmd_manager=cmd_manager, title="Start a Match",
                         text="Select a match to start and set the start date and time.",
                         clear_scr=True)
        self.pending_matches_data = pending_matches_data
        self.confirm_cmd = confirm_cmd
        self.cancel_cmd = cancel_cmd

    def render(self):
        super().render()
        print(RoundView.matches_table_template(self.pending_matches_data))
        indexes = [int(i)+1 for i in self.pending_matches_data.keys()]
        match_idx = prompt_v(
            prompt="To select a match enter its index\nMatch index > ",
            validator=lambda x: str(x).isdecimal() and int(x) in indexes,
            skip_blank=True)
        if match_idx is None:
            self.issuecmd(self.cancel_cmd)
            return
        start_time = datetime.now()
        print(f"Match start time defaults to current time: ({start_time.strftime("%d/%m/%Y %H:%M:%S")}")
        prompt_str = "hit <Enter> to use default or set custom time ([YYYY-MM-DD ]HH:MM:SS):\nStart Time > "
        if u_start_time := prompt_v(prompt=prompt_str,
                                    validator=lambda x: is_valid_datetime(x) or is_valid_time(x),
                                    skip_blank=True):
            if is_valid_datetime(u_start_time):
                start_time = datetime.fromisoformat(u_start_time)
            else:
                today = date.today()
                start_time = datetime.fromisoformat(f"{today.isoformat()} {u_start_time}")
        print(start_time)

        if self.confirm_cmd:
            self.confirm_cmd.set_command_params(match_idx=int(match_idx)-1, start_time=start_time)
            self.issuecmd(self.confirm_cmd)
