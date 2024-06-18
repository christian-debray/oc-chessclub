from app.helpers.text_ui import prompt_v, clear


class Menu:
    def __init__(self, title: str = None, options: list[str] = None):
        self.options: list[str] = options or []
        self.title: str = title
        self.ruler = "="
        self.indent = 1

    def choose(self) -> int:
        """Display the menu and prompts for a choice.
        Returns the index of the option selected by the user."""
        clear()
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
            opt_lines.append(f"{opt_indent}{opt_marker}{opt}")
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
