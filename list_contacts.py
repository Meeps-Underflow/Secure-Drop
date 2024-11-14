# list_contacts.py

import json
import socket
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from network import is_socket_open

SERVER_HOST = '127.0.0.1' # localhost
SERVER_PORT = 5500

# Create socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def decrypt_data(encrypted_data, user_private_key):
    private_key = serialization.load_pem_private_key(
        user_private_key,
        password=None,
        backend=default_backend()
    )
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data

def load_private_key(user_email):
    with open(f"{user_email}_private.pem", "rb") as key_file:
        return key_file.read()

def load_and_decrypt_contacts(user_email):
    user_private_key = load_private_key(user_email)
    try:
        with open(f"{user_email}_contacts.json", "rb") as file:
            encrypted_contacts = file.read()
            decrypted_contacts = decrypt_data(encrypted_contacts, user_private_key)
            return json.loads(decrypted_contacts.decode('utf-8'))
    except FileNotFoundError:
        print("No contacts file found for this user.")
        return {}

def list_contacts(user_email):
    contacts = load_and_decrypt_contacts(user_email)
    if contacts:
        print("-----------\nCONTACTS:\n")
        # Check If All Contacts Are Online
        for email, nameAndPort in contacts.items():
            tempPort = nameAndPort[1]
            if is_socket_open('127.0.0.1', int(tempPort)):
                print("ONLINE: " + str(nameAndPort[0]) + ' (' +  str(email) + ")")
            else:
                print("OFFLINE: " + str(nameAndPort[0]) + ' (' +  str(email) + ")")
    else:
        print("No contacts found.")
