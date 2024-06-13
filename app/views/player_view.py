from app.models.player_model import Player
from datetime import date
from app.helpers.string_formatters import format_cols
from app.helpers.text_ui import proceed_any_key

class PlayerView:

    def player_template(self, player: Player, as_cells: bool= False) -> str | list[str]:
        id_tpl = f"{player.national_player_id}"
        name_tpl = f"{player.surname.upper()} {player.name.capitalize()}"
        date_tpl = f"(born {player.birthdate.strftime("%d/%m/%Y")})"
        cells = [id_tpl, name_tpl, date_tpl]
        return cells if as_cells else " - ".join(cells)

    def print_player_list(self, players: list[Player]):
        p_lines = [self.player_template(p, as_cells= True) for p in players]
        print(format_cols(p_lines, ["Player ID", "Name", "Birthdate"]))

        print("\n")
        proceed_any_key(timeout=10)

