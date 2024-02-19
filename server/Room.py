class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.users = []

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