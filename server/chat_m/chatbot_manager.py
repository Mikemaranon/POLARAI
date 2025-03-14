import os
import json
from chat_m.chatbot import Chatbot

BOT_OWNERSHIP_PATH = "server/data/bot-ownership.json"

class ChatbotManager:
    def __init__(self, user):
        self.user = user
        self.chatbots = self.load_chatbots(user)

    def load_chatbots(self, user):
         
        # Loads the chatbots for a user from `bot-ownership.json`.
        # 
        # :param user: Name of the user.
        # :return: Dictionary with the chatbots available for the user.
         
        if not os.path.exists(BOT_OWNERSHIP_PATH):
            return {}

        with open(BOT_OWNERSHIP_PATH, "r") as file:
            bot_ownership = json.load(file)

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
                chat_history=bot_data["chat-history"]
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

    def send_message(self, bot_name, message):
         
        # Sends a message to a chatbot and returns the response.
        #
        # :param bot_name: Name of the chatbot.
        # :param message: Message to send to the chatbot.
        # :return: Response from the chatbot, or error if the chatbot is not found.
         
        chatbot = self.get_chatbot(bot_name)
        if chatbot:
            return chatbot.send_message(message)
        else:
            return f"El chatbot '{bot_name}' no está disponible para el usuario '{self.user}'."
