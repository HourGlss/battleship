import secrets
import string


class Room:
    def __init__(self, name, capacity: int):
        self.name = name
        self.capacity = capacity
        self.users = []
        # make a room id with a random string
        self.id = generate_room_id(8)

    def add_user(self, user):
        if len(self.users) < self.capacity:
            self.users.append(user)
            return True
        return False

    def remove_user(self, user):
        self.users.remove(user)

    def get_users(self):
        return self.users

    def get_name(self):
        return self.name

    def get_capacity(self):
        return self.capacity

    def set_ships(self, user, ships):
        for u in self.users:
            if u.name == user.name:
                u.set_ships(ships)


def generate_room_id(length=8):
    # Generate a secure random string of specified length
    alphabet = string.ascii_letters + string.digits
    room_id = ''.join(secrets.choice(alphabet) for i in range(length))
    return room_id
