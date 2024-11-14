# registration.py

import json
import os
import getpass
import hashlib
import socket
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from network import get_new_port_num

SERVER_HOST = '127.0.0.1'  # localhost
SERVER_PORT = 5500  # Default port

# Create socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def hash_password(password, salt=None):
    salt = salt or os.urandom(32)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed_password, salt

def generate_rsa_keys(email):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Serialize and save the private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(f"{email}_private.pem", "wb") as f:
        f.write(private_key_pem)

    # Serialize and save the public key
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(f"{email}_public.pem", "wb") as f:
        f.write(public_key_pem)

def register_user():
    print("User registration:")
    full_name = input("Enter Full Name: ")
    email = input("Enter Email Address: ").lower()
    password = getpass.getpass("Enter Password: ")
    confirm_password = getpass.getpass("Re-enter Password: ")

    if password != confirm_password:
        print("Passwords do not match. Please try again.")
        return False

    hashed_password, salt = hash_password(password)

    port_number = get_new_port_num()

    user_data = {
        'full_name': full_name,
        'email': email,
        'port_number': port_number,
        'password': hashed_password.hex(),
        'salt': salt.hex()
    }

    if os.path.exists('users.json'):
        # File exists, get the existing data
        with open('users.json', "r") as file:
            existing_data = json.load(file)
    else:
        # File doesn't exist, initialize with an empty list
        existing_data = []

    # Append the new user to the existing data
    existing_data.append(user_data)

    # Add new user data
    with open('users.json', 'w') as file:
        json.dump(existing_data, file, indent=4)

    # Generate RSA keys for the user
    generate_rsa_keys(email)

    print("Passwords Match.")
    print("User Registered.")
    return True
