import app
from app.commands.commands_abc import (
    CommandManagerInterface,
    CommandInterface,
    StopCommand,
    ExitCurrentCommand,
)
from app.commands import commands
from time import sleep
from app.views.views_abc import AbstractView
from app.views.menu import MenuOption, Menu
from pathlib import Path
import logging

logger = logging.getLogger()


class MainController(CommandManagerInterface):
    """Main App controller.

    Pilots the app execution from an infinite loop in the main() method.

    The commands found in the queue are executed in stacked order.
    Usually, a command will call a controller's method.
    Controllers set up views and pass them to the view() method.
    Views issue commands, collected by the receive() method and placed in the queue.

    """

    def __init__(self):
        self._command_queue: list[CommandInterface] = []
        self._received_stop_command = False
        self._views: list[AbstractView] = []

    def receive(self, command: CommandInterface):
        """Receive a command and add it to the command stack.

        Only the StopCommand will be executed immediately.
        All other commands are executed in stack order.
        """
        logger.debug(f"Received command {command.__class__}")
        if command.cycle:
            logger.debug(
                "This command will be repeated {}".format(
                    f"{command.cycle} times"
                    if isinstance(command.cycle, int)
                    else "forever"
                )
            )
        if isinstance(command, StopCommand):
            self._received_stop_command = True
            command.execute()
        else:
            self._command_queue.append(command)

    def view(self, viewobj: AbstractView):
        """Load a view to the current view store.

        Views will be rendered once the current command has completed its execution.
        """
        logger.debug(f"loaded view {viewobj.__class__}")
        self._views.append(viewobj)

    def render_views(self):
        """Renders the views found in the view store by calling their 'render()' methods."""
        while len(self._views):
            v = self._views.pop()
            logger.debug(f"Render view {v.__class__}")
            v.render()

    def main_menu(self):
        """Loads the main menu in the views store."""
        logger.debug("Preparing the main menu.")
        menu_view = Menu("Chess Club Main Menu", cmdManager=self)
        menu_view.add_option(MenuOption(option_text="First option - does nothing"))
        menu_view.add_option(MenuOption(option_text="Scond option - does nothing"))
        menu_view.add_option(
            MenuOption(option_text="Normal Exit", command=ExitCurrentCommand(mngr=self))
        )
        menu_view.add_option(
            MenuOption(
                option_text="Exit All, immediately", command=StopCommand(mngr=self)
            )
        )
        self.view(menu_view)

    def exit_all(self):
        """Exits the app without delay."""
        logger.debug("Exit app without delay.")
        self._received_stop_command = True
        self._command_queue = []
        self._views = []
        exit()

    def exit_current(self):
        """Exits current context."""
        logger.debug(
            f"Exit current context: {len(self._command_queue)} -> {len(self._command_queue) - 1}"
        )
        if len(self._command_queue) > 0:
            self._command_queue.pop()

    def issue_main_menu_command(self):
        """Issue the main menu command to ourselve."""
        mainMenuCommand = commands.DisplayMenuCommand(
            cls_or_obj=self, menu_method="main_menu", cycle=True
        )
        self.receive(mainMenuCommand)

    def main(self):
        """Runs the application main loop."""
        logger.debug("Start application main loop")
        self.issue_main_menu_command()

        while len(self._command_queue) > 0 and self._received_stop_command is False:
            if len(self._command_queue) > 0:
                logger.debug(f"{len(self._command_queue)} commands found in queue")
                cmd = self._command_queue.pop()
                logger.debug(f"executing command {cmd.__class__}")

                # should we repeat this command next loop ?
                if cmd.cycle is True:
                    self.receive(cmd)
                elif isinstance(cmd.cycle, int) and cmd.cycle > 0:
                    cmd.cycle -= 1
                    self.receive(cmd)

                cmd.execute()
                self.render_views()
            self.render_views()
            sleep(0.01)
        logger.debug(
            "Main loop ended, stop application because {}.".format(
                "command queue is empty"
                if len(self._command_queue) == 0
                else "stop command received"
            )
        )
        print("Done.")
        exit()


if __name__ == "__main__":
    logfile = Path(app.APPDIR, "debug.log")
    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    chessApp = MainController()
    chessApp.main()
