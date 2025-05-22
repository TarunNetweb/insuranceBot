import asyncio
from app.services.chat_service import sio, ChatService, socket_app # socket_app might be needed if main mounts it
from app.database.session import SessionLocal
from app.models.chat_model import ChatMessage # For type hinting if needed, not strictly for controller

# 3. Implement Database Session Management Utility
def get_chat_service_with_session():
    """
    Creates a DB session and a ChatService instance.
    Returns:
        tuple: (ChatService instance, DB session instance)
    """
    db_session = SessionLocal()
    chat_service = ChatService(db_session=db_session)
    return chat_service, db_session

print("chat_controller.py: Imports and get_chat_service_with_session utility defined.")

# 4. Define and Register Socket.IO Event Handlers

@sio.event
async def connect(sid, environ, auth=None):
    print(f"Controller: Client connecting - SID: {sid}, Auth: {auth}")
    chat_service, db_session = get_chat_service_with_session()
    try:
        # ChatService.handle_connect is async
        await chat_service.handle_connect(sid, environ, auth)
        # Example: Send a welcome message or connection confirmation
        await sio.emit('system_message', {'message': 'Welcome to the chat! You are connected.'}, room=sid)
        print(f"Controller: Client {sid} connected successfully.")
    except Exception as e:
        print(f"Controller: Error during connect for SID {sid}: {e}")
        # Optionally, emit an error message back if appropriate, though connect often doesn't have a client expecting a response to failure
    finally:
        db_session.close()
        print(f"Controller: DB session closed for connect SID {sid}.")

@sio.event
async def disconnect(sid):
    print(f"Controller: Client disconnecting - SID: {sid}")
    chat_service, db_session = get_chat_service_with_session()
    try:
        # ChatService.handle_disconnect is async
        await chat_service.handle_disconnect(sid)
        print(f"Controller: Client {sid} disconnected successfully.")
    except Exception as e:
        print(f"Controller: Error during disconnect for SID {sid}: {e}")
    finally:
        db_session.close()
        print(f"Controller: DB session closed for disconnect SID {sid}.")

@sio.on('join_room')
async def on_join_room(sid, data):
    print(f"Controller: SID {sid} attempting to join room. Data: {data}")
    chat_service, db_session = get_chat_service_with_session()
    try:
        if not data or 'room_id' not in data:
            await sio.emit('error_message', {'error': 'room_id missing in join_room request'}, room=sid)
            print(f"Controller: Missing room_id for SID {sid} in join_room.")
            return

        room_id = data['room_id']
        # ChatService.join_room is async
        await chat_service.join_room(sid, room_id)
        await sio.emit('system_message', {'message': f'You have joined room: {room_id}'}, room=sid)
        # Optionally notify others in the room (ChatService could also do this)
        # await sio.emit('system_message', {'message': f'User {sid} has joined the room.'}, room=room_id, skip_sid=sid)
        print(f"Controller: SID {sid} successfully joined room {room_id}.")
    except Exception as e:
        print(f"Controller: Error during join_room for SID {sid}, room {data.get('room_id')}: {e}")
        await sio.emit('error_message', {'error': f'Could not join room: {e}'}, room=sid)
    finally:
        db_session.close()
        print(f"Controller: DB session closed for join_room SID {sid}.")

@sio.on('leave_room')
async def on_leave_room(sid, data):
    print(f"Controller: SID {sid} attempting to leave room. Data: {data}")
    chat_service, db_session = get_chat_service_with_session()
    try:
        if not data or 'room_id' not in data:
            await sio.emit('error_message', {'error': 'room_id missing in leave_room request'}, room=sid)
            print(f"Controller: Missing room_id for SID {sid} in leave_room.")
            return

        room_id = data['room_id']
        # ChatService.leave_room is async
        await chat_service.leave_room(sid, room_id)
        await sio.emit('system_message', {'message': f'You have left room: {room_id}'}, room=sid)
        # Optionally notify others (ChatService could also do this)
        # await sio.emit('system_message', {'message': f'User {sid} has left the room.'}, room=room_id, skip_sid=sid)
        print(f"Controller: SID {sid} successfully left room {room_id}.")
    except Exception as e:
        print(f"Controller: Error during leave_room for SID {sid}, room {data.get('room_id')}: {e}")
        await sio.emit('error_message', {'error': f'Could not leave room: {e}'}, room=sid)
    finally:
        db_session.close()
        print(f"Controller: DB session closed for leave_room SID {sid}.")

@sio.on('send_room_message') # Changed from 'on_send_message' to match service example
async def on_send_room_message(sid, data):
    print(f"Controller: SID {sid} attempting to send room message. Data: {data}")
    chat_service, db_session = get_chat_service_with_session()
    try:
        required_fields = ['room_id', 'message_content', 'sender_id']
        if not data or not all(field in data for field in required_fields):
            await sio.emit('error_message', {'error': 'Missing fields in send_room_message request (room_id, message_content, sender_id)'}, room=sid)
            print(f"Controller: Missing fields for SID {sid} in send_room_message.")
            return

        room_id = data['room_id']
        message_content = data['message_content']
        sender_id = data['sender_id'] # As noted, sender_id from client is a risk.

        # ChatService.send_room_message is async.
        # The internal DB call within ChatService.send_room_message is currently a placeholder.
        # If it were a real sync DB call, ChatService would need to use asyncio.to_thread for it.
        await chat_service.send_room_message(sid, room_id, message_content, sender_id)
        
        await sio.emit('system_message', {'message': 'Message sent successfully to room.'}, room=sid)
        print(f"Controller: SID {sid} successfully sent message to room {room_id}.")
    except Exception as e:
        print(f"Controller: Error during send_room_message for SID {sid}: {e}")
        await sio.emit('error_message', {'error': f'Could not send message: {e}'}, room=sid)
    finally:
        db_session.close()
        print(f"Controller: DB session closed for send_room_message SID {sid}.")

