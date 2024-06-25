from app.commands.commands_abc import CommandManagerInterface
from app.views.views_abc import AbstractView
from yattag import Doc, indent, SimpleDoc
from app.helpers.string_formatters import formatdate


class TournamentInfoHTML(AbstractView):
    """Render tournament infos as HTML"""
    def __init__(self,
                 tournament_data: dict,
                 title: str = None,
                 cmd_manager: CommandManagerInterface = None):
        super().__init__(cmd_manager=cmd_manager)
        self.tournament_data = tournament_data
        self.title = title

    def render(self):
        markup: SimpleDoc = self.tournament_view_tpl(self.tournament_data)
        if not self.title:
            print(indent(markup.getvalue()))
        else:
            doc, tag, text, line = Doc().ttl()
            with tag("div"):
                line("h2", self.title)
                doc.asis(markup.getvalue())
            print(indent(doc.getvalue()))

    @staticmethod
    def tournament_view_tpl(data: dict) -> SimpleDoc:

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
        with tag("ul"):
            for dt, dd in list_data:
                with tag("li"):
                    line("strong", f"{dt}:")
                    text(f" {dd}")
        return doc
