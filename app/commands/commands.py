from app.commands.commands_abc import CommandInterface, GenericHandlerCommand
from typing import Callable


class DisplayMenuCommand(GenericHandlerCommand):
    """Requires the display of a menu.
    Usually this implies calling the menu() method of a class or object.
    """
    def __init__(self, cls_or_obj=None, menu_method="menu", cycle: int | bool = False) -> None:
        super().__init__(cls_or_obj=cls_or_obj, method=menu_method)
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
        self.valuehandler = valueHandler
        self.value = value

    def set_value(self, new_value):
        self.value = new_value

    def execute(self):
        self.valuehandler(self.value)
