import json


class Config:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    @staticmethod
    def from_json_file(filename: str):
        with open(filename) as f:
            config_json = json.load(f)

        return Config.from_dict(config_json)

    @staticmethod
    def from_dict(config_dict: dict):
        return Config(
            bot_token=config_dict['bot_token']
        )
