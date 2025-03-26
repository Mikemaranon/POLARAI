import os
import json
from chat_m.chatbot import Chatbot
from data_m.database import Database, USERNAME, PASSWORD, MODEL, CHAT_ID

class ChatbotManager:
    def __init__(self):
        self.chatbots = {}
        self.db = Database()
        
        # TODO: integrate in the module to be uses only by ChatbotManager
        # self.summary_maker = SummaryMaker()
        
    def set_session(self, session):
        self.session = session
        self.user = self.get_user()
        self.chatbots = self.load_chatbots(self.user)

    def get_user(self):
         
        # Gets the username from the session.
        #
        # :return: Username if it exists, otherwise `None`.
         
        if 'username' in self.session:
            return self.session['username']
        return None

    def load_chatbots(self, user):
         
        # Loads the chatbots for a user from `bot-ownership.json`.
        # 
        # :param user: Name of the user.
        # :return: Dictionary with the chatbots available for the user.

        # bot_ownership = self.db.load_chatbots_file()
        
        bot_ownership = self.db.load_chatbots_file(user)

        # Checks if the user has configured chatbots
        if user not in bot_ownership:
            return {}

        user_bots = bot_ownership[user]
        chatbots = {}

        # Creates Chatbot objects for each model available to the user
        for bot_name, bot_data in user_bots.items():
            chatbots[bot_name] = Chatbot(
                user=user,
                name=bot_name,
                api_key=bot_data["API_KEY"],
                endpoint=bot_data["API_ENDPOINT"],
                path=bot_data["API_PATH"]
            )

        return chatbots

    def get_chatbot(self, bot_name):
         
        # Gets a specific chatbot for the user.
        #
        # :param bot_name: Name of the chatbot.
        # :return: `Chatbot` object if it exists, otherwise `None`.
         
        if bot_name in self.chatbots:
            return self.chatbots[bot_name]
        return None

    def manager_send_message(self, bot_name, system_msg, temperature, context, message, chat_id):
         
        # Sends a message to a chatbot and returns the response.
        #
        # :param bot_name: Name of the chatbot.
        # :param message: Message to send to the chatbot.
        # :return: Response from the chatbot, or error if the chatbot is not found.
         
        chatbot = self.get_chatbot(bot_name)
        if chatbot:
            return chatbot.send_message(self.session[USERNAME], system_msg, temperature, context, message, chat_id)
        else:
            return f"El chatbot '{bot_name}' no está disponible para el usuario '{self.user}'."

    def set_user_bots(self):
        self.session["user_bots"] = self.db.get_user_bots_list(self.user)

    def get_user_bots(self):
        if "user_bots" not in self.session:
            self.set_user_bots()  # Si no están en la sesión, los carga
        return self.session["user_bots"]
    
    def is_summary(self, model, chat_id):        
        return self.get_chatbot(model).is_summary(chat_id)
    
    def get_last_summary(self, model, chat_id):
        return self.get_chatbot(model).get_last_summary(chat_id)