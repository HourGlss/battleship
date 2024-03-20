import secrets
import string
import socketio
import base64
import threading

import asyncio
import aioconsole

from src.pocs.crypto_example_2 import SecurePlayer
from src.shared_state import test_ship_dict

ships = test_ship_dict


async def monitor_keyboard(client):
    while True:
        input_str = await aioconsole.ainput("Enter command (q to quit, p to play, h to set ships, m to make move): ")
        if input_str == 'q':
            client.stop()
            break
        elif input_str == 'p':
            tag, nonce, ciphertext = client.secure_player.send_data("Open to play")
            client.sio.emit("open_to_play", {"username": client.name,
                                             "payload": {"tag": tag, "nonce": nonce, "ciphertext": ciphertext}})
        elif input_str == 'h':
            for port in client.rooms.keys():
                client.rooms[port]["client"].game_client.emit("set_ships",
                                                              {"username": client.name, "ships": test_ship_dict})
        elif input_str == 'm':
            # Prompt the user to enter x and y coordinates
            x = await aioconsole.ainput("Enter x coordinate (0-9): ")
            y = await aioconsole.ainput("Enter y coordinate (0-9): ")

            try:
                # Convert x and y to integers and validate the input
                x = int(x)
                y = int(y)
                if not (0 <= x <= 9) or not (0 <= y <= 9):
                    print("Coordinates must be between 0 and 9.")
                    continue
            except ValueError:
                # Handle case where x or y is not an integer
                print("Coordinates must be integers.")
                continue

            # Emit the make_move event with the user-provided coordinates
            for port in client.rooms.keys():
                client.rooms[port]["client"].game_client.emit("make_move", {"username": client.name, "x": x, "y": y})
        await asyncio.sleep(1)  # Sleep to yield control back to the event loop



def generate_name():
    # Generate a secure random string of specified length
    alphabet = string.ascii_letters + string.digits
    name = ''.join(secrets.choice(alphabet) for i in range(8))
    return name


class GameClientThread:
    def __init__(self, port, username, on_disconnect_callback):
        self.port = port
        self.username = username
        self.on_disconnect_callback = on_disconnect_callback  # Store the callback
        self.game_client = socketio.Client()
        try:
            self.game_client.connect(f"http://45.79.223.73:{self.port}")
            self.game_client.emit("join", {"username": self.username})
            self.game_client.emit("ping")
            self.register_handlers()
        except Exception as e:
            print(f"Connection failed: {e}")

    def register_handlers(self):
        # It's safer to define event handlers here and attach them to the client
        def on_response(data):
            print("Response from server:", data)

        def on_game_over(data):
            print("Game over:", data)
            self.stop()

        def on_move_prompt(data):
            print(data)

        def on_print_board(data):
            print(str(data["message"]))

        self.game_client.on('response', on_response)
        self.game_client.on('game_over', on_game_over)
        self.game_client.on('move_prompt', on_move_prompt)

    def start_thread(self):
        self.thread = threading.Thread(target=self.game_client.wait)
        self.thread.start()

    def stop(self):
        self.game_client.disconnect()
        if self.thread.is_alive():
            self.thread.join()
        self.on_disconnect_callback(self.port)


class Client:
    def __init__(self, uri):
        # Initialize a socketio.Client instance here instead of using the socketio module directly
        self.sio = socketio.Client()
        self.uri = uri
        self.rooms = {}
        self.register_handlers()
        self.name = generate_name()
        self.secure_player = SecurePlayer("password", self.name)

    def register_handlers(self):
        # Define event handlers using the instance's `on` method
        @self.sio.on('ping')
        def ping(data):
            print("Ping received")

        @self.sio.on('get_port')
        def get_port(data):
            print("Getting port:", data)
            try:
                port = data['port']
                if port not in self.rooms:
                    game_client = GameClientThread(port, self.name,
                                                   self.handle_game_client_disconnect)
                    self.rooms[port] = {"client": game_client}
                    game_client.start_thread()
                    print("Connected to port", port)
            except Exception as e:
                print(f"Error getting port: {e}")
            except KeyError:
                print("Port not found")

        @self.sio.on('response')
        def response(data):
            print("Response from server:", data)

        @self.sio.on('heartbeat')
        def heartbeat():
            print("Heartbeat received")
            # Respond to the heartbeat directly using the client instance
            message = self.secure_player.send_data("Heartbeat acknowledged")
            self.sio.emit("heartbeat_response", {"username": self.name, "payload": message})

        @self.sio.on('initial send')
        def initial_send(data):
            print("Initial send received")
            from_server = (data["enc_session_key"], data["cipher_aes.nonce"], data["tag"], data["ciphertext"])
            self.secure_player.initial_receive(from_server)

    def handle_game_client_disconnect(self, port):
        # Remove the disconnected game client from the rooms dictionary
        if port in self.rooms:
            del self.rooms[port]
            print(f"Game client disconnected and removed from room: {port}")

    def start(self):
        # Connect using the client instance to the specified URI
        print(self.secure_player.pub_rsa)
        self.sio.connect(self.uri, headers={"username": self.name},
                         auth={"rec_key": base64.urlsafe_b64encode(self.secure_player.pub_rsa).decode("utf-8")})
        print("Client started and connected to", self.uri)
        self.sio.emit("initial send", {"username": self.name})
        # client.sio.emit("register", {"username": self.name, "payload": self.secure_player.send_data("Registering")})

    def stop(self):
        # Disconnect using the client instance
        self.sio.disconnect()
        print("Client disconnected")

async def main():
    client = Client('http://45.79.223.73:5555')
    client.start()

    await monitor_keyboard(client)


if __name__ == "__main__":
    asyncio.run(main())
