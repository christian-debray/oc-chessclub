from app.helpers.ansi import Formatter


class AppStatusView:
    """A widget that displays status messages.
    """
    def display_status_message(self, msg: str):
        print(msg)

    def notify(self, msg: str):
        print(msg)

    def notify_warning(self, msg: str):
        self.notify(Formatter.format(msg, "yellow"))

    def notify_success(self, msg: str):
        self.notify(Formatter.format(msg, "light_green"))

    def notify_failure(self, msg: str):
        self.notify(Formatter.format(msg, "light_red"))
