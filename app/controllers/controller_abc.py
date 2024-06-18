from abc import abstractmethod
from app.commands.commands_abc import CommandManagerInterface
from app.views.views_abc import AbstractView
from app.views.app_status_view import AppStatusView
from typing import Callable
from app.views.menu import Menu


class MainController(CommandManagerInterface):

    @abstractmethod
    def view(self, view: AbstractView):
        """Register a view"""
        pass


class BaseController:
    def __init__(self):
        self.status = AppStatusView()


class MenuController:
    """A generic menu controller.
    Provides a loop to choose
    """

    def __init__(self, menu_title: str = None):
        self._options_map = []
        self._menu = Menu(title=menu_title)

    def set_title(self, title: str):
        self._menu.title = title

    def add_option(self, opt_action: Callable | None, opt_text: str):
        self._options_map.append((opt_action, opt_text))
        self._menu.options.append(opt_text)

    def menu_loop(self):
        """User selects next action.
        Loops until user selects an option mapped to None.
        """
        loop = True
        while loop:
            choice = self._menu.choose()
            if choice is not None:
                do = self._options_map[choice][0]
                if do is not None and callable(do):
                    do()
                else:
                    loop = False
            else:
                loop = False