@sio.on('send_direct_message')
async def on_send_direct_message(sid, data):
    print(f"Controller: SID {sid} attempting to send direct message. Data: {data}")
    chat_service, db_session = get_chat_service_with_session()
    try:
        required_fields = ['receiver_id', 'message_content', 'sender_id'] # receiver_id (user_id)
        if not data or not all(field in data for field in required_fields):
            await sio.emit('error_message', {'error': 'Missing fields in send_direct_message request (receiver_id, message_content, sender_id)'}, room=sid)
            print(f"Controller: Missing fields for SID {sid} in send_direct_message.")
            return

        receiver_id = str(data['receiver_id']) # Ensure string for room name if emitting to user_id room
        message_content = data['message_content']
        sender_id = data['sender_id'] # As noted, sender_id from client is a risk.

        # ChatService.send_direct_message is async.
        # Similar to send_room_message, internal DB call placeholder.
        await chat_service.send_direct_message(sid, receiver_id, message_content, sender_id)
        
        await sio.emit('system_message', {'message': 'Direct message sent successfully.'}, room=sid)
        print(f"Controller: SID {sid} successfully sent direct message to user {receiver_id}.")
    except Exception as e:
        print(f"Controller: Error during send_direct_message for SID {sid}: {e}")
        await sio.emit('error_message', {'error': f'Could not send direct message: {e}'}, room=sid)
    finally:
        db_session.close()
        print(f"Controller: DB session closed for send_direct_message SID {sid}.")

print("chat_controller.py: Socket.IO event handlers defined and registered.")

# To make this runnable with FastAPI, you would typically mount the socket_app:
# from fastapi import FastAPI
# app = FastAPI()
# app.mount("/ws", socket_app) # Mounts the Socket.IO app at /ws path
# And then run with Uvicorn: uvicorn main:app --reload
# The chat_controller.py itself doesn't run, but its sio object is configured by these decorators.
# Ensure this file is imported in __init__.py so handlers are registered when app loads.
# The ChatService's current implementation uses placeholder message creation.
# For real DB operations, ChatService's send_..._message methods would need to use
# `await asyncio.to_thread(self.chat_repository.create_message, ...)`
# if chat_repository.create_message remains synchronous.
# The controller correctly `await`s the async ChatService methods.
# The session management (open/close per event) is basic; connection pooling and more
# sophisticated session management might be needed for high load.
# The `sender_id` being passed from the client is a temporary measure for this exercise.
# In a production system, `sender_id` MUST be derived from the authenticated session/token
# associated with the `sid` on the server-side to prevent impersonation.
# For example, in the `connect` handler, after successful authentication:
# `sio.save_session(sid, {'user_id': authenticated_user_id})`
# And then in message handlers:
# `session = await sio.get_session(sid)`
# `sender_id = session['user_id']`
# This is a more secure approach.
# The `auth` object in `connect` is a placeholder for this mechanism.I have completed steps 1-4 for the `chat_controller.py` file.

1.  **Created `chat_controller.py`**: Done in a previous turn.
2.  **Imported Necessary Components**: `sio`, `ChatService` from `app.services.chat_service`, and `SessionLocal` from `app.database.session` are imported. `asyncio` is also imported.
3.  **Implemented Database Session Management Utility**: `get_chat_service_with_session()` function is defined, which creates and returns a `ChatService` instance and a database session.
4.  **Defined and Registered Socket.IO Event Handlers**:
    *   `connect(sid, environ, auth=None)`: Calls `chat_service.handle_connect`, emits a welcome message.
    *   `disconnect(sid)`: Calls `chat_service.handle_disconnect`.
    *   `on_join_room(sid, data)`: Expects `data={'room_id': str}`, calls `chat_service.join_room`, emits a system message.
    *   `on_leave_room(sid, data)`: Expects `data={'room_id': str}`, calls `chat_service.leave_room`, emits a system message.
    *   `on_send_room_message(sid, data)` (renamed from `on_send_message` for clarity): Expects `data={'room_id': str, 'message_content': str, 'sender_id': int}`, calls `chat_service.send_room_message`, emits an acknowledgment.
    *   `on_send_direct_message(sid, data)`: Expects `data={'receiver_id': int, 'message_content': str, 'sender_id': int}`, calls `chat_service.send_direct_message`, emits an acknowledgment.
    *   Each handler uses `get_chat_service_with_session()` and closes the session in a `finally` block.
    *   Basic logging and error emitting are included.
    *   Important notes about `sender_id` security and the need for `ChatService` to internally handle sync DB calls with `asyncio.to_thread` are present in the comments.

Now I will proceed with step 5: Update `chat-microservice/app/api/controllers/__init__.py`.
I'll first check if the file exists and its current content.
