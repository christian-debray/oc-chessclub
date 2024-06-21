import logging
import app
import types
import typing
from dataclasses import dataclass, field
from time import sleep
from pathlib import Path
from app.commands.commands_abc import CommandInterface
from app.controllers.controller_abc import MainController, BaseController
from app.commands.commands import StopCommand, ExitCurrentCommand
from app.commands import commands
from app.views.views_abc import AbstractView
from app.views.menu import MenuOption, Menu
from app.models.player_model import PlayerRepository
from app.controllers.player_manager import PlayerManager
from app.models.tournament_model import TournamentRepository
from app.controllers.tournament_manager import TournamentManager

logger = logging.getLogger()


@dataclass
class AppConfig:
    player_repository_file: Path = field(default=Path(app.DATADIR, "players.json"))
    tournament_data_dir: Path = field(default=Path(app.DATADIR, "tournaments"))
    tournament_repository_file: Path = field(
        default=Path(app.DATADIR, "tournaments", "tournament_index.json")
    )


class AssetLoader:
    """Helper class used to instanciate controllers and repositories."""

    def __init__(self, cfg: AppConfig, app: MainController):
        self._cfg = cfg
        self.player_repo = None
        self.tournament_repo = None
        self.tournament_manager = None
        self.app: MainController = app

    def load(self, cls) -> BaseController:
        """Loads an instance of a suppported controller or repository,
        applying the app config.
        """
        cls_n = cls if isinstance(cls, str) else cls.__name__
        match cls_n:
            case PlayerManager.__name__:
                return self.load_player_manager()
            case PlayerRepository.__name__:
                return self.load_player_repository()
            case TournamentRepository.__name__:
                return self.load_tournament_repository()
            case TournamentManager.__name__:
                return self.load_tournament_manager()
        raise ValueError(f"Failed to load instance of unknown class {cls_n}.")

    def load_player_repository(self) -> PlayerRepository:
        if not self.player_repo:
            self.player_repo = PlayerRepository(self._cfg.player_repository_file)
        return self.player_repo

    def load_player_manager(self) -> PlayerManager:
        return PlayerManager(player_repo=self.load_player_repository(), app=self.app)

    def load_tournament_repository(self) -> TournamentRepository:
        if not self.tournament_repo:
            self.tournament_repo = TournamentRepository(
                metadata_file=self._cfg.tournament_repository_file,
                player_repo=self.load_player_repository(),
            )
        return self.tournament_repo

    def load_tournament_manager(self) -> TournamentManager:
        if not self.tournament_manager:
            self.tournament_manager = TournamentManager(
                player_repo=self.load_player_repository(),
                tournament_repo=self.load_tournament_repository(),
                main_app=self.app,
            )
        return self.tournament_manager


class MainMenuCommand(CommandInterface):
    def __init__(self, app: MainController, cycle: bool | int = False) -> None:
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
        #
        # some features require to store values
        self._state: dict = {}

    def set_state(self, key: str, value: typing.Any):
        self._state[key] = value

    def get_state(self, key: str) -> typing.Any:
        return self._state.get(key)

    def clear_state(self, key: str):
        if key in self._state:
            del self._state[key]

    def receive(self, *command: CommandInterface):
        """Receive one or more commands and add them to the command stack.

        Only the StopCommand will be executed immediately.
        All other commands are executed in stack order.
        """
        for cmd in command:
            logger.debug(f"Received command {cmd.__class__}")
            if cmd.cycle:
                logger.debug(
                    "This command will be repeated {}".format(
                        f"{cmd.cycle} times"
                        if isinstance(cmd.cycle, int)
                        else "forever"
                    )
                )
            if isinstance(cmd, StopCommand):
                self._received_stop_command = True
                cmd.execute()
            else:
                self._command_queue.append(cmd)

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
                    app=self, cls_or_obj=PlayerManager
                ),
            )
        )
        menu_view.add_option(
            MenuOption(
                option_text="Manage Tournaments",
                command=commands.LaunchManagerCommand(
                    app=self, cls_or_obj=TournamentManager
                ),
            )
        )
        menu_view.add_option(
            MenuOption(
                option_text="Exit", alt_key="X", command=ExitCurrentCommand(self)
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

    def launch(self, cls_or_obj, method="default", **kwargs):
        """Launches a manager / controller.

        Method can be either the name (str) of a method,
        or a function object referencing the method to be called.
        In all cases, the method will be called in the context
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

    def interpret_script(self, cmd_list: list[str] = None):
        """Interprets the elements of a list as commands.
        Decodes each line to produce the command with proper parameters.

        We expect elements like this in the input:
        <controllerclass>.<controllermethod>(params_json)
        controller pparameters must be expressed as a JSON string:
        property names are double-quoted, boolean values are lowercase, None is null

        for ex.:
        "TournamentManager.register_player({"player_id": "OP98765", "tournament_id": null, "confirmed": false})"

        """
        import json

        script: list[CommandInterface] = []
        try:
            line = 0
            for cmd_str in cmd_list:
                line += 1
                cls_n = cmd_str[: cmd_str.index(".")]
                method_n = cmd_str[cmd_str.index(".") + 1: cmd_str.index("(")]
                if param_json := cmd_str[cmd_str.index("(") + 1: cmd_str.index(")")]:
                    params = json.loads(param_json)
                else:
                    params = {}
                script.append(
                    commands.LaunchManagerCommand(
                        app=self, cls_or_obj=cls_n, method=method_n, **params
                    )
                )
        except Exception as e:
            err_msg = f"Error in commands script at line {line}: {e}"
            logger.error(err_msg, stack_info=True)
            print(err_msg)
            
            return []
        return script

    def main(self, cmd_script: list[str] = None):
        """Runs the application main loop.

        Accepts a list of commands to execute."""
        logger.debug("Start application main loop")

        # always display the main menu when we hit the bottom of the command stack
        self.receive(MainMenuCommand(app=self, cycle=True))

        # load commmands from external script
        if cmd_script:
            cmd_list = list(reversed(self.interpret_script(cmd_script)))
            self.receive(*cmd_list)

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
    script = None
    script = [
        'TournamentManager.load_tournament({"tournament_id": "9ed32c19-4e38-4c48-a1f2-197ac6feb65f"})',
        'TournamentManager.register_player()'
    ]
    chessApp.main(cmd_script=script)
