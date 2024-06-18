from app.commands import commands_abc, commands
from app.controllers.player_manager import PlayerManager
from app.views.menu import Menu, MenuOption


class MainMenu(Menu):
    """The Main Menu"""
    def __init__(self, cmdManager: commands_abc.CommandManagerInterface = None):
        super().__init__(title="Chess App Main Menu",
                         options=None,
                         cmdManager=cmdManager)
        self.add_option(
            MenuOption(
                option_text="Manage Players",
                command=commands.LaunchManagerCommand(
                    app=self.cmd_manager,
                    cls_or_obj=PlayerManager
                )
                ))
        self.add_option(MenuOption("Exit", command=commands_abc.ExitCurrentCommand(self.cmd_manager)))
