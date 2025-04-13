import json

class TokenReader:
    def __init__(self, file_path):
        self.file_path = file_path


    def get_token(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                return data.get("token")
        except (FileNotFoundError, json.JSONDecoderError) as e:
            print(f"Error reading token from file: {e}")
            return None