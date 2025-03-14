import json
from datetime import datetime

class Chat:
    def __init__(self, chat_id=None, timestamp=None, messages=None):
         
        # Initialize a Chat object to manage a single chat session.
        # 
        # :param chat_id: Unique identifier for the chat
        # :param timestamp: Creation time of the chat
        # :param messages: List of message dictionaries
         
        self.id = chat_id or self._generate_chat_id()
        self.timestamp = timestamp or datetime.now().isoformat()
        self.messages = messages or []

    def add_message(self, sender, content):
         
        # Add a new message to the chat.
        # 
        # :param sender: Either 'user' or 'bot'
        # :param content: Content of the message
         
        self.messages.append({
            "sender": sender,
            "content": content
        })

    def to_dict(self):
        # Convert chat to dictionary format for storage. 
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "messages": self.messages
        }

    @classmethod
    def from_dict(cls, chat_dict):
        # Create a Chat instance from a dictionary. 
        return cls(
            chat_id=chat_dict["id"],
            timestamp=chat_dict["timestamp"],
            messages=chat_dict["messages"]
        )

    @staticmethod
    def _generate_chat_id():
        # Generate a unique chat ID based on timestamp. 
        return datetime.now().strftime("Chat-%Y%m%d%H%M%S")

    def __repr__(self):
        return f"Chat(id={self.id}, messages_count={len(self.messages)})"