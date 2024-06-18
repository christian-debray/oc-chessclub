from abc import abstractmethod
from typing import Callable


class CommandInterface:
    """Interface of all Commands.

    cycle property: specify that this command must be reiterated
    by the handling CommanManagerInterface.

    Possible values are:
    - False: don't repeat the command (default)
    - True: always repeat the command
    - integer > 0: repeat n times
    """
    def __init__(self, cycle: bool | int = False) -> None:
        self.cycle = cycle

    @abstractmethod
    def execute(self):
        pass


class CommandManagerInterface:
    """Interface of all classes managing command queues.
    """

    @abstractmethod
    def receive(self, cmd: CommandInterface):
        pass

    @abstractmethod
    def exit_all(self):
        """Exit all running processes,
        and stops the app."""
        pass

    @abstractmethod
    def exit_current(self):
        """Exit the current process.
        """
        pass

    def launch(self, cls_or_obj, method, **kwargs):
        """Launches a new process or controller
        """
        pass


class CommandIssuer:
    """Generic implementation of a class issuing commands.
    Command execution is delegated to a CommandManager object.
    """
    def __init__(self, cmd_manager: CommandManagerInterface):
        self.cmd_manager = cmd_manager

    def issuecmd(self, cmd: CommandInterface = None):
        """Helper method to issue a command.
        Won't do anything if no command manager is set.
        """
        if self.cmd_manager and cmd:
            self.cmd_manager.receive(cmd)


class StopCommand(CommandInterface):
    """Require the app to stop without delay.
    """
    def __init__(self, mngr: CommandManagerInterface) -> None:
        super().__init__()
        self.mngr: CommandManagerInterface = mngr

    def execute(self):
        self.mngr.exit_all()


class ExitCurrentCommand(CommandInterface):
    """Require the app to exit current context.

    Useful to exit a cycling menu, for instance.
    """
    def __init__(self, mngr: CommandManagerInterface) -> None:
        super().__init__()
        self.mngr: CommandManagerInterface = mngr

    def execute(self):
        self.mngr.exit_current()


class GenericHandlerCommand(CommandInterface):
    def __init__(self, cls_or_obj=None, method=None, **kwargs) -> None:
        super().__init__()
        self.cls_or_obj = cls_or_obj
        self.method = method
        self.params = kwargs or {}

    def execute(self):
        handler = None
        if self.cls_or_obj:
            if hasattr(self.cls_or_obj, self.method):
                handler = getattr(self.cls_or_obj, self.method)
            elif callable(self.cls_or_obj):
                handler = self.cls_or_obj
        elif self.method and Callable(self.method):
            handler = self.method
        if not handler:
            return
        handler(**self.params)
