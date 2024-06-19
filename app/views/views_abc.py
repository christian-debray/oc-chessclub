from abc import abstractmethod
from app.commands.commands_abc import (
    CommandIssuer,
    CommandManagerInterface,
    CommandInterface,
)
from app.helpers import text_ui


class AbstractView(CommandIssuer):
    """Base class for all views.

    Views a responsible for rendering the UI.
    User input handling is delegated to Command objects.
    """

    def __init__(self, cmd_manager: CommandManagerInterface):
        super().__init__(cmd_manager)

    @abstractmethod
    def render(self):
        """Displays the view to the user. Usually called by the main app."""
        pass


class BaseView(AbstractView):
    """A simple view that displays a title and some text.

    Use this as a template or base class when creating new views.
    """

    def __init__(
        self,
        cmd_manager: CommandManagerInterface,
        title: str,
        text: str = None,
        clear_scr: bool = False,
    ):
        super().__init__(cmd_manager)
        self.title: str = title
        self.text: str = text
        self.clear_when_render: bool = clear_scr

    def clear_scr(self):
        text_ui.clear()

    def render(self):
        if self.clear_when_render:
            self.clear_scr()
        else:
            print("\n")
        if self.title:
            print(f"*** {self.title.upper()} ***\n")
        if self.text:
            print(self.text)


class SimpleView(BaseView):
    """A simple view that displays a title and some text.

    Optionnally issues a command when done with rendering.
    Use this as a template when creating new views.
    """

    def __init__(
        self,
        cmd_manager: CommandManagerInterface,
        title: str,
        text: str = None,
        clear_scr: bool = False,
        command: CommandInterface = None,
    ):
        super().__init__(
            cmd_manager=cmd_manager, title=title, text=text, clear_scr=clear_scr
        )
        self.command = command

    def render(self):
        if self.clear_when_render:
            self.clear_scr()
        else:
            print("\n")
        if self.title:
            print(f"*** {self.title.upper()} ***\n")
        if self.text:
            print(self.text)

        if self.command:
            self.issuecmd(self.command)
