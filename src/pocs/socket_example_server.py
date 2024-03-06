from flask import Flask
import flask_socketio as fs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SeRvEr SeCrEt'
socketio = fs.SocketIO(app)


@socketio.on('receive')
def handle_message(data):
    fs.send("recieved" + data)


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
