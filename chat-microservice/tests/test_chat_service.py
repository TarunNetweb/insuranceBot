import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.chat_service import ChatService, sio
from app.models.chat_model import ChatMessage # For constructing expected objects and return types
from app.repositories.chat_repository import ChatRepository # For type hinting if needed

# Mark all tests in this file as asyncio tests for pytest
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_db_session():
    """Fixture for a mock database session."""
    return MagicMock() # Using MagicMock for db_session as it's passed to sync ChatRepository

@pytest.fixture
def mock_chat_repository_instance():
    """Fixture for a mock ChatRepository instance."""
    repo = MagicMock(spec=ChatRepository) # Use MagicMock for the repo instance
    # Mock the async method `create_message` if it were async
    # Since ChatRepository.create_message is synchronous, its mock should be MagicMock
    repo.create_message = MagicMock(
        return_value=ChatMessage(
            id=1,
            sender_id=1,
            receiver_id=None,
            room_id="test_room",
            message_content="hello",
            timestamp=None # Timestamp is usually set by DB or default_factory
        )
    )
    return repo

async def test_send_room_message_saves_and_broadcasts(mock_db_session, mock_chat_repository_instance):
    """
    Tests that send_room_message correctly calls repository's create_message
    and broadcasts using sio.emit.
    """
    # Patch ChatRepository in the module where ChatService looks it up.
    # ChatService creates its own ChatRepository instance.
    with patch('app.services.chat_service.ChatRepository', return_value=mock_chat_repository_instance) as MockedChatRepository:
        # Patch sio.emit where it's defined (app.services.chat_service.sio)
        # sio.emit is an async method, so use AsyncMock
        with patch.object(sio, 'emit', new_callable=AsyncMock) as mock_sio_emit:
            
            # Instantiate ChatService. It will use the patched ChatRepository.
            # ChatService constructor expects a db_session.
            chat_service = ChatService(db_session=mock_db_session)

            test_sid = "test_sid_room"
            test_room_id = "test_room"
            test_message_content = "hello room"
            test_sender_id = 1

            # Call the method to be tested
            # send_room_message is async, so await it
            await chat_service.send_room_message(
                sid=test_sid,
                room_id=test_room_id,
                message_content=test_message_content,
                sender_id=test_sender_id
            )

            # Assert that ChatRepository was instantiated correctly within ChatService
            MockedChatRepository.assert_called_once_with(mock_db_session)

            # Assert that chat_repository.create_message was called
            # The ChatService's send_room_message has a placeholder for create_message.
            # For this test to pass as is, the placeholder logic in ChatService needs to be active.
            # If the actual create_message were called, this assertion would be:
            # mock_chat_repository_instance.create_message.assert_called_once()
            # And we would check its arguments.
            # Given the current ChatService, create_message is NOT called.
            # This test will reflect the placeholder logic.
            # TO MAKE THIS TEST THE ACTUAL DB INTERACTION:
            # 1. ChatService's send_room_message must call self.chat_repository.create_message
            # 2. That call must be `await asyncio.to_thread(self.chat_repository.create_message, message_data)`
            
            # For now, let's assume the placeholder logic is what we test:
            # So, create_message will not have been called.
            # mock_chat_repository_instance.create_message.assert_not_called() # If placeholder is active

            # If we assume the placeholder is bypassed and create_message IS called (ideal test):
            # This requires ChatService to be modified to actually call it.
            # Let's write the test as if ChatService *does* call create_message.
            # This means the test might fail until ChatService is updated.
            mock_chat_repository_instance.create_message.assert_called_once()
            args_create_message, _ = mock_chat_repository_instance.create_message.call_args
            expected_message_data = {
                "sender_id": test_sender_id,
                "room_id": test_room_id,
                "message_content": test_message_content,
                "receiver_id": None
            }
            assert args_create_message[0] == expected_message_data


            # Assert that sio.emit was called
            mock_sio_emit.assert_called_once()
            args_emit, kwargs_emit = mock_sio_emit.call_args
            
            assert args_emit[0] == 'new_message' # Event name
            # The data sent by sio.emit in ChatService (currently placeholder)
            # We need to check the structure of args_emit[1] based on ChatService's implementation
            # ChatService's placeholder:
            # saved_message = ChatMessage(**message_data, id=1, timestamp=None)
            # data_to_send = { "id": saved_message.id, "sender_id": ..., "room_id": ..., "message_content": ..., "timestamp": ...}
            assert args_emit[1]['sender_id'] == test_sender_id
            assert args_emit[1]['room_id'] == test_room_id
            assert args_emit[1]['message_content'] == test_message_content
            assert 'id' in args_emit[1] # Placeholder gives it an id
            
            assert kwargs_emit['room'] == test_room_id

