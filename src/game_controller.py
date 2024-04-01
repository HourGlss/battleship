from flask import Flask, request
from flask_socketio import SocketIO
from threading import Thread, Lock
from src.battleship import Battleship, Player
from src.utils import ShipRotation


class GameController(Thread):
    def __init__(self, port, room_id, remove_room_callback=None):
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
        self.remove_room_callback = remove_room_callback

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
            if len(self.players) == 0:
                self.remove_room_callback(self.room_id)

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
            player = self.find_player_by_username(data["username"])
            ships = self.convert_ship_rotation_to_enum(data["ships"])
            ships = self.convert_ship_keys_to_int(ships)
            if ships:
                self.players[player]["ships"] = ships
                self.players[player]["ships_set"] = True

            if self.all_ships_set():
                player1 = Player()
                self.players["player1"]["playerstate"] = player1
                player2 = Player()
                self.players["player2"]["playerstate"] = player2
                self.battleship.add_players(self.players["player1"]["playerstate"],
                                            self.players["player2"]["playerstate"])
                self.battleship.players[0].set_ships(self.players["player1"]["ships"])
                self.battleship.players[1].set_ships(self.players["player2"]["ships"])
                if self.battleship.validate_and_place_ships():
                    self.socketio.emit("response", {'message': 'Ships have been placed'})
                else:
                    self.socketio.emit("response", {'message': 'Invalid ship placement'})
                    self.players["player1"]["ships_set"] = False
                    self.players["player2"]["ships_set"] = False

        @self.socketio.on("make_move")
        def make_move(data):
            player = self.find_player_by_username(data["username"])
            expected_player = "player1" if self.player_turn == 0 else "player2"

            if player != expected_player:
                self.socketio.emit("response", {"message": "Not your turn to move"}, room=request.sid)
                return

            player_index = self.player_turn
            result = self.battleship.make_move(player_index, data["x"], data["y"])

            p1, p2 = self.battleship.check_game_over()

            if not p1 or not p2:
                winner, loser = ("player2", "player1") if not p1 else ("player1", "player2")
                self.socketio.emit("game_over", {"message": "Game over you won"}, room=self.players[winner]["sid"])
                self.socketio.emit("game_over", {"message": "Game over you lost"}, room=self.players[loser]["sid"])
                self.remove_room_callback(self.room_id)
            else:
                if result[0] == 2:
                    # Get the type of ship that was hit (5 = carrier, 4 = battleship, 3 = sub1, 2 = sub2, 1 = destroyer)
                    if result[1] == 5:
                        ship_type = "carrier"
                    elif result[1] == 4:
                        ship_type = "battleship"
                    elif result[1] == 3:
                        ship_type = "sub1"
                    elif result[1] == 2:
                        ship_type = "sub2"
                    else:
                        ship_type = "destroyer"
                    self.socketio.emit("response", {"message": f"You sunk their {ship_type}"}, room=request.sid)
                self.socketio.emit("print_board", {"message": "Your board \n", "board": self.battleship.print_my_board(self.player_turn)}, room=request.sid)
                self.player_turn = 1 - self.player_turn
                self.socketio.emit("print_board", {"message": "Opponents board\n", "board": self.battleship.print_opponent_board(self.player_turn)}, room=request.sid)
                self.notify_players_turn(self.player_turn)

    def start(self):
        self.socketio.run(self.app, host='0.0.0.0', port=self.port, use_reloader=False)

    def add_player(self, player, sid):
        with self.lock:
            player = {"username": player, "ships_set": False, "sid": sid, "ships": None}
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
            player1sid = self.players["player1"]["sid"]
            player2sid = self.players["player2"]["sid"]
            self.socketio.emit("get_port", {"port": self.port}, room=player1sid)
            self.socketio.emit("get_port", {"port": self.port}, room=player2sid)

    def all_ships_set(self):
        with self.lock:
            for player in self.players.values():
                if not player["ships_set"]:
                    return False
            return True

    def find_player_by_username(self, username):
        with self.lock:
            for player, info in self.players.items():
                if info['username'] == username:
                    return player
            return None

    def convert_ship_rotation_to_enum(self, ships):
        """
        Convert the rotation of each ship in the provided dictionary from a numeric
        value to the corresponding enum value.

        :param ships: A dictionary of ships, where each key is a ship type and each value
                      is a list of dictionaries containing 'x', 'y', and 'rotation'.
        :return: The same ships dictionary, but with 'rotation' converted to enum values.
        """
        for ship_type, ship_list in ships.items():
            for ship in ship_list:
                if ship["rotation"] == 3:
                    ship["rotation"] = ShipRotation.UP
                if ship["rotation"] == 2:
                    ship["rotation"] = ShipRotation.DOWN
                if ship["rotation"] == 1:
                    ship["rotation"] = ShipRotation.LEFT
                if ship["rotation"] == 0:
                    ship["rotation"] = ShipRotation.RIGHT
        return ships

    def convert_ship_keys_to_int(self, ships):
        """
        Convert the keys of the ships dictionary from strings to integers.

        :param ships: A dictionary of ships, where each key is a ship type and each value
                      is a list of dictionaries containing 'x', 'y', and 'rotation'.
        :return: The same ships dictionary, but with keys converted to integers.
        """
        return {int(k): v for k, v in ships.items()}

    def notify_players_turn(self, current_player):
        if current_player == 0:
            current_player_sid = self.players["player1"]["sid"]
            waiting_player_sid = self.players["player2"]["sid"]
        else:
            current_player_sid = self.players["player2"]["sid"]
            waiting_player_sid = self.players["player1"]["sid"]

        self.socketio.emit("move_prompt",{"message": "your turn to move"}, room=current_player_sid)
        self.socketio.emit("response", {"message": "Opponent's turn to move"}, room=waiting_player_sid)
