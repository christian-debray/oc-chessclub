import logging
import app
import types
from dataclasses import dataclass, field
from time import sleep
from pathlib import Path
from app.commands.commands_abc import CommandInterface
from app.controllers.controller_abc import MainController
from app.commands.commands import StopCommand, ExitCurrentCommand
from app.commands import commands
from app.views.views_abc import AbstractView
from app.views.menu import MenuOption, Menu
from app.models.player_model import PlayerRepository
from app.controllers.player_manager import PlayerManager

logger = logging.getLogger()


@dataclass
class AppConfig:
    player_repository_file: Path = field(default=Path(app.DATADIR, "players.json"))


class AssetLoader:
    """Helper class used to instanciate controllers and repositories.
    """
    def __init__(self, cfg: AppConfig, app: MainController):
        self._cfg = cfg
        self.player_repo = None
        self.tournament_repo = None
        self.app: MainController = app

    def load(self, cls):
        """Loads an instance of a suppported controller or repository,
        applying the app config.
        """
        match cls.__name__:
            case PlayerManager.__name__:
                return self.load_player_manager()
            case PlayerRepository.__name__:
                return self.load_player_repository()

    def load_player_repository(self) -> PlayerRepository:
        if not self.player_repo:
            self.player_repo = PlayerRepository(self._cfg.player_repository_file)
        return self.player_repo

    def load_player_manager(self) -> PlayerManager:
        return PlayerManager(player_repo=self.load_player_repository(),
                             app=self.app)


class MainMenuCommand(CommandInterface):
    def __init__(self,
                 app: MainController,
                 cycle: bool | int = False) -> None:
        super().__init__(cycle)
        self.app = app

    def execute(self):
        self.app.main_menu()


class MainController(MainController):
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
        self._config: AppConfig = AppConfig()
        self._loader: AssetLoader = AssetLoader(cfg=self._config, app=self)

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
        menu_view.add_option(
            MenuOption(
                option_text="Manage Players",
                command=commands.LaunchManagerCommand(
                    app=self,
                    cls_or_obj=PlayerManager)
                ))
        menu_view.add_option(MenuOption("Exit", command=ExitCurrentCommand(self)))
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

    def launch(self, cls_or_obj, method="default", **kwargs):
        """Launches a manager / controller.

        Method can be either the name (str) of a method,
        or a function object referencing the method to be called.
        In all cases, the methdo will be called in the context
        of an instance of the cls object.
        """
        obj = self._loader.load(cls_or_obj)
        if not obj:
            raise ValueError(f"Failed to load class {str(cls_or_obj)}")
        method_n = method
        if isinstance(method, types.FunctionType):
            method_n = method.__name__
        handler = getattr(obj, method_n or "default")
        logger.debug(f"Launching: {obj.__class__.__name__}.{method_n} ({kwargs})")
        handler(**kwargs)

    def main(self):
        """Runs the application main loop."""
        logger.debug("Start application main loop")

        # always display the main menu when we hit the bottom of the command stack
        self.receive(MainMenuCommand(app=self, cycle=True))

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
