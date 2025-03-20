import os
import json
import requests
import http.client
from datetime import datetime
from chat_m.chat import Chat
from chat_m.summary_maker import SummaryMaker
from data_m.database import Database

DATA_PATH = "server/data/chat-history/"  # Ubicación de los historiales de chat

class Chatbot:
    def __init__(self, user, name, api_key, endpoint, path):
        
        # Initializes a Chatbot object with its name, API key, endpoint, and owning user.
        
        # :param user: Name of the user who owns this chatbot.
        # :param name: Name of the chatbot (e.g., "google-gemini", "azure-gpt-4o-mini").
        # :param api_key: API key for authentication.
        # :param endpoint: URL of the AI model endpoint.
        
        self.user = user
        self.name = name
        self.api_key = api_key
        self.endpoint = endpoint 
        self.path = path
        self.db = Database()     
        self.summary_maker = SummaryMaker()
        
        self.chats = self.load_chats()
        
    def load_chats(self):
        
        # Loads the chat history from the JSON file.
        
        # :return: List of Chat objects with the data from the JSON file.
         
        chat_list = []
        chats_file = self.db.load_chat_history(self.user, self.name)
                
        for chat in chats_file:
            chat_list.append(Chat (
                chat_id = chat["id"],
                topic = chat["topic"],
                timestamp = chat["timestamp"],
                messages = chat["messages"],
                summary = chat.get("summary", ""),
                temperature = chat.get("temperature", "0.7"),
                system_msg = chat.get("system_msg", "")
            ))
            
        return chat_list
        
    def send_message(self, user, context, message, chat_id):
        
        # Sends a message to the chatbot and saves the conversation in the history.
        #
        # :param message: Input text for the model.
        # :return: Response generated by the model.
        
        # LEER DE LA BASE DE DATOS
        #   TODO: crear archivo para cada modelo
        #   TODO: crear método en la base de datos
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = json.dumps({
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": context + '\n\n' + message}
            ],
            "max_tokens": 1000,
            "temperature": 1.0
        })

        # Buscar el chat correspondiente o crear uno nuevo
        target_chat = None
        new = True

        for chat in self.chats:
            if chat.id == chat_id:
                target_chat = chat
                new = False
                break

        if target_chat is None:
            target_chat = self.new_chat(chat_id)
            self.chats.append(target_chat)

        # Establecer conexión con modelo
        conn = http.client.HTTPSConnection(self.endpoint)

        try:
            conn.request("POST", self.path, body=payload, headers=headers)
            response = conn.getresponse()

            if response.status != 200:
                raise Exception(f"Error {response.status}: {response.reason}")

            response_data = json.loads(response.read().decode())
            bot_response = response_data.get("choices", [{}])[0].get("message", {}).get("content", "Error: No se recibió respuesta.")

            self.summary_maker.set_session_info(self.user, self.name, chat_id)

            # Guardar mensaje en historial
            target_chat.add_message("user", message)
            target_chat.add_message("bot", bot_response)
            
            self.summary_maker.add_message("user", message)
            sum = self.summary_maker.add_message("bot", bot_response)
            print(f"Tipo de sum: {type(sum)} - Contenido: {sum}")
            
            if sum != 0:
                target_chat.add_summary(sum)
                
        except Exception as e:
            bot_response = f"Error: {str(e)}"

        finally:
            conn.close()

        target_chat.save_messages(user, self.name, new)

        return bot_response
    

    def new_chat(self, chat_id):
        
        # Saves a new chat.

        # :param user_message: User's message.
        # :param bot_message: Chatbot's response.
        
        new_chat = Chat (
            chat_id = chat_id,
        )
        
        return new_chat

    def is_summary(self, chat_id):
        for chat in self.chats:
            if chat.id == chat_id:
                return chat.get_is_summary()
        # return False if no chat is found
        return False 


    def get_last_summary(self, chat_id):
        return self.chats[chat_id].get_last_summary()

    def __repr__(self):
        return f"Chatbot(user={self.user}, name={self.name}, endpoint={self.endpoint})"
