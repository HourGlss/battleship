import secrets
import string
import datetime
from battleship import BattleShip, Player


class Room:
    def __init__(self):
        self.name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.capacity = 2
        self.users = []
        # make a room id with a random string
        self.id = generate_room_id(8)
        self.battleship = BattleShip()

    def add_user(self, user):
        if len(self.users) < self.capacity:
            self.users.append(user)
            return True
        if len(self.users) == self.capacity:
            self.battleship.add_players(self.users[0], self.users[1])
            self.battleship.validate_and_place_ships()
        return False

    def remove_user(self, user):
        self.users.remove(user)

    def get_users(self):
        return self.users


    def get_name(self):
        return self.name

    def set_ships(self, user, ships):
        for u in self.users:
            if u.name == user.name:
                u.ships = ships
        self.verify_ships()


    def verify_ships(self):
        if self.users[0].ships and self.users[1].ships:
            player1 = Player(self.users[0])
            player2 = Player(self.users[1])
            player1.set_ships(self.users[0].ships)
            player2.set_ships(self.users[1].ships)
            print(player1.ships)
            print(player2.ships)
            self.battleship.add_players(player1, player2)
            self.battleship.validate_and_place_ships()

    def has_players(self, player1, player2):
        return player1 in self.users and player2 in self.users


def generate_room_id(length=8):
    # Generate a secure random string of specified length
    alphabet = string.ascii_letters + string.digits
    room_id = ''.join(secrets.choice(alphabet) for i in range(length))
    return room_id
