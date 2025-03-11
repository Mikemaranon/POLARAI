import os
import json

class Database:
    
    def __init__(self, db_file: str):
        self.db_file = os.path.join(os.path.dirname(__file__), db_file)
    
    def load_users(self):
        with open(self.db_file, "r") as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.db_file, "w") as f:
            json.dump(users, f, indent=4)

    def get_user(self, username: str):
        users = self.load_users()
        return users.get(username)
