from app.commands import commands_abc
from app.views.views_abc import BaseView, AbstractView
from app.helpers.string_formatters import format_cols, formatdate
from app.helpers.text_ui import form_field, confirm, prompt_v
import app.helpers.validation as validation
from app.views.app_status_view import AppStatusView


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
    ):
        super().__init__(cmd_manager)
        self.confirm_command = confirm_command
        self.cancel_command = cancel_command

    def render(self):
        if tournament_id := self.prompt_for_tournament_id():
            if self.confirm_command:
                self.confirm_command.set_command_params(tournament_id=tournament_id)
                self.issuecmd(self.confirm_command)
        elif self.confirm_command:
            self.issuecmd(self.cancel_command)

    @staticmethod
    def prompt_for_tournament_id(prompt_txt: str = None) -> str:
        """Displays a prompt to enter a tournament ID"""
        prompt_txt = prompt_txt or "Enter a tournament ID > "
        return prompt_v(
            prompt=prompt_txt,
            validator=r"^[a-zA-Z0-9\-_]+$",
            not_valid_msg="Only alphanumeric characters, hyphen and underscore",
            skip_blank=True,
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
