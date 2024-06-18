from abc import abstractmethod
from app.commands.commands_abc import CommandManagerInterface
from app.views.views_abc import AbstractView
from app.views.app_status_view import AppStatusView


class MainController(CommandManagerInterface):

    @abstractmethod
    def view(self, view: AbstractView):
        """Register a view"""
        pass


class BaseController:
    def __init__(self):
        self.status = AppStatusView()

    @abstractmethod
    def default():
        """Default method to call when invoking a controller.
        """
        pass
