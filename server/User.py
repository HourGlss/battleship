class User:
    def __init__(self, name, number, public_key):
        self.name = name
        self.number = number
        self.public_key = public_key
        self.open_to_play = "false"

    def __str__(self):
        return f"{self.name} "

    def set_open_to_play(self, open_to_play):
        self.open_to_play = open_to_play