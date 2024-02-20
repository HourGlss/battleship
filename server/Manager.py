from itertools import combinations

from Room import Room


class Manager:
    def __init__(self):
        self.rooms: list[Room] = []

    def add_room(self, room):
        self.rooms.append(room)

    def remove_room(self, room):
        self.rooms.remove(room)

    def add_user_to_room(self, user, room_id):
        for room in self.rooms:
            if room.id == room_id:
                room.add_user(user)

    def remove_user_from_room(self, user, room_id):
        for room in self.rooms:
            if room.id == room_id:
                room.remove_user(user)

    def get_room(self, room_id):
        for room in self.rooms:
            if room.id == room_id:
                return room
        return None

    def create_games_for_open_players(self, registered_users):
        ret = ""
        open_players = [user for user in registered_users.values() if user.open_to_play]
        # Create a game for every pair of open players that haven't been paired yet
        for player1, player2 in combinations(open_players, 2):
            if not any(room.battleship.has_player(player1) for room in self.rooms):
                room = Room()
                self.add_room(room)
                self.add_user_to_room(player1, room.id)
                self.add_user_to_room(player2, room.id)
                ret += f"Created room with ID:{room.id} and players {player1.name} and {player2.name}\n"
                print(f"Created room {room.id} with players {player1.name} and {player2.name}")
            else:
                print(f"Room already exists for {player1.name}")
                ret += f"Room already exists for {player1.name}\n"
        return ret
