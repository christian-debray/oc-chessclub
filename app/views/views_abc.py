from abc import abstractmethod
from app.commands.commands_abc import CommandIssuer, CommandManagerInterface


class AbstractView(CommandIssuer):
    """Base class for all views.

    Views a responsible for rendering the UI.
    User input handling is delegated to Command objects.
    """
    def __init__(self, cmd_manager: CommandManagerInterface):
        super().__init__(cmd_manager)

    @abstractmethod
    def render(self):
        """Displays the view to the user. Usually called by the main app.
        """
        pass
