from app.commands import commands_abc
from app.views.views_abc import BaseView, AbstractView
from app.helpers.string_formatters import format_cols, formatdate
from app.helpers.text_ui import form_field, confirm, prompt_v
import app.helpers.validation as validation
from app.views.app_status_view import AppStatusView
from datetime import date


class TournamentMetaView(AbstractView):
    def __init__(
        self,
        cmd_manager: commands_abc.CommandManagerInterface,
        tournament_metadata: dict,
    ):
        super().__init__(cmd_manager)
        self.data: tournament_metadata

    def render(self):
        print(self.tournament_meta_template(self.data))

    @staticmethod
    def tournament_meta_template(data: dict, as_cells=False) -> str | list[str]:
        id_tpl = f"{data.get('tournament_id')}"
        location_tpl = f"{data.get('location')}"
        status_tpl = f"{data.get('status')}"
        start_date_tpl = formatdate(d=data.get("start_date"), fmt="%d/%m/%Y", empty="-")
        end_date_tpl = formatdate(d=data.get("end_date"), fmt="%d/%m/%Y", empty="-")
        cells = [id_tpl, location_tpl, status_tpl, start_date_tpl, end_date_tpl]
        return cells if as_cells else " - ".join(cells)


class TournamentsListView(BaseView):
    """Display a list of tournaments"""

    def __init__(
        self,
        cmd_manager: commands_abc.CommandManagerInterface,
        title: str,
        text: str = None,
        clear_scr: bool = False,
        tournament_list: list[dict] = None,
    ):
        super().__init__(
            cmd_manager=cmd_manager, title=title, text=text, clear_scr=clear_scr
        )
        self.tournament_list: list[dict] = tournament_list or None

    def render(self):
        # render title and text
        super().render()
        if not self.tournament_list or len(self.tournament_list) == 0:
            print("No data to display")
        else:
            print(self.list_tpl(self.tournament_list))

    @staticmethod
    def list_tpl(tournament_list: list[dict]) -> str:
        if not tournament_list or len(tournament_list) == 0:
            return ""
        lines = [
            TournamentMetaView.tournament_meta_template(data=t, as_cells=True)
            for t in tournament_list
        ]
        return format_cols(
            data=lines,
            headers=["Tournament_id", "location", "status", "start date", "end date"],
        )


class SelectTournamentIDView(AbstractView):
    """Prompts user for a tournament ID to load as current tournament."""

    def __init__(
        self,
        cmd_manager: commands_abc.CommandManagerInterface,
        confirm_command: commands_abc.CommandInterface = None,
        cancel_command: commands_abc.CommandInterface = None,
        list_command: commands_abc.CommandInterface = None
    ):
        super().__init__(cmd_manager)
        self.confirm_command = confirm_command
        self.cancel_command = cancel_command
        self.list_command = list_command
        self.list_key = "L"

    def render(self):
        print("\n")
        instructions = "Enter tournament ID to select a tournament"
        instructions += "\n   or (<ctrl>+D or enter to skip)"
        if self.list_command:
            shortcuts = {self.list_key: self.list_key}
            instructions += f"\n   or '{self.list_key}' and enter to list tournaments"
        else:
            shortcuts = {}
        print(instructions)
        if tournament_id := self.prompt_for_tournament_id(prompt_txt="tournament ID > ", shortcuts=shortcuts):
            if tournament_id == self.list_key:
                self.issuecmd(self.list_command)
            elif self.confirm_command:
                self.confirm_command.set_command_params(tournament_id=tournament_id)
                self.issuecmd(self.confirm_command)
        else:
            self.issuecmd(self.cancel_command)

    @staticmethod
    def prompt_for_tournament_id(prompt_txt: str = None, shortcuts: dict[str, str] = None, text: str = None) -> str:
        """Displays a prompt to enter a tournament ID"""
        if text:
            print(text)
        prompt_txt = prompt_txt or "Enter a tournament ID > "
        return prompt_v(
            prompt=prompt_txt,
            validator=r"^[a-zA-Z0-9\-_]+$",
            not_valid_msg="Only alphanumeric characters, hyphen and underscore",
            skip_blank=True,
            shortcuts=shortcuts
        )