async def test_send_direct_message_saves_and_emits(mock_db_session, mock_chat_repository_instance):
    """
    Tests that send_direct_message correctly calls repository's create_message
    and emits using sio.emit to the correct user room.
    """
    # Adjust the mock repository's return value for this specific test if needed
    mock_chat_repository_instance.create_message.return_value = ChatMessage(
        id=2, # Different ID for this message
        sender_id=1,
        receiver_id=2,
        message_content="hello direct",
        timestamp=None
    )

    with patch('app.services.chat_service.ChatRepository', return_value=mock_chat_repository_instance) as MockedChatRepository:
        with patch.object(sio, 'emit', new_callable=AsyncMock) as mock_sio_emit:
            chat_service = ChatService(db_session=mock_db_session)

            test_sid = "test_sid_dm"
            test_receiver_user_id = "2" # Corresponds to receiver_id=2
            test_message_content = "hello direct"
            test_sender_id = 1

            await chat_service.send_direct_message(
                sid=test_sid,
                receiver_user_id=test_receiver_user_id,
                message_content=test_message_content,
                sender_id=test_sender_id
            )

            MockedChatRepository.assert_called_once_with(mock_db_session)
            
            # Similar to the room message, this assumes ChatService calls create_message.
            mock_chat_repository_instance.create_message.assert_called_once()
            args_create_message, _ = mock_chat_repository_instance.create_message.call_args
            expected_dm_data = {
                "sender_id": test_sender_id,
                "receiver_id": int(test_receiver_user_id),
                "message_content": test_message_content,
                "room_id": None
            }
            assert args_create_message[0] == expected_dm_data

            mock_sio_emit.assert_called_once()
            args_emit, kwargs_emit = mock_sio_emit.call_args
            
            assert args_emit[0] == 'new_dm'
            assert args_emit[1]['sender_id'] == test_sender_id
            assert args_emit[1]['receiver_id'] == int(test_receiver_user_id)
            assert args_emit[1]['message_content'] == test_message_content
            assert 'id' in args_emit[1]

            # ChatService emits to a room named after receiver_user_id for DMs
            assert kwargs_emit['room'] == test_receiver_user_id

# Note: These tests currently assume that the placeholder logic in 
# ChatService's send_room_message and send_direct_message for database interaction
# (i.e., the try-except block for self.chat_repository.create_message)
# is MODIFIED to actually call self.chat_repository.create_message.
# If the ChatService still uses the "dummy" ChatMessage object creation
# and does NOT call self.chat_repository.create_message, the assertions for
# mock_chat_repository_instance.create_message.assert_called_once() will fail.
# The tests are written to test the *intended* behavior (saving the message).
# The ChatService might require `await asyncio.to_thread(self.chat_repository.create_message, ...)`
# for these calls to work correctly in an async context with a sync repository.
# For the purpose of this subtask, the test structure and assertions for the *intended* logic are provided.I have completed the steps for this subtask.

