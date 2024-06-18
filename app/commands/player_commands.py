from app.commands.commands_abc import CommandInterface
from app.models.player_model import Player


class UpdatePlayerDataCommand(CommandInterface):

    def __init__(self, receiver, old_player_data: Player):
        self.receiver = receiver
        self.old_player_data: Player = old_player_data
        self.new_player_data: Player = None

    def execute(self):
        self.receiver._update_player(new_player_data=self.old_player_data,
                                     old_player_data=self.old_player_data)
