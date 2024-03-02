from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import os.path
import base64


class Node:
    def __init__(self, secret_code, name=None):
        if name is None:
            name = "server"
        self.name = name
        self.rsa_filepath = f"{self.name}rsa_ley.bin"
        self.secret_code = secret_code
        if not os.path.isfile(self.rsa_filepath):
            self.create_rsa()
        self.pub_rsa = None
        self.priv_rsa = None
        self.load_key()

    def create_rsa(self):
        key = RSA.generate(2048)
        encrypted_key = key.export_key(passphrase=self.secret_code, pkcs=8,
                                       protection="scryptAndAES128-CBC",
                                       prot_params={'iteration_count': 131072})

        with open(self.rsa_filepath, "wb") as f:
            f.write(encrypted_key)

    def load_key(self):
        encoded_key = open(self.rsa_filepath, "rb").read()
        key = RSA.import_key(encoded_key, passphrase=self.secret_code)

        self.pub_rsa = key.publickey().export_key()
        self.priv_rsa = key.export_key()


class Player(Node):

    def __init__(self, secret_code, name):
        super().__init__(secret_code, name=name)
        self.serverkey = None

    def initial_receive(self, comms_data):
        private_key = RSA.import_key(self.priv_rsa)

        enc_session_key, nonce, tag, ciphertext = comms_data

        # Decrypt the session key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        self.serverkey = data

    def send_data(self, data: str):
        data = data.encode()

        aes_key = self.serverkey

        cipher = AES.new(aes_key, AES.MODE_OCB)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        assert len(cipher.nonce) == 15

        return tag, cipher.nonce, ciphertext

    def receive_data(self, data):
        tag, nonce, ciphertext = data
        cipher = AES.new(self.serverkey, AES.MODE_OCB, nonce=nonce)
        message = None
        try:
            message = cipher.decrypt_and_verify(ciphertext, tag)
            print("Message:", message.decode())
        except ValueError:
            print("The message was modified!")


class Server(Node):

    def __init__(self, secret_code):
        super().__init__(secret_code)
        self.players = {}

    def initial_send(self, name, rec_key):
        if name not in self.players.keys():
            player_key = self.add_player(name)
        else:
            player_key = self.players[name]
        data = player_key
        rec_key = RSA.import_key(rec_key)
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(rec_key)
        enc_session_key = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        # all of these values must be shared
        # need to add signing from server.
        return enc_session_key, cipher_aes.nonce, tag, ciphertext

    def add_player(self, name):
        pkey = get_random_bytes(16)
        self.players[name] = pkey
        return pkey

    def send_data(self, name, data: str):
        data = data.encode()

        aes_key = self.players[name]

        cipher = AES.new(aes_key, AES.MODE_OCB)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        assert len(cipher.nonce) == 15

        return tag, cipher.nonce, ciphertext

    def receive_data(self, name, data):
        tag, nonce, ciphertext = data
        cipher = AES.new(self.players[name], AES.MODE_OCB, nonce=nonce)
        message = None
        try:
            message = cipher.decrypt_and_verify(ciphertext, tag)
            print("Message:", message.decode())
        except ValueError:
            print("The message was modified!")


if __name__ == "__main__":
    p = Player("my name is bob", "Bob")
    s = Server("SECRET TOPS")
    back_to_player = s.initial_send(p.name, p.pub_rsa)
    p.initial_receive(back_to_player)
    s.receive_data("Bob",p.send_data("Hello there"))
    p.receive_data(s.send_data("Bob","From The Server"))