1.  **Inspect Existing Test Structure:**
    *   I listed files in `chat-microservice/tests/` and found `__init__.py` and `conftest.py`.
    *   I read `chat-microservice/tests/conftest.py` and found it to be empty. This indicates no predefined global fixtures are available.
    *   No other test files were explicitly mentioned to exist or read, so the pattern is to create new test files. The use of `conftest.py` and the subtask instructions point towards using `pytest`.

2.  **Create Test File for Chat Service:**
    *   I created the file `chat-microservice/tests/test_chat_service.py`.

3.  **Write Basic Tests for `ChatService` in `test_chat_service.py`:**
    *   **Imports:** Added `pytest`, `asyncio`, `unittest.mock.AsyncMock`, `unittest.mock.MagicMock`, `unittest.mock.patch`, `ChatService`, `sio` (from `app.services.chat_service`), `ChatMessage` (from `app.models.chat_model`), and `ChatRepository` (from `app.repositories.chat_repository` for type hinting).
    *   **Pytest Marker:** Added `pytestmark = pytest.mark.asyncio` to mark all tests in the file for `pytest-asyncio`.
    *   **Fixtures:**
        *   `mock_db_session()`: Returns a `MagicMock` for the database session.
        *   `mock_chat_repository_instance()`: Returns a `MagicMock` for `ChatRepository`, with its `create_message` method also a `MagicMock` returning a sample `ChatMessage`. This is because `ChatRepository.create_message` is a synchronous method.
    *   **Test Case 1: `test_send_room_message_saves_and_broadcasts` (async def)**
        *   Patched `app.services.chat_service.ChatRepository` to control the instance of `ChatRepository` used by `ChatService`. The patched repository is `mock_chat_repository_instance`.
        *   Patched `sio.emit` (from `app.services.chat_service.sio.emit`) using `patch.object(sio, 'emit', new_callable=AsyncMock)` because `sio.emit` is an async method.
        *   Instantiated `ChatService` with `mock_db_session`.
        *   Called `await chat_service.send_room_message(...)` with sample data.
        *   Asserted that `MockedChatRepository` (the patched class) was called once with `mock_db_session`.
        *   Asserted that `mock_chat_repository_instance.create_message` was called once with the expected message data. **(This assertion assumes `ChatService` is modified to actually call `create_message` rather than using its placeholder logic. Comments in the test file reflect this.)**
        *   Asserted that `mock_sio_emit` was called once with the correct event name (`'new_message'`), message payload, and `room` argument.
    *   **Test Case 2: `test_send_direct_message_saves_and_emits` (async def)**
        *   Similar setup to the first test case.
        *   Adjusted the `return_value` of `mock_chat_repository_instance.create_message` for this specific test if needed.
        *   Called `await chat_service.send_direct_message(...)` with sample data.
        *   Asserted `MockedChatRepository` instantiation.
        *   Asserted `mock_chat_repository_instance.create_message` was called once with expected direct message data. **(Same assumption about `ChatService` logic as above.)**
        *   Asserted `mock_sio_emit` was called once with the correct event name (`'new_dm'`), message payload, and `room` argument (targeting the receiver's user ID room).

**Important Considerations noted in the test file comments:**
*   The tests are written to verify the *intended* behavior of `ChatService`, which includes persisting messages via `ChatRepository.create_message`.
*   The current `ChatService` implementation (from previous subtasks) has placeholder logic for message creation that does *not* call the repository. For these tests to pass against the actual database interaction, `ChatService`'s `send_room_message` and `send_direct_message` methods would need to be updated to:
    1.  Call `self.chat_repository.create_message(message_data)`.
    2.  Since `chat_repository.create_message` is synchronous and `ChatService` methods are asynchronous, this call should be wrapped: `await asyncio.to_thread(self.chat_repository.create_message, message_data)`.
*   The test file provides the structure and assertions for this intended, fully functional behavior.

The tests are set up using `pytest` conventions and appropriate mocking for external dependencies (`ChatRepository` and `sio.emit`).
