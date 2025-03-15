import os
import json
import requests
from datetime import datetime
from chat_m.chat import Chat
from data_m.database import Database

DATA_PATH = "server/data/chat-history/"  # Ubicación de los historiales de chat

class Chatbot:
    def __init__(self, user, name, api_key, endpoint):
        
        # Initializes a Chatbot object with its name, API key, endpoint, and owning user.
        
        # :param user: Name of the user who owns this chatbot.
        # :param name: Name of the chatbot (e.g., "google-gemini", "azure-gpt-4o-mini").
        # :param api_key: API key for authentication.
        # :param endpoint: URL of the AI model endpoint.
        
        self.user = user
        self.name = name
        self.api_key = api_key
        self.endpoint = endpoint 
        self.db = Database()     
        
        self.chats = self.load_chats()
        
    def load_chats(self):
        
        # Loads the chat history from the JSON file.
        
        # :return: List of Chat objects with the data from the JSON file.
        
        chat_list = []
        chats_file = self.db.load_chat_history(self.user, self.name)
                
        for chat in chats_file:
            chat_list.append(Chat (
                chat_id = chat["id"],
                timestamp = chat["timestamp"],
                messages = chat["messages"]
            ))
        
        return chat_list
        
    def send_message(self, context, message, chat_id):
        
        # Sends a message to the chatbot and saves the conversation in the history.
        #
        # :param message: Input text for the model.
        # :return: Response generated by the model.
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"input": context + '\n\n' + message}

        for chat in self.chats:
            if chat.id == chat_id:
                target_chat = chat
                break

        target_chat.add_message("user", message)
        
        try:            
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            bot_response = response.json().get("response", "Error: No se recibió respuesta.")
            
            # Guardar mensaje en historial
            target_chat.add_message("bot", bot_response)
            
        except requests.exceptions.RequestException as e:
            bot_response = f"Error: {str(e)}"

        Database.save_chat_history(
            self.user, self.name, 
            target_chat.new_messages            
        )
        target_chat.save_messages(self.user, self.name)
        
        return bot_response

    def new_chat(self, user_message, bot_message):
        
        # Saves a new chat.

        # :param user_message: User's message.
        # :param bot_message: Chatbot's response.
        
        new_chat = Chat()
        self.chats.append(new_chat)

        chat_entry = {
            "id": new_chat.id,
            "timestamp": new_chat.timestamp,
            "messages": [
                {"sender": "user", "content": user_message},
                {"sender": "bot", "content": bot_message}
            ]
        }

        Database.create_new_chat(self.user, self.name, chat_entry)

    def __repr__(self):
        return f"Chatbot(user={self.user}, name={self.name}, endpoint={self.endpoint})"
