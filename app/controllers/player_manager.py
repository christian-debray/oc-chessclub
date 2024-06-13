from app.models.player_model import PlayerRepository, Player
from app.views.player_editor import PlayerEditor
from app.views.app_status_view import AppStatusView
from app.controllers.controller_abc import BaseController
import logging
logger = logging.getLogger()

class PlayerManager(BaseController):
    def __init__(self, player_repo: PlayerRepository):
        super().__init__()
        self.player_repo: PlayerRepository = player_repo
    
    def register_new_player(self):
        editor = PlayerEditor()
        player = editor.prompt_for_player_data(Player())
        try:
            if player.is_valid():
                self.player_repo.add(player)
                self.player_repo.commit_changes()
                self.status.notify_success(f"New player registered with ID: {player.id()}")
            else:
                self.status.notify_failure("Can't register player with invalid or incomplete data. Abandon.")
        except KeyError as e:
            logger.exception(e)
            self.status.notify_failure("Failed to register player: Duplicate or invalid Player ID. Abandon.")
        except Exception as e:
            logger.exception(e)
            self.status.notify_failure("Failed to register player because of an unexpected error. Abandon.")

if __name__ == '__main__':
    logging.basicConfig(filename="./debug.log", level=logging.DEBUG)
    from app import DATADIR
    from pathlib import Path
    player_json_file = Path(DATADIR, 'players.json').resolve()
    manager = PlayerManager(PlayerRepository(player_json_file))
    for i in range(3):
        manager.status.notify(f"Register New Player, attempt {i+1}")
        manager.register_new_player()
