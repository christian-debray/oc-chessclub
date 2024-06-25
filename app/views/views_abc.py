from abc import abstractmethod
from app.commands.commands_abc import (
    CommandIssuer,
    CommandManagerInterface,
    CommandInterface,
)
from app.helpers import text_ui
from pathlib import Path
import sys
from contextlib import AbstractContextManager
import logging

logger = logging.getLogger()


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
        cmd_manager: CommandManagerInterface = None,
        title: str = None,
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
            title_str = f"*** {self.title.upper()} ***"
            print(title_str)
            print("="*len(title_str) + "\n")
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


class RenderToFileContext(AbstractContextManager):
    """Redirects output to a file
    """
    def __init__(self, ofile: Path = None, encoding="utf8"):
        self.ofile: Path = Path(ofile)
        self._o_handle = None
        self._o_encoding = encoding
        self._stdout_bck = None

    def __enter__(self):
        if self.ofile:
            logger.debug(f"Enter Write Context: redirect stdout to file: {self.ofile}")
            if not self.ofile.exists():
                if not self.ofile.parent.exists():
                    self.ofile.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
                self.ofile.touch(mode=0o666)
            self._o_handle = open(self.ofile, mode="w", encoding=self._o_encoding)
            self._stdout_bck = sys.stdout
            sys.stdout = self._o_handle
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Exit write context")
        try:
            self._o_handle.close()
        finally:
            sys.stdout = self._stdout_bck
        return False
