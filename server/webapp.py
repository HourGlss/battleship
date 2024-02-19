from flask import Flask, request, jsonify
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import json
from User import User

app = Flask(__name__)

# A dictionary to store registered users' data (in memory, not persistent)
registered_users: dict[str, User] = {}


def gen_pub_priv():
    private_key = RSA.generate(2048, get_random_bytes)
    public_key = private_key.publickey()
    return private_key, public_key


def add_user_to_register(username: str, number, pub):
    user = User(username, number, pub)
    registered_users[username.lower()] = user


def remove_user_from_register(username: str):
    registered_users.pop(username.lower())


@app.route('/register', methods=['POST', 'GET'])
def register():
    data = {}
    try:
        if request.method == 'GET':
            data = request.args
            for k, v in data.items():
                print(f"{k}: {v}")
        else:
            data = request.json
            for k, v in data.items():
                print(f"{k}: {v}")

    except:
        print("triple fail")

    if 'username' not in data.keys() or 'number' not in data.keys():
        return jsonify({'error': 'Missing username or number parameter'}), 400

    username = data['username']
    number = int(data['number'])

    # Checking if the number is within the specified range
    if not (100_000_0000 <= number <= 999_999_9999):
        return jsonify({'error': 'Number should be between 1000000000 and 9999999999'}), 400
    if username in registered_users.keys():
        if registered_users[username]['number'] == number:
            remove_user_from_register(username)
    prkey, pubkey = gen_pub_priv()
    add_user_to_register(username, number, pubkey)
    return jsonify({'private_key': prkey.export_key().decode('utf-8')}), 200


@app.route('/listusers', methods=['GET'])
def list_users():
    ret = ""
    for username, user_obj in registered_users.items():
        user_name = user_obj.name
        user_number = user_obj.number

        ret += f"Username: {user_name}, Number: {user_number}\n"
    return ret, 200


@app.route('/set_open_to_play', methods=['POST'])
def set_open_to_play():
    data = request.json
    print(data)

    # Validate input
    if 'username' not in data or 'open_to_play' not in data:
        return jsonify({'error': 'Missing username or open_to_play parameter'}), 400

    username = data['username'].lower()
    open_to_play = data['open_to_play'].lower() in ['true', '1', 't', 'y', 'yes']

    # Update user status
    if username in registered_users:
        # Assuming you have a way to update the open_to_play status in your user object
        registered_users[username].open_to_play = open_to_play
        return jsonify({'message': f"User {username}'s open to play status updated to {open_to_play}"}), 200
    else:
        return jsonify({'error': 'User not found'}), 404



if __name__ == '__main__':
    app.run(port=9999)
