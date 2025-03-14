import os
import json
from chat_m.chatbot import Chatbot
from data_m.database import Database

class ChatbotManager:
    def __init__(self, db: Database):
        self.session = None
        self.user = None
        self.chatbots = {}
        self.db = db
        
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

        bot_ownership = self.db.load_chatbots_file()

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
                db=self.db
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

    def _send_message(self, bot_name, context, message, chat_id):
         
        # Sends a message to a chatbot and returns the response.
        #
        # :param bot_name: Name of the chatbot.
        # :param message: Message to send to the chatbot.
        # :return: Response from the chatbot, or error if the chatbot is not found.
         
        chatbot = self.get_chatbot(bot_name)
        if chatbot:
            return chatbot.send_message(context, message, chat_id)
        else:
            return f"El chatbot '{bot_name}' no está disponible para el usuario '{self.user}'."

    