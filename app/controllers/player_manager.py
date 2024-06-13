from app.models.player_model import PlayerRepository, Player, NationalPlayerID
from app.views.player_editor import PlayerEditor
from app.views.player_view import PlayerView
from app.views.menu import Menu
from app.controllers.controller_abc import BaseController, MenuController
import logging
logger = logging.getLogger()

class PlayerManager(BaseController):
    def __init__(self, player_repo: PlayerRepository):
        super().__init__()
        self.player_repo: PlayerRepository = player_repo
        self._make_menu()
    
    def _make_menu(self):
        """Build our menu
        """
        self.menu_mngr = MenuController("Manage Players")
        self.menu_mngr.add_option(opt_action= self.register_new_player, opt_text= "Register a new player")
        self.menu_mngr.add_option(opt_action= self.edit_player, opt_text= "Edit player")
        self.menu_mngr.add_option(opt_action= self.list_all_players, opt_text= "List All Players")
        self.menu_mngr.add_option(opt_action= None, opt_text= "Exit")

    def menu(self):
        """User selects next action
        """
        self.menu_mngr.menu_loop()

    def register_new_player(self):
        """Register a new player in the database.
        """
        editor = PlayerEditor(self.status)
        if player := editor.prompt_for_player_data(Player()):
            self._add_new_player(player)
    
    def select_player(self):
        """Selects a player from the database for further operation
        """
        view = PlayerEditor(self.status)
        player_id = view.player_id_prompt("Find Player by ID: ")
        selected_player = None
        if player_id:
            selected_player = self.player_repo.find_by_id(player_id)
        if selected_player is not None:
            self.status.notify_success(f"Selected player {selected_player.id()}: {selected_player.name} {selected_player.surname}")
            return selected_player
        else:
            self.status.notify_failure("Failed to select player - check the National Player ID.")

    def edit_player(self, player_or_id: str|Player = None):
        """Edit player identified by player ID."""
        if not player_or_id:
            player_or_id = self.select_player()

        if isinstance(player_or_id, Player):
            player = player_or_id
        else:
            try:
                player = self.player_repo.find_by_id(player_or_id)
                if not player:
                    raise ValueError("Unknown player ID")
            except ValueError as e:
                self.status.notify_failure("Player not found: " + str(e))
                return
        editor = PlayerEditor(self.status)
        if player_copy := editor.prompt_for_player_data(player):
            self._update_player(player_copy, player)

    def _add_new_player(self, player: Player) -> bool:
        """Register a new player to the database
        """
        try:
            if player.is_valid():
                self.player_repo.add(player)
                self.player_repo.commit_changes()
                self.status.notify_success(f"New player registered with ID: {player.id()}")
                return True
            else:
                self.status.notify_failure("Can't register player with invalid or incomplete data. Abandon.")
        except KeyError as e:
            logger.exception(e)
            self.status.notify_failure("Failed to register player: Duplicate or invalid Player ID. Abandon.")
        except Exception as e:
            logger.exception(e)
            self.status.notify_failure("Failed to register player because of an unexpected error. Abandon.")
        return False
    
    def _update_player(self, new_player_data: Player, old_player_data: Player) -> bool:
        """Updates an existing player in the database.

        First compares old player data with new player data.

        - If nothing has changed, send a notificaiton to the user and return.
        - If the player ID has changed, first remove the old ID from the repository,
        then update or create the new one.
        - In all other cases update the existing player data in the repository.
        Notify user and returns True on success.
        """
        if old_player_data == new_player_data:
            self.status.notify_warning("No changes to record")
            return
        try:
            if not new_player_data.is_valid():
                self.status.notify_failure("Can't update player with invalid or incomplete data. Abandon.")
                return False
            if old_player_data.id() != new_player_data.id():
                # We must delete the existing player data first
                # Then check if the new ID already exists,
                # in which case we just udpate a player
                # otherwise we must register a new player
                self.status.notify("Changing player ID: deleting old record...")
                self.player_repo.delete(old_player_data.id())
                if not self.player_repo.find_by_id(new_player_data.id()):
                    return self._add_new_player(new_player_data)
                
            self.player_repo.update(new_player_data)
            self.player_repo.commit_changes()
            self.status.notify_success(f"Updated player: {new_player_data.id()}")
            return True                
        except Exception as e:
            logger.exception(e)
            self.status.notify_failure("Failed to update player because of an unexpected error. Abandon.")
        return False

    def list_all_players(self):
        player_list = list(self.player_repo.find_many())
        if len(player_list) == 0:
            self.status.notify_warning("No players to display.")
            return
        # alphabetic order:
        player_list.sort(key= lambda x: (x.surname.lower() + x.name.lower()))
        view = PlayerView()
        view.print_player_list(players=player_list)

if __name__ == '__main__':
    logging.basicConfig(filename="./debug.log", level=logging.DEBUG)
    from app import DATADIR
    from pathlib import Path
    player_json_file = Path(DATADIR, 'players.json').resolve()

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", default="menu", choices=["create", "edit", "list", "menu"])
    parser.add_argument("-m", nargs="?", dest="action", const="menu")
    parser.add_argument("-c", nargs="?", dest="action", const="create")
    parser.add_argument("-e", nargs="?", dest="action", const="edit")
    parser.add_argument("-l", nargs="?", dest="action", const="list")

    args = parser.parse_args()
    manager = PlayerManager(PlayerRepository(player_json_file))
    if args.action == "create":
        print("*** REGISTER NEW PLAYER ***")
        manager.register_new_player()
    elif args.action == "edit":
        print("*** EDIT PLAYER ***")
        manager.edit_player()
    elif args.action == "list":
        print("*** LIST PLAYERS ***")
        manager.list_all_players()
    elif args.action == "menu":
        manager.menu()

