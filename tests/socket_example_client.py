import socketio
import time

def main():
    with socketio.SimpleClient() as sio:
        sio.connect('http://localhost:5000')
        while True:
            time.sleep(1)
            sio.call(event="receive",data="test test")
            result=sio.receive()
            print(result)


if __name__ == '__main__':
    main()