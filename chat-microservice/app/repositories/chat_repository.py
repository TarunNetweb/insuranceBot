from sqlalchemy.orm import Session
from sqlalchemy import select, or_, desc
from app.models.chat_model import ChatMessage
from app.repositories.base_repository import BaseRepository
from typing import Any

class ChatRepository(BaseRepository[ChatMessage]):
    def __init__(self, db: Session):
        super().__init__(db, ChatMessage)

    def create_message(self, message_data: dict[str, Any]) -> ChatMessage:
        # The BaseRepository.create already handles this, but if specific logic is needed,
        # it can be implemented here. For now, we can leverage the base method.
        # Ensure message_data keys match ChatMessage model attributes.
        return super().create(**message_data)

    def get_messages_by_room(self, room_id: str, limit: int = 100, offset: int = 0) -> list[ChatMessage]:
        statement = (
            select(self.model)
            .filter(self.model.room_id == room_id)
            .order_by(desc(self.model.timestamp)) # Assuming newest messages first
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(statement).scalars().all())

    def get_direct_messages(
        self, user_one_id: int, user_two_id: int, limit: int = 100, offset: int = 0
    ) -> list[ChatMessage]:
        statement = (
            select(self.model)
            .filter(
                or_(
                    (self.model.sender_id == user_one_id) & (self.model.receiver_id == user_two_id),
                    (self.model.sender_id == user_two_id) & (self.model.receiver_id == user_one_id),
                )
            )
            .filter(self.model.room_id == None) # Ensure these are direct messages, not room messages
            .order_by(desc(self.model.timestamp)) # Assuming newest messages first
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(statement).scalars().all())
