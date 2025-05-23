from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base_model import BaseModel
from .user_model import User # Ensure User model is imported for relationships

class ChatMessage(BaseModel):
    """
    Represents a chat message in the system.
    A message can be either a direct message between two users or a message in a room.
    """
    __tablename__ = "chat_messages"

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for room-based messages (if room_id is set)
    room_id = Column(String, nullable=True) # Nullable for direct messages (if receiver_id is set)
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Define relationships (optional but good practice)
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
