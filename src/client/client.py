import secrets
import string
import time
import keyboard
import socketio


def generate_name():
    # Generate a secure random string of specified length
    alphabet = string.ascii_letters + string.digits
    name = ''.join(secrets.choice(alphabet) for i in range(8))
    return name


class Client:
    def __init__(self, uri):
        # Initialize a socketio.Client instance here instead of using the socketio module directly
        self.sio = socketio.Client()
        self.uri = uri
        self.rooms = {}
        self.register_handlers()
        self.name = generate_name()

    def register_handlers(self):
        # Define event handlers using the instance's `on` method
        @self.sio.on('ping')
        def ping(data):
            print("Ping received")

        @self.sio.on('get_port')
        def get_port(data):
            print("Getting port:", data)
            port = data['port']
            if port not in self.rooms:
                # Initialize a new socketio.Client for the game room
                game_client = socketio.Client()
                game_client.connect(f"http://45.79.223.73:{port}")
                game_client.emit(f"join", {"username": self.name})
                game_client.emit("ping")
                self.rooms[port] = {"client": game_client}
                print("Connected to port", port)

        @self.sio.on('response')
        def response(data):
            print("Response from server:", data)

        @self.sio.on('heartbeat')
        def heartbeat(data):
            print("Heartbeat received")
            # Respond to the heartbeat directly using the client instance
            self.sio.emit("heartbeat_response", {'data': 'Heartbeat acknowledged'})

    def start(self):
        # Connect using the client instance to the specified URI
        self.sio.connect(self.uri)
        print("Client started and connected to", self.uri)
        client.sio.emit("register", {"username": self.name})

    def stop(self):
        # Disconnect using the client instance
        self.sio.disconnect()
        print("Client disconnected")


if __name__ == "__main__":
    client = Client('http://45.79.223.73:5555')
    client.start()

    while True:
        if keyboard.is_pressed('q'):
            client.stop()
            break
        if keyboard.is_pressed('p'):
            client.sio.emit("open_to_play")
        time.sleep(1)
