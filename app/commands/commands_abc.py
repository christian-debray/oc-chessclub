from abc import abstractmethod


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
        self.params = {}

    @abstractmethod
    def execute(self):
        pass

    def set_command_params(self, *args, **kwargs):
        """Clients may set parameters before issuing a command.
        """
        if kwargs:
            if not self.params:
                self.params = {}
            for k, v in kwargs.items():
                self.params[k] = v


class CommandManagerInterface:
    """Interface of all classes managing command queues.
    """

    @abstractmethod
    def receive(self, *cmd: CommandInterface):
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

    def issuecmd(self, cmd: CommandInterface | list[CommandInterface] = None):
        """Helper method to issue a command.
        Won't do anything if no command manager is set.
        """
        if not self.cmd_manager or not cmd:
            return
        cmd_list = cmd if isinstance(cmd, list) else [cmd]
        self.cmd_manager.receive(*cmd_list)
