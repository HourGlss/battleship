import keyboard as keyboard
import socketio

if __name__ == "__main__":
    rooms = []
    sio = socketio.Client()
    sio.connect('http://localhost:5555/game')
    print("Connected to server")

    print("Sending message to server")
    sio.emit("join", {"username": "player1"})


    @sio.on('response')
    def response(data):
        print(data)  # {'from': 'server'}

    @sio.on('join_confirm')
    def join_confirm(data):
        if data['sid'] not in rooms:
            rooms.append(data['sid'])
            print("join confirmed")


    @sio.on('room_creation')
    def room_creation(data):
        if data['sid'] not in rooms:
            sio.emit('join', {"username": "player1", "sid": data["sid"]})

    while True:
        # if shift + enter is pressed exit the program
        if keyboard.is_pressed('shift + enter'):
            sio.disconnect()
            exit(0)


