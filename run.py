from src.Battleship import create_app, socketio

app = create_app()

socketio.run(app, allow_unsafe_werkzeug=True, port=5555)

