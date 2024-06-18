from app.helpers.text_ui import prompt_v
from app.commands.commands_abc import CommandInterface, CommandManagerInterface
from app.views.views_abc import AbstractView


class MenuOption:
    def __init__(self, option_text: str,
                 option_value=None,
                 command: CommandInterface = None):
        self.text = option_text
        self.value = option_value
        self.command = command


class Menu(AbstractView):
    def __init__(self, title: str = None, options: list[MenuOption] = None,
                 cmdManager: CommandManagerInterface = None):
        super().__init__(cmd_manager=cmdManager)
        self.options: list[MenuOption] = options or []
        self.title: str = title
        self.ruler = "="
        self.indent = 1

    def render(self):
        choice = self.choose()
        self.issuecmd(self.options[choice].command)

    def add_option(self, option: MenuOption):
        self.options.append(option)

    def choose(self) -> int:
        """Display the menu and prompts for a choice.
        Returns the index of the option selected by the user."""
        if self.title:
            title_str = " ".join([w.capitalize() for w in self.title.split()])
            print(title_str)
        opt_keys = {}
        # render options and build option keys in the same process
        width = len(title_str)
        opt_lines = []
        for o in range(len(self.options)):
            opt = self.options[o]
            opt_key = f"{o + 1}"
            opt_marker = f"{opt_key}. "
            opt_indent = " " * self.indent
            opt_lines.append(f"{opt_indent}{opt_marker}{opt.text}")
            opt_keys[opt_key] = o
            lw = len(opt_lines[-1])
            width = lw if lw > width else width

        print(self.ruler * width)
        print("\n".join(opt_lines))
        print(self.ruler * width)

        choice = prompt_v(
            prompt="Enter option number: ", validator=lambda x: x in opt_keys
        )
        if choice is not None and choice in opt_keys:
            return opt_keys[choice]
        else:
            return None
