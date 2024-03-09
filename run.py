from src import create_app, socketio


def main():
    app = create_app()

    socketio.run(app,ipaddress="0.0.0.0", allow_unsafe_werkzeug=True, port=5555)


if __name__ == "__main__":
    main()
