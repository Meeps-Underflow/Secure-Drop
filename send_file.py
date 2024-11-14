# send_file.py

import os
import shutil
import socket
import sys
from list_contacts import load_and_decrypt_contacts  # Import the load_and_decrypt_contacts function to get the user's contacts
from network import is_socket_open  # Checks to see if a user is online
from network import get_port_num  # Gets the port number of a user
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def encrypt(message, keyPath):
    key = RSA.import_key(open(keyPath).read())
    cipher = PKCS1_OAEP.new(key)
    encrypted_message = cipher.encrypt(message.encode('latin-1'))
    return encrypted_message.decode('latin-1')

def send_message_and_receive_response(client_socket, message):
    client_socket.sendall(message.encode())
    response = client_socket.recv(1024)
    return response.decode()

def send_file(user_email):
    contact_email = input("Enter the email of the contact you want to send the file to: ")
    contact_list = load_and_decrypt_contacts(user_email)

    if contact_list == {}:
        print("Contact not found; you do not have any contacts.")
        return
    
    contact_found = False

    for email, name in contact_list.items():
        if email == contact_email:
            contact_found = True
            break
    
    if contact_found == False:
        print("Contact not found.");
        return

    contact_port_num = get_port_num(contact_email)
    is_contact_online = is_socket_open('127.0.0.1', contact_port_num)

    if not is_contact_online:
        print(f"{contact_email} is not online.")
        return

    response = None

    # Ping contact's port to get response (whether to accept the file or not)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', int(contact_port_num)))
        
        message = "AcceptFile " + user_email

        response = send_message_and_receive_response(client_socket, message)
        print(response)
        client_socket.close()
    except ConnectionRefusedError:
        print(f"Connection to 127.0.0.1:{contact_port_num} refused. Make sure the contact is online.")
    except Exception as e:
        print(f"An error occurred while getting response: {e}")

    if response == "Contact has declined the transfer request.":
        return

    file_location = input("Enter the file you would like to send: ")
    directory_path, file_name = os.path.split(file_location)
    file_path = os.path.join(directory_path, file_name)

    if not os.path.isfile(file_path):
        print("File not found.")
        return

    message = file_name + " "

    with open(file_path, 'r') as file:
        contents = file.read()
        message += contents

    encrypted_part = encrypt(message, contact_email + "_public.pem")
    encrypted_message = "FileTransfer " + encrypted_part

    # Ping contact's port to get response (whether file transfer was successful)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', int(contact_port_num)))
        client_socket.sendall(encrypted_message.encode())
        print("File has been successfully transferred.")
        client_socket.close()
    except ConnectionRefusedError:
        print(f"Connection to 127.0.0.1:{contact_port_num} refused. Make sure the contact is online.")
    except Exception as e:
        print(f"An error occurred while getting response: {e}")