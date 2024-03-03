from socketio import Client
from flask_socketio import SocketIO


class CustomClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_name = None  # You can add additional properties here


socketio = SocketIO(client_class=CustomClient)
