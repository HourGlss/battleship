import secrets
import string

from flask import request
from flask_socketio import join_room, send, leave_room, emit

from .extensions import socketio

rooms = []
def generate_room_id(length=8):
    # Generate a secure random string of specified length
    alphabet = string.ascii_letters + string.digits
    room_id = ''.join(secrets.choice(alphabet) for i in range(length))
    return room_id


@socketio.on("connect")
def handle_connect():
    print("Client Connected")
    socketio.emit("response", {"from": "server"})

@socketio.on("message")
def handle_message(data):
    print("Message from client: ", data)
    socketio.emit("response", {"from": "server"})

@socketio.event
def chat(data):
    print("Chat from client: ", data)
    socketio.emit("response", {"from": "server"})

@socketio.event
def set_open_to_play(data):
    connections = [connection.sid for connection in socketio.server.environ.values()]

    socketio.emit("response", {"from": "server"})

@socketio.event
def poll_connections():
    connections = [connection for connection in socketio.server.environ.values()]
    print(len(connections))
    socketio.emit("response", {"connections": len(connections)})

@socketio.on('join')
def on_join(data):
    username = data['username']
    connections = [connection for connection in socketio.server.environ.values()]
    for i in range(len(connections)):
        data = {}
        data["sid"] = generate_room_id()
        join_room(data["sid"])
        rooms.append(data['sid'])
        socketio.emit("join_confirm", {"sid": data["sid"]})
        socketio.emit("room_creation", data)
    print(rooms)



@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)