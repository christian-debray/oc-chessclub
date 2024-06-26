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
