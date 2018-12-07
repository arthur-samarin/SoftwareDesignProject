class Game:
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name

    def get_initial_data_for_player(self, id):
        pass

    def validate_move(self, id, data):
        pass

    def handle_player_move(self, id, data):
        pass

    def check_win(self):
        pass
