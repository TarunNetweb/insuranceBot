from sqlalchemy.orm import Session
from sqlalchemy import select, or_, desc
from app.models.chat_model import ChatMessage
from app.repositories.base_repository import BaseRepository
from typing import Any, List

class ChatRepository(BaseRepository[ChatMessage]):
    """
    Repository for chat message operations.
    Handles database interactions related to ChatMessage model.
    """
    def __init__(self, db: Session):
        """
        Initializes the ChatRepository.

        Args:
            db: The SQLAlchemy database session.
        """
        super().__init__(db, ChatMessage)

    def create_message(self, message_data: dict[str, Any]) -> ChatMessage:
        """
        Creates a new chat message.

        This method leverages the generic `create` method from BaseRepository.
        It can be overridden if specific pre-processing or post-processing logic
        for chat message creation is needed. Ensure `message_data` keys align with
        ChatMessage model attributes.

        Args:
            message_data: A dictionary containing the message attributes.

        Returns:
            The created ChatMessage object.
        """
        # The BaseRepository.create already handles this, but if specific logic is needed,
        # it can be implemented here. For now, we can leverage the base method.
        # Ensure message_data keys match ChatMessage model attributes.
        return super().create(**message_data)

    def get_messages_by_room(self, room_id: str, limit: int = 100, offset: int = 0) -> List[ChatMessage]:
        """
        Retrieves messages for a specific room, ordered by timestamp descending.

        Args:
            room_id: The ID of the room.
            limit: The maximum number of messages to retrieve. Defaults to 100.
            offset: The number of messages to skip. Defaults to 0.

        Returns:
            A list of ChatMessage objects from the specified room.
        """
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
    ) -> List[ChatMessage]:
        """
        Retrieves direct messages between two users, ordered by timestamp descending.
        Ensures that room_id is None for these messages.

        Args:
            user_one_id: The ID of the first user.
            user_two_id: The ID of the second user.
            limit: The maximum number of messages to retrieve. Defaults to 100.
            offset: The number of messages to skip. Defaults to 0.

        Returns:
            A list of direct ChatMessage objects between the two users.
        """
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
