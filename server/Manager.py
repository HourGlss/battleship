from Room import Room


class Manager:
    def __init__(self):
        self.rooms: list[Room] = []

    def add_room(self, room):
        self.rooms.append(room)

    def remove_room(self, room):
        self.rooms.remove(room)

    def add_user_to_room(self, room, user, id):
        if room.id == id:
            room.add_user(user)

    def remove_user_from_room(self, room, user):
        room.remove_user(user)
