import json
from datetime import datetime
from data_m.database import Database

class Chat:
    def __init__(self, chat_id, topic, timestamp, messages):
         
        # Initialize a Chat object to manage a single chat session.
        # 
        # :param chat_id: Unique identifier for the chat
        # :param timestamp: Creation time of the chat
        # :param messages: List of message dictionaries
         
        self.id = chat_id or self._generate_chat_id()
        self.topic = topic
        self.timestamp = timestamp or datetime.now().isoformat()
        self.messages = messages or []
        self.new_messages = []
        
        self.db = Database()

    def add_message(self, sender, content):
         
        # Add a new message to the chat.
        # 
        # :param sender: Either 'user' or 'bot'
        # :param content: Content of the message
        
        self.new_messages.append({
            "sender": sender,
            "content": content
        })
        
    def save_messages(self, user, name, new):
        
        if new == True:
            info = {
                "id": self.id,
                "timestamp": self.timestamp,
                "messages": self.messages
            }
            self.db.create_new_chat(user, name, info)
        else: 
            # Save new messages to the chat history.
            self.db.save_chat_history(self.id, user, name, self.new_messages)
        
        self.messages.extend(self.new_messages)
        self.new_messages = []

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "timestamp": self.timestamp,
            "messages": self.messages
        }

    @staticmethod
    def _generate_chat_id():
        # Generate a unique chat ID based on timestamp. 
        return datetime.now().strftime("Chat-%Y%m%d%H%M%S")

    def __repr__(self):
        return f"Chat(id={self.id}, messages_count={len(self.messages)})"