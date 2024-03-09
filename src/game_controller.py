from flask import Flask, request
from flask_socketio import SocketIO
from threading import Thread, Lock
from src.battleship import Battleship, Player


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
        self.player_turn = 0

        # Register event handlers
        self.register_socket_events()

    def register_socket_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected from server at port ', self.port)
            if request.sid in self.players.keys():
                del self.players[request.sid]

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

        @self.socketio.on('set_ships')
        def set_ships(data):
            player = self.find_player_by_sid(request.sid)
            self.players[player]["ships"] = data["ships"]
            self.players[player]["ships_set"] = True

            if self.all_ships_set():
                player1 = Player()
                self.players["player1"]["playerstate"] = player1
                player2 = Player()
                self.players["player2"]["playerstate"] = player2
                self.battleship.add_players(self.players["player1"]["playerstate"],
                                            self.players["player2"]["playerstate"])
                if self.battleship.validate_and_place_ships():
                    self.socketio.emit("response", {'message': 'Ships have been placed'})
                else:
                    self.socketio.emit("response", {'message': 'Invalid ship placement'})
                    self.players["player1"]["ships_set"] = False
                    self.players["player2"]["ships_set"] = False

        @self.socketio.on("make_move")
        def make_move(data):
            player = self.find_player_by_sid(request.sid)
            if (self.player_turn == 0 and player == "player1") or (self.player_turn == 1 and player == "player2"):
                self.battleship.make_move(data["p"], data["x"], data["y"])
                p1, p2 = self.battleship.check_game_over()
                if p1 == False or p2 == False:
                    self.socketio.emit("response", {"message": "Game over you won"}, room=request.sid)
            else:
                self.socketio.emit("response", {"message": "Not your turn to move"}, room=request.sid)

    def start(self):
        self.socketio.run(self.app, host='0.0.0.0', port=self.port, use_reloader=False)

    def add_player(self, player, sid):
        with self.lock:
            player = {"username": player, "ships_set": False, "sid": sid}
            if len(self.players) == 0:
                self.players["player1"] = player
            else:
                self.players["player2"] = player

    def ping_players(self):
        with self.lock:
            for key, value in self.players.items():
                self.socketio.emit("ping", {"from": "server"}, room=key)

    def get_port(self):
        with self.lock:
            for key, value in self.players.items():
                self.socketio.emit("get_port", {"port": self.port}, to=key)

    def all_ships_set(self):
        with self.lock:
            for player in self.players.values():
                if not player["ships_set"]:
                    return False
            return True

    def find_player_by_sid(self, sid):
        with self.lock:
            for player, info in self.players.items():
                if info['sid'] == sid:
                    return player
            return None