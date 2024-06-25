from app.views.views_abc import BaseView, CommandManagerInterface
from app.views.tournament.running_tournament import RoundView
from app.views.tournament.tournament_views import TournamentInfoView


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
