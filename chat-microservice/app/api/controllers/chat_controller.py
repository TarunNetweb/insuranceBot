import asyncio # Not directly used here now, but kept if future direct async ops are added
from app.services.chat_service import sio, ChatService
from app.database.session import SessionLocal

# Module-level note on security:
# The `sender_id` in message handlers currently comes from client data.
# In a production system, `sender_id` MUST be derived from an authenticated session/token
# associated with the `sid` on the server-side to prevent impersonation. For example:
# @sio.event
# async def connect(sid, environ, auth):
#     user = await authenticate_user_from_auth(auth) # Custom auth logic
#     if user:
#         sio.save_session(sid, {'user_id': user.id, 'username': user.username})
#     else:
#         return False # Connection rejected
#
# In message handlers:
# session = await sio.get_session(sid)
# sender_id = session['user_id']


def get_chat_service_with_session():
    """
    Provides a ChatService instance with a new database session.

    This utility function encapsulates the creation of a database session
    and its provision to the ChatService. It's designed to be used by
    each Socket.IO event handler to ensure that every event is processed
    with a fresh session that is closed afterwards.

    Returns:
        tuple: (ChatService instance, database Session instance)
    """
    db_session = SessionLocal()
    chat_service = ChatService(db_session=db_session)
    return chat_service, db_session

# Socket.IO Event Handlers

@sio.event
async def connect(sid: str, environ: dict, auth: dict | None = None):
    """
    Handles new client connections.
    Delegates to ChatService.handle_connect and emits a welcome message.

    Args:
        sid: The session ID of the connecting client.
        environ: The WSGI environment dictionary.
        auth: Optional authentication data from the client.
    """
    chat_service, db_session = get_chat_service_with_session()
    try:
        await chat_service.handle_connect(sid, environ, auth)
        await sio.emit('system_message', {'message': 'Welcome to the chat! You are connected.'}, room=sid)
    except Exception as e:
        # In a production app, use proper logging instead of print
        print(f"Error during connect for SID {sid}: {e}")
        # Consider emitting an error to the client if appropriate for connect failures
    finally:
        db_session.close()

@sio.event
async def disconnect(sid: str):
    """
    Handles client disconnections.
    Delegates to ChatService.handle_disconnect.

    Args:
        sid: The session ID of the disconnecting client.
    """
    chat_service, db_session = get_chat_service_with_session()
    try:
        await chat_service.handle_disconnect(sid)
    except Exception as e:
        print(f"Error during disconnect for SID {sid}: {e}") # Replace with logging
    finally:
        db_session.close()

@sio.on('join_room')
async def on_join_room(sid: str, data: dict):
    """
    Handles a client's request to join a room.
    Expected data: {'room_id': str}
    Delegates to ChatService.join_room.

    Args:
        sid: The session ID of the client.
        data: Dictionary containing event data, must include 'room_id'.
    """
    chat_service, db_session = get_chat_service_with_session()
    try:
        room_id = data.get('room_id')
        if not room_id:
            await sio.emit('error_message', {'error': 'room_id missing in join_room request'}, room=sid)
            return

        await chat_service.join_room(sid, room_id)
        await sio.emit('system_message', {'message': f'You have joined room: {room_id}'}, room=sid)
    except Exception as e:
        print(f"Error during join_room for SID {sid}: {e}") # Replace with logging
        await sio.emit('error_message', {'error': f'Could not join room: {str(e)}'}, room=sid)
    finally:
        db_session.close()

@sio.on('leave_room')
async def on_leave_room(sid: str, data: dict):
    """
    Handles a client's request to leave a room.
    Expected data: {'room_id': str}
    Delegates to ChatService.leave_room.

    Args:
        sid: The session ID of the client.
        data: Dictionary containing event data, must include 'room_id'.
    """
    chat_service, db_session = get_chat_service_with_session()
    try:
        room_id = data.get('room_id')
        if not room_id:
            await sio.emit('error_message', {'error': 'room_id missing in leave_room request'}, room=sid)
            return

        await chat_service.leave_room(sid, room_id)
        await sio.emit('system_message', {'message': f'You have left room: {room_id}'}, room=sid)
    except Exception as e:
        print(f"Error during leave_room for SID {sid}: {e}") # Replace with logging
        await sio.emit('error_message', {'error': f'Could not leave room: {str(e)}'}, room=sid)
    finally:
        db_session.close()

@sio.on('send_room_message')
async def on_send_room_message(sid: str, data: dict):
    """
    Handles a client's request to send a message to a room.
    Expected data: {'room_id': str, 'message_content': str, 'sender_id': int}
    (Note: 'sender_id' should ideally be derived server-side from session/auth).
    Delegates to ChatService.send_room_message.

    Args:
        sid: The session ID of the client.
        data: Dictionary containing message data.
    """
    chat_service, db_session = get_chat_service_with_session()
    try:
        room_id = data.get('room_id')
        message_content = data.get('message_content')
        sender_id = data.get('sender_id') # Vulnerable: sender_id should be from auth session

        if not all([room_id, message_content, sender_id is not None]): # sender_id can be 0
            await sio.emit('error_message', {'error': 'Missing fields in send_room_message (room_id, message_content, sender_id)'}, room=sid)
            return

        await chat_service.send_room_message(sid, room_id, message_content, sender_id)
        await sio.emit('system_message', {'message': 'Message sent successfully to room.'}, room=sid)
    except Exception as e:
        print(f"Error during send_room_message for SID {sid}: {e}") # Replace with logging
        await sio.emit('error_message', {'error': f'Could not send message: {str(e)}'}, room=sid)
    finally:
        db_session.close()

@sio.on('send_direct_message')
async def on_send_direct_message(sid: str, data: dict):
    """
    Handles a client's request to send a direct message to another user.
    Expected data: {'receiver_id': str, 'message_content': str, 'sender_id': int}
    (Note: 'sender_id' should ideally be derived server-side from session/auth).
    Delegates to ChatService.send_direct_message.

    Args:
        sid: The session ID of the client.
        data: Dictionary containing message data.
    """
    chat_service, db_session = get_chat_service_with_session()
    try:
        receiver_id = data.get('receiver_id') # Should be receiver's user_id
        message_content = data.get('message_content')
        sender_id = data.get('sender_id') # Vulnerable: sender_id should be from auth session

        if not all([receiver_id, message_content, sender_id is not None]):
            await sio.emit('error_message', {'error': 'Missing fields in send_direct_message (receiver_id, message_content, sender_id)'}, room=sid)
            return

        await chat_service.send_direct_message(sid, str(receiver_id), message_content, sender_id)
        await sio.emit('system_message', {'message': 'Direct message sent successfully.'}, room=sid)
    except Exception as e:
        print(f"Error during send_direct_message for SID {sid}: {e}") # Replace with logging
        await sio.emit('error_message', {'error': f'Could not send direct message: {str(e)}'}, room=sid)
    finally:
        db_session.close()

# The Socket.IO event handlers are registered above using @sio.event and @sio.on.
# These handlers are responsible for:
# 1. Receiving events from clients.
# 2. Validating incoming data (basic validation shown).
# 3. Obtaining a ChatService instance with a dedicated database session.
# 4. Calling the appropriate ChatService method to handle the core logic.
# 5. Sending responses or acknowledgments back to the client(s) via Socket.IO.
# 6. Ensuring the database session is closed after processing the event.
#
# This controller acts as the primary interface for Socket.IO events, delegating
# business logic to the ChatService and managing DB session lifecycle per event.
# For a production application, consider replacing print statements with a robust logging setup.
