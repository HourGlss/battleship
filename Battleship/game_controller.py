from flask import Flask, request
from flask_socketio import SocketIO
from threading import Thread, Lock
from battleship import Battleship
from .extensions import socketio

class GameController(Thread):
    def __init__(self, port, room_id):
        super(GameController, self).__init__()
        self.lock = Lock()
        self.room_id = room_id
        self.port = port
        self.players = {}
        self.battleship = Battleship()
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Register event handlers
        self.register_socket_events()

    def register_socket_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected from server at port ', self.port)

        @self.socketio.on('join')
        def handle_join(data):
            username = data['username']
            sid = request.sid  # request.sid is the session ID of the client
            self.add_player(username, sid)
            self.socketio.emit('join_ack', {'message': f'{username} has joined.'}, room=sid)

        @self.socketio.on('message')
        def handle_message(data):
            print('Received message: ', data)
            self.socketio.emit('response', {'data': 'Message received'})

    def run(self):
        self.socketio.run(self.app, host='0.0.0.0', port=self.port, use_reloader=False)

    def add_player(self, player, sid):
        with self.lock:
            player = {"username": player}
            self.players[sid] = player

    def ping_players(self):
        for key, value in self.players.items():
            self.socketio.emit("ping", {"from": "server"}, room=key)

    def get_port(self):
        for key, value in self.players.items():
            self.socketio.emit("get_port", {"port": self.port}, to=key)
