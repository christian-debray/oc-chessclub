from app.commands.commands_abc import CommandInterface, CommandManagerInterface
from app.views.views_abc import BaseView
from app.helpers.text_ui import confirm
from app.helpers import ansi


class Dialog(BaseView):
    """Mimics a dialog with Accept/Abort commands.
    """

    def __init__(
        self,
        cmd_manager: CommandManagerInterface,
        title: str = None,
        text: str = None,
        clear_scr: bool = False,
        confirm_cmd: CommandInterface = None,
        abandon_cmd: CommandInterface = None
    ):
        super().__init__(
            cmd_manager=cmd_manager, title=title, text=text, clear_scr=clear_scr
        )
        self.confirm_cmd = confirm_cmd
        self.abandon_cmd = abandon_cmd

    def render(self):
        super().render()
        if confirm():
            self.issuecmd(self.confirm_cmd)
        else:
            print(ansi.Formatter.format("Abandon", ansi.Formatter.YELLOW))
            self.issuecmd(self.abandon_cmd)
