from flask import Flask

from src.events import socketio
from src.routes import main


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'secret!'
    app.register_blueprint(main)

    socketio.init_app(app, logger=True, ping_interval=1, ping_timeout=2)

    return app
