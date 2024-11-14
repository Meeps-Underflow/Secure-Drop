# secure_shell.py

from add_contact import add_contact  # Import the add_contact function to allow adding new contacts
from list_contacts import list_contacts # import list contact function
from send_file import send_file # import send_file function
from network import connect_to_user_port
import socket
import json, os
import time
import threading
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

fileInput = False
socketConnection = None

def decrypt(message, keyPath):
    key = RSA.import_key(open(keyPath).read())
    cipher = PKCS1_OAEP.new(key)
    decrypted_message = cipher.decrypt(message.encode('latin-1'))
    return decrypted_message.decode('latin-1')

def init_secure_drop_shell(user_email):
    global fileInput

    print("Welcome to SecureDrop.\nType \"help\" For Commands.")  # Display a welcome message and prompt for commands
    user_socket = connect_to_user_port(user_email) # Open User Specific Socket

    def get_message_from_server():
        global fileInput
        global socketConnection

        time.sleep(2)

        while True:
            connection, address = user_socket.accept()
            data = connection.recv(1024)
            data = data.decode()

            socketConnection = connection

            if isinstance(data, str) and data.startswith("AcceptFile"):
                parts = data.split()
                sender = parts[-1]
                print("Contact " + sender + " is sending a file. Accept (y/n)?")
                fileInput = True
            elif isinstance(data, str) and data.startswith("FileTransfer"):
                connection.close()

                decrypted_info = data[13:]
                decrypted_data = decrypt(decrypted_info, user_email + "_private.pem")
                decrypted_parts = decrypted_data.split()
                decrypted_file_name = decrypted_parts[0]

                # Extract the contents of the message
                decrypted_contents = ' '.join(decrypted_parts[1:])
                
                with open('filesReceived/' + decrypted_file_name, 'w') as file:
                    file.write(decrypted_contents)

    thread = threading.Thread(target=get_message_from_server)
    thread.start()

    while True:  # Start an infinite loop to continuously accept user commands
        command = input("secure_drop> ").lower().strip()  # Prompt for a command, convert it to lowercase and strip whitespace
        
        if command == "help":  # Check if the command is "help"
            # Display the list of available commands to the user
            print("\"add\" -> Add a new contact\n\"list\" -> List all online contacts\n\"send\" -> Transfer file to contact\n\"exit\" -> Exit SecureDrop")
        elif command == "add":  # Check if the command is "add"
            add_contact(user_email)  # Call the add_contact function passing the user's email
        elif command == "list":  # Check if the command is "list"
            list_contacts(user_email)  # Call the list_contacts function to display all contacts
        elif command == "send":  # Check if the command is "send"
            send_file(user_email)  # Call the send_file function to initiate file transfer
        elif command == "exit":  # Check if the command is "exit"
            print("Exiting SecureDrop.")  # Print an exit message
            user_socket.close()
            time.sleep(2)
            break  # Break the loop to exit
        elif command == 'y' and fileInput == True:
            fileInput = False
            socketConnection.sendall("Contact has accepted the transfer request.".encode())
            socketConnection.close()
        elif command == 'n' and fileInput == True:
            fileInput = False
            socketConnection.sendall("Contact has declined the transfer request.".encode())
            socketConnection.close()
        else:  # If the command doesn't match any known commands
            print("Unknown command. Type \"help\" for commands.")  # Inform the user that the command is unrecognized
