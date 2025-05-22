from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base_model import BaseModel
from .user_model import User # Ensure User model is imported for relationships

class ChatMessage(BaseModel):
    __tablename__ = "chat_messages"

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for room-based messages
    room_id = Column(String, nullable=True) # Nullable for direct messages
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Define relationships (optional but good practice)
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
