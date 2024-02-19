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
