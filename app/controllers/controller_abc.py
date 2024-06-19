from abc import abstractmethod
from app.commands.commands_abc import CommandManagerInterface
from app.views.views_abc import AbstractView
from app.views.app_status_view import AppStatusView
from typing import Any


class MainController(CommandManagerInterface):

    @abstractmethod
    def view(self, view: AbstractView):
        """Register a view"""
        pass

    @abstractmethod
    def set_state(self, key: str, value):
        """Records a value in the application's current state.
        """
        pass

    @abstractmethod
    def get_state(self, key: str) -> Any:
        """Returns the value of an element in the application's current state.
        """

    @abstractmethod
    def clear_state(self, key: str):
        """Removes an element from the application's current state."""


class BaseController:
    def __init__(self):
        self.status = AppStatusView()

    @abstractmethod
    def default():
        """Default method to call when invoking a controller.
        """
        pass
