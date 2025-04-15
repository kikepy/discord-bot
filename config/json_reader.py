import json

class TokenReader:
    def __init__(self, file_path):
        self.file_path = file_path


    def get_token(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read().lstrip('\ufeff')
                data = json.loads(content)
                return data.get("token")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading token from file: {e}")
            return None