from Crypto.PublicKey import RSA

# THIS PART ONLY NEEDS TO HAPPEN ONCE. So, Server needs to do it ONCE, Client needs to do it ONCE

secret_code = "Unguessable"  # this should be unique per client
key = RSA.generate(2048)  # this is your key
encrypted_key = key.export_key(passphrase=secret_code, pkcs=8,
                               protection="scryptAndAES128-CBC",
                               prot_params={'iteration_count': 131072})

with open("rsa_key.bin", "wb") as f:  # save that key to a file
    f.write(encrypted_key)
# END ONLY HAPPEN ONCE

# this is reloading the key, this is how you should do it from now on.
secret_code = "Unguessable"  # USER WOULD RE-ENTER PASSWORD
encoded_key = open("rsa_key.bin", "rb").read()
key = RSA.import_key(encoded_key, passphrase=secret_code)

pub = key.publickey().export_key()  # public key you can share. Must keep private safe

# so that was infrastructure, now we use the keys we have
priv = key.export_key()

with open("receiver.pem", "wb") as f:  # this just makes things easier, this should be cleaned-up
    f.write(pub)
with open("private.pem", "wb") as f:  # this just makes things easier, this should be cleaned-up
    f.write(priv)

# private and public keys are used for sending data. that is the underlying info for async communications
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

data = "I met aliens in UFO. Here is the map.".encode("utf-8")

recipient_key = RSA.import_key(open("receiver.pem").read())
session_key = get_random_bytes(16)

# Encrypt the session key with the public RSA key

cipher_rsa = PKCS1_OAEP.new(recipient_key)
enc_session_key = cipher_rsa.encrypt(session_key)

# Encrypt the data with the AES session key

cipher_aes = AES.new(session_key, AES.MODE_EAX)
ciphertext, tag = cipher_aes.encrypt_and_digest(data)

with open("encrypted_data.bin", "wb") as f:
    f.write(enc_session_key)
    f.write(cipher_aes.nonce)
    f.write(tag)
    f.write(ciphertext)

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

private_key = RSA.import_key(priv)

with open("encrypted_data.bin", "rb") as f:
    enc_session_key = f.read(private_key.size_in_bytes())
    nonce = f.read(16)
    tag = f.read(16)
    ciphertext = f.read()

# Decrypt the session key with the private RSA key
cipher_rsa = PKCS1_OAEP.new(private_key)
session_key = cipher_rsa.decrypt(enc_session_key)

# Decrypt the data with the AES session key
cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
data = cipher_aes.decrypt_and_verify(ciphertext, tag)
print(data.decode("utf-8"))
