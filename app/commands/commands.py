from app.commands.commands_abc import CommandInterface, CommandManagerInterface
from typing import Callable


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


class LaunchManagerCommand(CommandInterface):
    """Launches a controller or manager"""
    def __init__(self,
                 app: CommandManagerInterface,
                 cls_or_obj,
                 method=None,
                 **kwargs) -> None:
        super().__init__()
        self.app = app
        self.cls_or_obj = cls_or_obj
        self.method = method
        self.set_command_params(**kwargs)

    def execute(self):
        self.app.launch(cls_or_obj=self.cls_or_obj, method=self.method, **self.params)


class DisplayMenuCommand(LaunchManagerCommand):
    """Requires the display of a menu.
    Usually this implies calling the menu() method of a class or object.
    """
    def __init__(self,
                 app: CommandManagerInterface,
                 cls_or_obj=None,
                 menu_method="menu",
                 cycle: int | bool = False) -> None:
        super().__init__(app=app, cls_or_obj=cls_or_obj, method=menu_method)
        self.cycle = cycle


class AbortCommand(CommandInterface):
    """Abort current process.
    """
    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        return False


class ConfirmValueCommand(CommandInterface):
    """Pass a value to a receiver.
    """
    def __init__(self, valueHandler: Callable, value=None):
        super().__init__()
        self.valuehandler = valueHandler
        self.value = value

    def set_command_params(self, *args, **kwargs):
        self.set_value(*args)

    def set_value(self, new_value):
        self.value = new_value

    def execute(self):
        self.valuehandler(self.value)
