from app.commands.commands_abc import CommandManagerInterface
from yattag import Doc, indent
from app.views.html.base_html import HTMLBaseView
from app.helpers.string_formatters import formatdate


class PlayersReportHTML(HTMLBaseView):
    """Render Player list as HTML"""
    def __init__(self,
                 player_list: list[dict],
                 title: str = None,
                 cmd_manager: CommandManagerInterface = None,
                 standalone: bool = False):
        super().__init__(cmd_manager=cmd_manager)
        self.player_list = player_list
        self.title = title
        self.standalone = standalone

    def render(self):
        title_tag = "h1" if self.standalone else "h2"
        markup = self.player_list_tpl(self.player_list, self.title, title_tag)
        if not self.standalone:
            print(indent(markup))
        else:
            print(self.document(markup))

    @staticmethod
    def player_list_tpl(player_list: list[dict], title: str = None, title_tag="h1"):
        """Renders a list of players as an HTML table
        """
        doc, tag, text, line = Doc().ttl()

        if title:
            doc.line(tag_name=title_tag, text_content=title)
        with tag("table"):
            line("caption", f"{len(player_list)} players")
            with tag("thead"):
                with tag("tr"):
                    line("th", "Player ID")
                    line("th", "Name")
                    line("th", "Birthdate")
            with tag("tbody"):
                for row in player_list:
                    with tag("tr"):
                        line("td", row.get("national_player_id"))
                        line("td", f"{row.get('surname', "-").upper()} {row.get('name', "-").capitalize()}")
                        line("td", formatdate(row.get('birthdate'), "%d/%m/%Y", "-"))
        return doc.getvalue()


class TournamentInfoHTML(HTMLBaseView):
    """Render tournament infos as HTML"""
    def __init__(self,
                 tournament_data: dict,
                 title: str = None,
                 cmd_manager: CommandManagerInterface = None,
                 standalone: bool = False):
        super().__init__(cmd_manager=cmd_manager)
        self.tournament_data = tournament_data
        self.title = title
        self.standalone = standalone

    def render(self):
        title_tag = "h1" if self.standalone else "h2"
        markup = self.tournament_view_tpl(self.tournament_data, self.title, title_tag)
        if not self.standalone:
            print(indent(markup))
        else:
            print(self.document(markup))

    @staticmethod
    def tournament_view_tpl(data: dict, title: str = None, title_tag: str = "h1") -> str:
        """Returns the tournament data as an HTML5 list
        """
        start_date_tpl = formatdate(d=data.get("start_date"), fmt="%d/%m/%Y", empty="")
        end_date_tpl = formatdate(d=data.get("end_date"), fmt="%d/%m/%Y", empty="")
        dates_tpl = ""
        if data.get('status') == "open":
            if start_date_tpl:
                dates_tpl += f"scheduled on {start_date_tpl}"
            else:
                dates_tpl += "not scheduled yet"
        elif data.get('status') == "running":
            dates_tpl += f" started on {start_date_tpl}"
        elif data.get('status') == "ended":
            dates_tpl += f"from {start_date_tpl} to {end_date_tpl}"
        else:
            dates_tpl += " ???"
        #
        # now produce the HTML
        #
        list_data = [
            ("Tournament ID", data.get('tournament_id')),
            ("Location", data.get('location', "(not set)")),
            ("Dates", dates_tpl),
            ("Status", data.get('status')),
            ("Rounds", data.get("round_count")),
            ("Description", data.get("description"))
        ]
        doc, tag, text, line = Doc().ttl()
        if title:
            doc.line(tag_name=title_tag, text_content=title)
        with tag("ul"):
            for dt, dd in list_data:
                with tag("li"):
                    line("strong", f"{dt}:")
                    text(f" {dd}")
        return doc.getvalue()


class TournamentListHTML(HTMLBaseView):
    """Render Tournament list as HTML"""
    def __init__(self,
                 tournament_list: list[dict],
                 title: str = None,
                 cmd_manager: CommandManagerInterface = None,
                 standalone: bool = False):
        super().__init__(cmd_manager=cmd_manager)
        self.tournament_list = tournament_list
        self.title = title
        self.standalone = standalone

    def render(self):
        title_tag = "h1" if self.standalone else "h2"
        markup = self.tournament_list_tpl(self.tournament_list, self.title, title_tag)
        if not self.standalone:
            print(indent(markup))
        else:
            print(self.document(markup))

    @staticmethod
    def tournament_list_tpl(tournament_list: list[dict], title: str = None, title_tag="h1"):
        """Renders a list of players as an HTML table
        """
        doc, tag, text, line = Doc().ttl()
        if title:
            doc.line(tag_name=title_tag, text_content=title)
        with tag("table"):
            line("caption", f"{len(tournament_list)} tournaments")
            with tag("thead"):
                with tag("tr"):
                    line("th", "Tournament ID")
                    line("th", "Location")
                    line("th", "Status")
                    line("th", "Start date")
                    line("th", "End date")
            with tag("tbody"):
                for row in tournament_list:
                    with tag("tr"):
                        line("td", row.get('tournament_id'))
                        line("td", row.get('location'))
                        line("td", row.get('status'))
                        line("td", formatdate(d=row.get("start_date"), fmt="%d/%m/%Y", empty="-"))
                        line("td", formatdate(d=row.get("end_date"), fmt="%d/%m/%Y", empty="-"))
        return doc.getvalue()


