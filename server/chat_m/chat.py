import json
from datetime import datetime
from data_m.database import Database

class Chat:
    def __init__(self, chat_id=None, topic=None, timestamp=None, messages=None, 
                 summary=None, temperature=None, system_msg=None):
         
        # Initialize a Chat object to manage a single chat session.
        # 
        # :param chat_id: Unique identifier for the chat
        # :param timestamp: Creation time of the chat
        # :param messages: List of message dictionaries
        
        self.topic = topic or "__NONE__"
        self.id = chat_id or self._generate_chat_id()
        self.timestamp = timestamp or datetime.now().isoformat()
        self.messages = messages or []
        self.summary = summary or []
        self.temperature = temperature or "0.7"
        self.system_msg = system_msg or "none"
                
        self.last_summary = ""
        self.new_messages = []
        self.is_summary = False
        
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
        
    def add_summary(self, summary):
        self.is_summary = True
        self.summary.append(self.last_summary)
        self.last_summary = ""
        self.last_summary = summary
        
    def get_last_summary(self):
        return self.last_summary
    
    def save_messages(self, user, name, new):
        
        if new == True:
            info = self.to_dict()
            self.db.create_new_chat(user, name, info)
            self.save_messages(user, name, False)
            
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
            "messages": self.messages,
            "summary": self.summary,
            "temperature": self.temperature,
            "system_msg": self.system_msg
        }

    def get_is_summary(self):
        sum = self.is_summary
        self.is_summary = False
        return sum

    @staticmethod
    def _generate_chat_id():
        # Generate a unique chat ID based on timestamp. 
        return datetime.now().strftime("Chat-%Y%m%d%H%M%S")

    def __repr__(self):
        return f"Chat(id={self.id}, messages_count={len(self.messages)})"