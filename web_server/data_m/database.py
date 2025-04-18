import os
import json

USER_FILE = "users.json"
BOTS_PATH = "bots_ownership/"
CHAT_PATH = "chat_history/"

# SESSION PARAMS
USERNAME = 'username'
PASSWORD = 'password'
MODEL = 'model'
CHAT_ID = 'chat-id'

# DB PARAMS
MESSAGES = "messages"
SUMMARY = "summary"
TEMP = "temperature"
SYS_MSG = "system_msg"

class Database:
    
    # static ini
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.users_file = os.path.join(os.path.dirname(__file__), USER_FILE)
        self.bots_path = os.path.join(os.path.dirname(__file__), BOTS_PATH)
        self.chat_path = os.path.join(os.path.dirname(__file__), CHAT_PATH)
        self.chat_history_path = None
    
    # ================= USERS ================= #
    
    def load_users(self):
        with open(self.users_file, "r") as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=4)
            
    def add_user(self, username: str, password: str):
        users = self.load_users()
        users[username] = {"password": password}
        self.save_users(users)

    def delete_user(self, username: str):
        users = self.load_users()
        users.pop(username)
        self.save_users(users)
    
    def get_user(self, username: str):
        users = self.load_users()
        return users.get(username)
    
    def get_userdata(self, username: str):
        users = self.load_users()
        return users.get(username)

    def get_user_bots_list(self, user):
        bots_file = self.load_chatbots_file(user)
        
        if user in bots_file:
            bots = list(bots_file[user].keys())
        
        return bots
    
    # ================= CHATBOTS =================
    
    # def load_chatbots_file(self):
    #     with open(self.bots_path, "r") as f:
    #         return json.load(f)
        
    def load_chatbots_file(self, user):
        chatbot_file = os.path.join(self.bots_path, f"{user}.json")
        with open(chatbot_file, "r") as f:
            return json.load(f)    
        
    def save_chatbots_file(self, user, chatbots):
        chatbot_file = os.path.join(self.bots_path, f"{user}.json")
        with open(chatbot_file, "w") as f:
            json.dump(chatbots, f, indent=4)
            
    def delete_model(self, user, bot_name):
        chat_history_path = os.path.join(self.chat_path, user, f"{bot_name}.json")
        os.remove(chat_history_path)
        
    # ================= CHATS =================
                       
    def create_new_chat(self, user, bot_name, chat_info):
        
        # self.ensure_chat_file_exists(user, bot_name)
        chat_history_path = os.path.join(self.chat_path, user, f"{bot_name}.json")

        chats = self.load_chat_history(user, bot_name)  

        # Agregar nuevo chat
        chats.append(chat_info)

        with open(chat_history_path, "w") as f:
            json.dump(chats, f)
            
    def ensure_chat_file_exists(self, user, bot_name):
        
        user_chat_dir = os.path.join(self.chat_path, user)
        chat_history_file = os.path.join(user_chat_dir, f"{bot_name}.json")

        # Crear directorio si no existe
        if not os.path.exists(user_chat_dir):
            os.makedirs(user_chat_dir)

        # Crear archivo si no existe
        if not os.path.exists(chat_history_file):
            with open(chat_history_file, "w") as f:
                json.dump([], f, indent=4)
    
    def load_chat_history(self, user, bot_name):
        chat_history_path = os.path.join(self.chat_path, user, f"{bot_name}.json")
        with open(chat_history_path, "r") as f:
            return json.load(f)
    
    def save_chat_config(self, id, user, bot_name, summary_list, temperature, system_msg):
        
        chat_history_path = os.path.join(self.chat_path, user, f"{bot_name}.json")
        
        # Read existing chats
        chats = self.load_chat_history(user, bot_name)
        
        for chat in chats:
            if chat["id"] == id:
                chat[SUMMARY] = summary_list
                chat[TEMP] = temperature
                chat[SYS_MSG] = system_msg
                break
        
        # Save updated chats back to file
        with open(chat_history_path, "w") as f:
            json.dump(chats, f, indent=4)
    
    def save_chat_history(self, id, user, bot_name, new_messages):
        chat_history_path = os.path.join(self.chat_path, user, f"{bot_name}.json")
        
        # Read existing chats
        chats = self.load_chat_history(user, bot_name)
            
        # Update messages for the specific chat ID
        for chat in chats:
            if chat["id"] == id:
                for message in new_messages:
                    chat[MESSAGES].append(message)
                break
        
        # Save updated chats back to file
        with open(chat_history_path, "w") as f:
            json.dump(chats, f, indent=4)

    def delete_chat(self, user, bot_name, id):
        chat_history_path = os.path.join(self.chat_path, user, f"{bot_name}.json")
        
        # Remove the content of the file corresponding to the chat
        with open(chat_history_path, "r") as f:
            chats = json.load(f)
            new_chats = [chat for chat in chats if chat["id"] != id]
        with open(chat_history_path, "w") as f:
            json.dump(new_chats, f, indent=4)
        
           
    def load_summary_list(self, user, bot_name, chat_id):
        chats = self.load_chat_history(user, bot_name)
        for chat in chats:
            if chat["id"] == chat_id:
                return chat["summary"]
        
    def save_summary_list(self, id, user, bot_name, new_sum_list):
        chat_history_path = os.path.join(self.chat_path, user, f"{bot_name}.json")
        
        # Read existing chats
        chats = self.load_chat_history(user, bot_name)
            
        # Update messages for the specific chat ID
        for chat in chats:
            if chat["id"] == id:
                chat["summary"] = new_sum_list
                break
        
        # Save updated chats back to file
        with open(chat_history_path, "w") as f:
            json.dump(chats, f, indent=4)
        
    