from flask_socketio import SocketIO
from src.pocs.crypto_example_2 import SecureServer

socketio = SocketIO()

secure_server = SecureServer("password")