class RoundDetailsHTML(HTMLBaseView):
    """Render details of a tournament round as HTML"""
    def __init__(self,
                 round_data: dict,
                 title: str = None,
                 cmd_manager: CommandManagerInterface = None,
                 standalone: bool = False):
        super().__init__(cmd_manager=cmd_manager)
        self.round_data: dict = round_data
        self.round_name: str = round_data.get("name")
        self.matches: list[dict] = round_data.get("matches", [])
        self.title = title
        self.standalone = standalone

    def render(self):
        title_tag = "h1" if self.standalone else "h2"
        markup = self.round_tpl(match_list=self.round_data, tile=self.title or self.round_name, title_tag=title_tag)
        if not self.standalone:
            print(indent(markup))
        else:
            print(self.document(markup))

    @staticmethod
    def round_tpl(match_list: list[dict], title: str = None, title_tag="h1"):
        """Renders the matches of round as an HTML table
        """
        doc, tag, text, line = Doc().ttl()
        if title:
            doc.line(tag_name=title_tag, text_content=title)
        with tag("table"):
            line("caption", f"{len(match_list)} matches")
            with tag("thead"):
                with tag("tr"):
                    line("th", "idx")
                    line("th", "player 1")
                    line("th", "player 2")
                    line("th", "status")
                    line("th", "started")
                    line("th", "ended")
            with tag("tbody"):
                for m_idx, m_data in match_list.items():
                    player1: dict[str, str] = m_data.get("player1")
                    player2: dict[str, str] = m_data.get("player2")
                    player1_str = f"{player1.get("surname").upper()} {player1.get("name").capitalize()}"
                    player1_tpl = f"{player1_str}\n{player1.get("national_player_id")}\n{m_data.get("score_player1")}"
                    player2_str = f"{player2.get("surname").upper()} {player2.get("name").capitalize()}"
                    player2_tpl = f"{player2_str}\n{player2.get("national_player_id")}\n{m_data.get("score_player2")}"
                    status_str = "pending" if m_data.get("start_time") is None\
                        else ("running" if m_data.get("end_time") is None else "ended")
                    with tag("tr"):
                        line("td", str(m_idx+1))
                        line("td", player1_tpl)
                        line("td", player2_tpl)
                        line("td", status_str)
                        line("td", formatdate(m_data.get("start_time"), "%d/%m/%Y %H:%M:%S", "-"))
                        line("td", formatdate(m_data.get("end_time"), "%d/%m/%Y %H:%M:%S", "-"))
        return doc.getvalue()


class TournamentReportHTML(HTMLBaseView):
    """Render Tournament full report as HTML"""
    def __init__(self,
                 tournament_data: dict,
                 title: str = None,
                 cmd_manager: CommandManagerInterface = None,
                 standalone: bool = False):
        super().__init__(cmd_manager=cmd_manager)
        self.tournament_data = tournament_data
        self.title = title
        self.standalone = standalone

    def render(self):
        title_tag = "h1" if self.standalone else "h2"
        markup = self.tournament_tpl(self.tournament_data, self.title, title_tag)
        if not self.standalone:
            print(indent(markup))
        else:
            print(self.document(markup))

    @staticmethod
    def tournament_tpl(tournament_data: dict, title: str = None, title_tag="h1"):
        """Renders a list of players as an HTML table
        """
        doc, tag, text, line = Doc().ttl()
        if title:
            doc.line(tag_name=title_tag, text_content=title)
        #
        # meta info
        #
        with tag("div"):
            meta = TournamentInfoHTML.tournament_view_tpl(
                data=tournament_data.get("metadata", {}),
                title="Overview",
                title_tag="h2"
            )
            doc.asis(meta)
        #
        # particpants ranking list
        #
        ranking_list: list[tuple] = tournament_data.get("ranking_list")
        if ranking_list:
            with tag("div"):
                doc.line("h2", "Participants and Rankings")
                with tag("table"):
                    line("caption", f"{len(ranking_list)} participants")
                    with tag("thead"):
                        with tag("tr"):
                            line("th", "Rank")
                            line("th", "Player")
                            line("th", "Score")
                    with tag("tbody"):
                        for p_rank, player, p_score in ranking_list:
                            player_str = player.get("national_player_id")
                            player_str += f" {player.get("surname", "").upper()}"
                            player_str += f" {player.get("name", "").capitalize()}"
                            with tag("tr"):
                                line("td", str(p_rank))
                                line("td", player_str)
                                line("td", str(p_score))
        #
        # matches
        #
        with tag("div"):
            line("h2", "Rounds")
            rounds_list: list[dict] = tournament_data.get("rounds", [])
            if len(rounds_list) == 0:
                line("p", "(No rounds data to display)")
            else:
                for round in rounds_list:
                    round_html = RoundDetailsHTML.round_tpl(
                        match_list=round.get("matches", []),
                        title=round.get("name"),
                        title_tag="h3")
                    doc.asis(round_html)
        return doc.getvalue()
