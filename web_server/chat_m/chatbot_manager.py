import os
import json
from chat_m.chatbot import Chatbot
from data_m.database import Database, USERNAME, PASSWORD, MODEL, CHAT_ID

class ChatbotManager:
    
    # static ini
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ChatbotManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance    
    
    def __init__(self):
        self.user_ownership_list = {}
        self.db = Database()
        
    # ================ class content ================ #
        
    def set_session(self, user):
        self.user_ownership_list = self.load_chatbots(user)

    def load_chatbots(self, user):
         
        # Loads the chatbots for a user from `bot-ownership.json`.
        # 
        # :param user: Name of the user.
        # :return: Dictionary with the chatbots available for the user.

        # bot_ownership = self.db.load_chatbots_file()
        
        bot_ownership = self.db.load_chatbots_file(user)
        ownership_list = self.user_ownership_list

        user_bots = bot_ownership[user]
        ownership_list[user] = []
        
        for bot_name, bot_data in user_bots.items():
            ownership_list[user].append(
                Chatbot(
                    user=user,
                    name=bot_name,
                    api_key=bot_data["API_KEY"],
                    endpoint=bot_data["API_ENDPOINT"],
                    path=bot_data["API_PATH"]
                )
            )            
        
        return ownership_list

    def get_chatbot(self, user, bot_name):
         
        # Gets a specific chatbot for the user.
        #
        # :param bot_name: Name of the chatbot.
        # :return: `Chatbot` object if it exists, otherwise `None`.
        if user in self.user_ownership_list:
            chatbots = self.user_ownership_list[user]
        
        if bot_name in chatbots:
            return chatbots[bot_name]
        return None

    def manager_send_message(self, user, bot_name, system_msg, temperature, context, message, chat_id):
         
        # Sends a message to a chatbot and returns the response.
        #
        # :param bot_name: Name of the chatbot.
        # :param message: Message to send to the chatbot.
        # :return: Response from the chatbot, or error if the chatbot is not found.
         
        chatbot = self.get_chatbot(user, bot_name)
        if chatbot:
            return chatbot.send_message(user, system_msg, temperature, context, message, chat_id)
        else:
            return f"El chatbot '{bot_name}' no está disponible para el usuario '{user}'."

    def get_user_bots(self, user):
        return self.db.get_user_bots_list(user)
    
    # TODO: define function to update the [Object chatbot] and database
    def save_user_bots(self, user):
        return 0
    
    def is_summary(self, model, chat_id):        
        return self.get_chatbot(model).is_summary(chat_id)
    
    def get_last_summary(self, model, chat_id):
        return self.get_chatbot(model).get_last_summary(chat_id)