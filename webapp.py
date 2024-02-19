from flask import Flask, request, jsonify
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

app = Flask(__name__)

# A dictionary to store registered users' data (in memory, not persistent)
registered_users = {}


def gen_pub_priv():
    private_key = RSA.generate(2048, get_random_bytes)
    public_key = private_key.publickey()
    return private_key, public_key


def add_user_to_register(username: str, number, pub):
    registered_users[username.lower()] = {
        'number': number,
        'pkey': pub
    }


def remove_user_from_register(username: str):
    registered_users.pop(username.lower())


@app.route('/register', methods=['POST', 'GET'])
def register():
    data = {}
    try:
        data = request.args.to_dict()
        for k, v in data.items():
            print(k, v)
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
def list():
    ret = ""
    for k, v in registered_users.items():
        ret += f"{k},{v['number']}\n<br />"
    return ret, 200


if __name__ == '__main__':
    app.run(port=9999)
