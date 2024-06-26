from app.commands.commands_abc import CommandManagerInterface
from yattag import Doc, indent
from app.views.html.base_html import HTMLBaseView
from app.helpers.string_formatters import formatdate


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
