import logging
import inspect
from src import create_app, socketio

FORMAT = "[{%(levelname)s} %(filename)s:%(lineno)s     - %(funcName)20s() ] %(message)s"
logging.basicConfig(filename='runlog.log', level=logging.DEBUG, format=FORMAT)


def main():
    func = inspect.currentframe().f_back.f_code
    app = create_app()

    socketio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True, port=5555)


if __name__ == "__main__":
    main()
