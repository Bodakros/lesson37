import json

class ConfigApi:
    def __init__(self, filename):
        self.api_key = None
        self.api_hash = None
        self.bot_token = None

        with open(filename, 'r') as f:
            data = json.load(f)
            self.api_key = data['api']['id']
            self.api_hash = data['api']['hash']
            self.phone = data['api']['phone']
            self.bot_token = data['api']['bot_token']