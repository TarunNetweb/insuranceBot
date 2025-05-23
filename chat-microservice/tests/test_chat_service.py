import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.chat_service import ChatService, sio
from app.models.chat_model import ChatMessage # For constructing expected objects
from app.repositories.chat_repository import ChatRepository # For type hinting mock spec

# Mark all tests in this file as asyncio tests for pytest
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_db_session():
    """Fixture for a mock database session."""
    return MagicMock()

@pytest.fixture
def mock_chat_repository_instance():
    """
    Fixture for a mock ChatRepository instance.
    The create_message method is mocked to return a predefined ChatMessage.
    """
    repo_instance = MagicMock(spec=ChatRepository)
    # ChatRepository.create_message is synchronous but called via asyncio.to_thread in ChatService.
    # The mock here simulates its behavior when called.
    repo_instance.create_message = MagicMock(
        return_value=ChatMessage(
            id=1, # Default ID for messages created by this mock
            sender_id=1, # Default sender
            receiver_id=None,
            room_id="test_room", # Default room
            message_content="hello", # Default content
            timestamp=MagicMock() # Mock timestamp as it's usually auto-generated
        )
    )
    return repo_instance

async def test_send_room_message_saves_and_broadcasts(mock_db_session, mock_chat_repository_instance):
    """
    Tests that send_room_message:
    1. Correctly instantiates ChatRepository.
    2. Calls chat_repository.create_message with appropriate data.
    3. Broadcasts the message using sio.emit to the correct room.
    This test assumes ChatService correctly uses asyncio.to_thread for sync repository calls.
    """
    # Patch ChatRepository where it's instantiated by ChatService.
    with patch('app.services.chat_service.ChatRepository', return_value=mock_chat_repository_instance) as MockedChatRepository:
        # Patch sio.emit, which is an async method.
        with patch.object(sio, 'emit', new_callable=AsyncMock) as mock_sio_emit:
            
            chat_service = ChatService(db_session=mock_db_session)

            test_sid = "test_sid_room"
            test_room_id = "test_room"
            test_message_content = "hello room"
            test_sender_id = 1
            
            # The mocked create_message will return a message with id=1 by default.
            # We can update its return_value if specific test data is needed for assertions here.
            mock_chat_repository_instance.create_message.return_value = ChatMessage(
                id=123, sender_id=test_sender_id, room_id=test_room_id, 
                message_content=test_message_content, timestamp=MagicMock()
            )

            await chat_service.send_room_message(
                sid=test_sid,
                room_id=test_room_id,
                message_content=test_message_content,
                sender_id=test_sender_id
            )

            # Verify ChatRepository instantiation
            MockedChatRepository.assert_called_once_with(mock_db_session)

            # Verify chat_repository.create_message call
            mock_chat_repository_instance.create_message.assert_called_once()
            args_create_message, _ = mock_chat_repository_instance.create_message.call_args
            expected_message_data = {
                "sender_id": test_sender_id,
                "room_id": test_room_id,
                "message_content": test_message_content,
                "receiver_id": None
            }
            assert args_create_message[0] == expected_message_data

            # Verify sio.emit call
            mock_sio_emit.assert_called_once()
            args_emit, kwargs_emit = mock_sio_emit.call_args
            
            assert args_emit[0] == 'new_message' # Event name
            emitted_data = args_emit[1]
            assert emitted_data['id'] == 123 # From the mocked return_value
            assert emitted_data['sender_id'] == test_sender_id
            assert emitted_data['room_id'] == test_room_id
            assert emitted_data['message_content'] == test_message_content
            assert 'timestamp' in emitted_data
            
            assert kwargs_emit['room'] == test_room_id

async def test_send_direct_message_saves_and_emits(mock_db_session, mock_chat_repository_instance):
    """
    Tests that send_direct_message:
    1. Correctly instantiates ChatRepository.
    2. Calls chat_repository.create_message with appropriate data for a direct message.
    3. Emits the message using sio.emit to the recipient's specific SID (if connected) 
       or their user_id based room for potential delivery.
    This test assumes ChatService correctly uses asyncio.to_thread for sync repository calls.
    """
    test_sid = "test_sid_dm"
    test_receiver_user_id = "2"
    test_receiver_user_sid = "receiver_sid_123" # Assume this SID for a connected receiver
    test_message_content = "hello direct"
    test_sender_id = 1
    
    # Configure the mock repository's create_message for this DM test
    mock_chat_repository_instance.create_message.return_value = ChatMessage(
        id=456, sender_id=test_sender_id, receiver_id=int(test_receiver_user_id),
        message_content=test_message_content, timestamp=MagicMock()
    )

    # Patch ChatRepository and sio.emit
    with patch('app.services.chat_service.ChatRepository', return_value=mock_chat_repository_instance) as MockedChatRepository:
        with patch.object(sio, 'emit', new_callable=AsyncMock) as mock_sio_emit:
            # Mock the connected_users dictionary within ChatService for this test
            # to simulate the receiver being connected.
            with patch('app.services.chat_service.connected_users', {test_receiver_user_id: test_receiver_user_sid}):
                chat_service = ChatService(db_session=mock_db_session)

                await chat_service.send_direct_message(
                    sid=test_sid,
                    receiver_user_id=test_receiver_user_id,
                    message_content=test_message_content,
                    sender_id=test_sender_id
                )

                # Verify ChatRepository instantiation
                MockedChatRepository.assert_called_once_with(mock_db_session)
                
                # Verify chat_repository.create_message call
                mock_chat_repository_instance.create_message.assert_called_once()
                args_create_message, _ = mock_chat_repository_instance.create_message.call_args
                expected_dm_data = {
                    "sender_id": test_sender_id,
                    "receiver_id": int(test_receiver_user_id),
                    "message_content": test_message_content,
                    "room_id": None
                }
                assert args_create_message[0] == expected_dm_data

                # Verify sio.emit call (should be to the specific SID of the receiver)
                mock_sio_emit.assert_called_once()
                args_emit, kwargs_emit = mock_sio_emit.call_args
                
                assert args_emit[0] == 'new_dm' # Event name
                emitted_data = args_emit[1]
                assert emitted_data['id'] == 456 # From the mocked return_value
                assert emitted_data['sender_id'] == test_sender_id
                assert emitted_data['receiver_id'] == int(test_receiver_user_id)
                assert emitted_data['message_content'] == test_message_content
                assert 'timestamp' in emitted_data
                
                # ChatService logic for DMs: emits to specific SID if user is in connected_users
                assert kwargs_emit['room'] == test_receiver_user_sid

# The tests verify that ChatService correctly interacts with ChatRepository
# (using `asyncio.to_thread` for its synchronous methods) and emits Socket.IO events.
# Mocking is used for database sessions, repositories, and sio.emit to isolate ChatService logic.
