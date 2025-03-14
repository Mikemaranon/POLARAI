import os
import json

DB_FILE = "users.json"
BOTS_FILE = "bot-ownership.json"

class Database:
    
    def __init__(self):
        self.db_file = os.path.join(os.path.dirname(__file__), DB_FILE)
        self.bots_file = os.path.join(os.path.dirname(__file__), BOTS_FILE)
    
    # ================= USERS =================
    
    def load_users(self):
        with open(self.db_file, "r") as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.db_file, "w") as f:
            json.dump(users, f, indent=4)

    def get_user(self, username: str):
        users = self.load_users()
        return users.get(username)
    
    def get_userdata(self, username: str):
        users = self.load_users()
        return users.get(username)

    # ================= CHATBOTS =================
    
    def load_chatbots_file(self):
        with open(self.bots_file, "r") as f:
            return json.load(f)
        
    def save_chatbots_file(self, chatbots):
        with open(self.bots_file, "w") as f:
            json.dump(chatbots, f, indent=4)

    # ================= CHATS =================
