from app.helpers.text_ui import prompt_v
from app.commands.commands_abc import CommandInterface, CommandManagerInterface
from app.views.views_abc import BaseView


class MenuOption:
    """A Menu Item.

    - option_text: label displayed for this option in the menu.
    - option_value: optional value of this item.
    - command: command to execute when this option is selected
    - alt_key: optional key to select this option. This will set
            a "permanent" key to select this item from the parent menu.

    Note: option keys and alt_keys are case insensitive, ie 'x' and 'X'
    are the same.
    """

    def __init__(
        self,
        option_text: str,
        option_value=None,
        command: CommandInterface = None,
        alt_key: str = None,
    ):
        self.text = option_text
        self.value = option_value
        self.command = command
        self.alt_key: str = alt_key.upper() if alt_key is not None else None


class Menu(BaseView):
    """Displays a menu and prompts the user to choose an option."""

    def __init__(
        self,
        title: str = None,
        text: str = None,
        options: list[MenuOption] = None,
        cmdManager: CommandManagerInterface = None,
        clear_scr: bool = False,
    ):
        super().__init__(
            cmd_manager=cmdManager, title=title, text=text, clear_scr=clear_scr
        )
        self.options: list[MenuOption] = options or []
        self.ruler = "="
        self.indent = 1

    def render(self):
        if self.clear_when_render:
            self.clear_scr()
        choice: int = self.choose()
        if choice is not None:
            self.issuecmd(self.options[choice].command)

    def add_option(self, option: MenuOption):
        self.options.append(option)

    def choose(self) -> int:
        """Display the menu and prompts for a choice.
        Returns the index of the option selected by the user."""

        print("\n\n")
        if self.title:
            title_str = " ".join([w.capitalize() for w in self.title.split()])
            print(title_str)
        opt_keys = {}
        # render options and build option keys in the same process
        width = len(title_str)
        opt_lines = []
        for o in range(len(self.options)):
            opt = self.options[o]
            opt_key = f"{o + 1}" if opt.alt_key is None else f"{opt.alt_key.upper()}"
            opt_marker = f"({opt_key}) "
            opt_indent = " " * self.indent
            opt_lines.append(f"{opt_indent}{opt_marker}{opt.text}")
            opt_keys[opt_key] = o
            if opt.alt_key is not None:
                opt_keys[opt.alt_key.upper()] = o
                opt_keys[opt.alt_key.lower()] = o
            lw = len(opt_lines[-1])
            width = lw if lw > width else width

        print(self.ruler * width)
        print("\n".join(opt_lines))
        print(self.ruler * width)

        if self.text:
            print(self.text, "\n")
        choice = prompt_v(
            prompt="Enter option number: ", validator=lambda x: x in opt_keys
        )
        if choice is not None and choice in opt_keys:
            return opt_keys[choice]
        else:
            return None
