import os
import json

DB_FILE = "users.json"
BOTS_FILE = "bot-ownership.json"
DATA_PATH = "chat-history/"

class Database:
    def __init__(self):
        self.db_file = os.path.join(os.path.dirname(__file__), DB_FILE)
        self.bots_file = os.path.join(os.path.dirname(__file__), BOTS_FILE)
        self.data_path = os.path.join(os.path.dirname(__file__), DATA_PATH)
        self.chat_history_path = None
    
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
        
    def load_chat_history(self, user, bot_name):
        chat_history_path = os.path.join(self.data_path, user, f"{bot_name}.json")
        with open(chat_history_path, "r") as f:
            return json.load(f)
        
    def save_chat_history(self, user, bot_name, new_messages):
        chat_history_path = os.path.join(self.data_path, user, f"{bot_name}.json")
        with open(chat_history_path, "w") as f:
            json.dump(new_messages, f, indent=4)
    
    def create_new_chat(self,  user, bot_name, chat_info):
        chat_history_path = os.path.join(self.data_path, user, f"{bot_name}.json")
        with open(chat_history_path, "w") as f:
            json.dump(chat_info, f)