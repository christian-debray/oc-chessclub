from app.views.views_abc import BaseView, CommandManagerInterface
from app.views import dialogs
from app.views.tournament.running_tournament import RoundView
from app.views.tournament.tournament_views import TournamentInfoView
from app.helpers.text_ui import prompt_v
from pathlib import Path
from app.helpers.validation import is_writable_path


class ExportToHTMLDialog(dialogs.Dialog):
    def __init__(self,
                 cmd_manager: CommandManagerInterface,
                 title: str = None,
                 text: str = None,
                 confirm_cmd: dialogs.CommandInterface = None,
                 abandon_cmd: dialogs.CommandInterface = None):
        super().__init__(cmd_manager=cmd_manager,
                         title=title,
                         text=text,
                         confirm_cmd=confirm_cmd,
                         abandon_cmd=abandon_cmd)
        if not self.text:
            self.text = "Export this report to HTML ?"
            self.text += "\nIf yes, enter the path to an ouptut file."
            self.text += "\nPress Enter of <ctrl>+D otherwise."
            cwd = Path('.').resolve()
            self.text += f"\n(current working directory: {cwd})"

    def render(self):
        """Prompts user if he wants to export to HTML,
        and if so, prompts for a file name.
        """
        print(self.text)
        if export_file := prompt_v(prompt="html ouptut file path > ", validator=is_writable_path, skip_blank=True):
            if self.confirm_cmd:
                self.confirm_cmd.set_command_params(export_to=export_file)
                self.issuecmd(self.confirm_cmd)


class TournamentReportView(BaseView):
    """Displays a full report on a tournament."""

    def __init__(
        self,
        tournament_data: dict,
        cmd_manager: CommandManagerInterface = None,
        title: str = "Tournament Review",
    ):
        super().__init__(cmd_manager=cmd_manager, title=title)
        self.tournament_data = tournament_data

    def render(self):
        super().render()
        if metadata := self.tournament_data.get("metadata"):
            print(TournamentInfoView.tournament_view_tpl(data=metadata))
        rounds: list[dict] = self.tournament_data.get("rounds", [])
        if len(rounds) > 0:
            print("\nRound details")
            print("=============\n")
            for round_data in rounds:
                if not round_data:
                    continue
                round_title = round_data.get("name") + " - Matches"
                print("\n"+round_title)
                print("="*len(round_title)+"\n")
                print(RoundView.matches_table_template(round_data.get("matches", {})))
        elif (self.tournament_data.get("metadata", {}).get("status") == "open"):
            print("(Tournament has not started yet, no round details available)")