class TournamentMetaEditor(BaseView):
    """Display a form to edit the metadata of a tournament.
    """
    def __init__(
        self,
        cmd_manager: commands_abc.CommandManagerInterface,
        title: str,
        data: dict,
        frozen_fields: list[str] = None,
        text: str = None,
        clear_scr: bool = False,
        status: AppStatusView = None,
        confirm_command: commands_abc.CommandInterface = None,
        cancel_command: commands_abc.CommandInterface = None
    ):
        super().__init__(
            cmd_manager=cmd_manager, title=title, text=text, clear_scr=clear_scr
        )
        self.data = data
        self.frozen_fields = frozen_fields or []
        self.status = status or AppStatusView()
        self.confirm_command = confirm_command
        self.cancel_command = cancel_command

    def render(self):
        super().render()
        if user_data := self.display_form(self.data, self.frozen_fields):
            if self.confirm_command:
                self.confirm_command.set_command_params(**user_data)
                self.issuecmd(self.confirm_command)
        elif self.cancel_command:
            self.issuecmd(self.cancel_command)

    def display_form(self, data: dict, frozen_fields: list[str] = None) -> dict:
        """Displays the form to edit a tournament's metadata, and returns the updated data.
        """
        user_data = data.copy()
        fv = form_field(
            field="location",
            form_data=data,
            frozen_fields=frozen_fields,
            validator=validation.is_valid_name,
            not_valid_msg="Enter a valid location name (letters, space, hyphen)",
            skip_blank=True,
            display_current=True
        )
        if fv and fv != data['location']:
            user_data['location'] = fv
        elif data['location'] and 'location' not in frozen_fields:
            self.status.notify_warning(f"Keeping previous value: {data['location']}\n")

        fv = form_field(
            field="start_date",
            form_data=data,
            frozen_fields=frozen_fields,
            validator=validation.is_valid_date,
            not_valid_msg="Enter a valid date (YYYY-mm-dd)",
            skip_blank=True,
            display_current=True
        )
        if fv and fv != data['start_date']:
            user_data['start_date'] = fv
        elif data['start_date'] and 'start_date' not in frozen_fields:
            self.status.notify_warning(f"Keeping previous value: {data['start_date']}\n")

        fv = form_field(
            field="turn_count",
            form_data=data,
            frozen_fields=frozen_fields,
            validator="^[0-9]+$",
            not_valid_msg="Enter a number above 0",
            skip_blank=True,
            display_current=True
        )
        if fv and fv != data['turn_count']:
            user_data['turn_count'] = fv
        elif data['turn_count'] and 'turn_count' not in frozen_fields:
            self.status.notify_warning(f"Keeping previous value: {data['turn_count']}\n")

        fv = form_field(
            field="description",
            form_data=data,
            frozen_fields=frozen_fields,
            skip_blank=True,
            display_current=True
        )
        if fv and fv != data['description']:
            user_data['description'] = fv
        elif data['description'] and 'description' not in frozen_fields:
            self.status.notify_warning(f"Keeping previous value: {data['description']}\n")

        if user_data == data:
            self.status.notify_warning("No changes to record. Aborting.")
            return None
        if confirm("Press Y to confirm changes"):
            return user_data
        else:
            self.status.notify_warning("Abandoning changes.")


class TournamentDetailsView(AbstractView):
    """Displays some details about a tournament
    """
    def __init__(self,
                 cmd_manager: commands_abc.CommandManagerInterface,
                 tournament_id: str,
                 status: str,
                 turn_count: int = None,
                 participants_count: int = None,
                 location: str = None,
                 start_date: date = None,
                 end_date: date = None,
                 current_turn_idx: int = None,
                 current_turn_name: str = None,
                 current_turns_status: str = None,
                 **kwargs
                 ):
        super().__init__(cmd_manager)
        self.tournament_id = tournament_id
        self.status = status
        self.turn_count = turn_count
        self.participants_count = participants_count
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.current_turn_idx = current_turn_idx
        self.current_turn_name = current_turn_name
        self.current_turns_status = current_turns_status

    def render(self):
        print(self.details_template())

    def details_template(self):
        if self.start_date:
            start_date_str = ", {} {}".format(
                "scheduled" if self.status == "open" else "started",
                formatdate(self.start_date, "%d/%m/%Y"))
        else:
            start_date_str = " not scheduled yet"
        if self.end_date and self.status == "ended":
            end_date_str = f", ended {formatdate(self.end_date, "%d/%m/%Y")}"
        else:
            end_date_str = ""
        tpl = (f"Tournament {self.tournament_id} in {self.location.strip() or "???"}{start_date_str}{end_date_str}")
        if self.participants_count:
            tpl += f"\n{self.participants_count} participants"
        if self.current_turn_idx and self.status == "running":
            tpl += f"\nRound {self.current_turn_idx}/{self.turn_count}"
            tpl += f": {self.current_turn_name} ({self.current_turns_status})"
        elif self.turn_count:
            tpl += f"\n{self.turn_count} turns"
        return tpl
