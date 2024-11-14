import socket
import json
import os
import asyncio

# Define server host and port
SERVER_HOST = '127.0.0.1'  # localhost
SERVER_PORT = 5500

global next_port
next_port=SERVER_PORT + 1

# Create socket object and bind to host and port
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((SERVER_HOST, SERVER_PORT))

# Allocate New Port For User
def get_new_port_num():
    global next_port
    if os.path.exists('users.json'):
        with open('users.json', "r") as file:
            data = json.load(file)
        # Get the last dictionary from the array
        last_dict = data[-1]
        # Retrieve the value associated with the key "port"
        port_value = last_dict.get("port_number")
        return int(port_value) + 1
    else:
        # File doesn't exist, initialize with an empty list
        return SERVER_PORT + 1
    

# Listen for connections in a loop
#NOT BEING USED ANYMORE SINCE EACH USER HAD THERE OWN PORT< WILL COMMUNICATE DIRECTLY
def start_server():
    pass
    # next_port = SERVER_PORT + 1
    # print(f"Server is listening on {SERVER_HOST}:{SERVER_PORT}")

    # while True:
    #     # Listen for incoming connections
    #     server_socket.listen(1)

    #     # Accept incoming connection
    #     client_socket, client_address = server_socket.accept()

    #     # Receive data from client
    #     encoded_data = client_socket.recv(1024)
    #     data = encoded_data.decode()

    #     # Assign port number
    #     if data == "port_number":
    #         client_socket.sendall(str(get_new_port_num()).encode())

    #     # Close client connection
    #     client_socket.close()

    # # Close server connection
    # server_socket.close()


# Will Listen to Request from other Users (Allows us to ping to see if users are online)
async def listen_to_responses(client_socket):
    client_socket.listen()


# After users login, will open socket and user assigned port
def connect_to_user_port(user_email):
    if os.path.exists('users.json'):
        # File exists, read the existing data
        with open('users.json', "r") as file:
            existing_data = json.load(file)
        # Find User that signed IN to Retrieve Port Number
        for users in existing_data:
            # If User is Found
            if users['email'].lower() == user_email:
                #Open User Socket
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.bind(('127.0.0.1', int(users['port_number'])))
                    asyncio.run(listen_to_responses(client_socket))
                    print("Port Connection Success to " + str(users['port_number']))
                except ConnectionRefusedError:
                    print(f"Connection to 127.0.0.1:{users['port_number']} refused. Make sure the server is running.")
                except Exception as e:
                    print(f"An error occurred in \"connect_to_user_port\": {e}")
        return client_socket
    

# Check if Socket Is Open
def is_socket_open(ip, port):
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set a timeout for the connection attempt (in seconds)
        client_socket.settimeout(1)
        # Attempt to connect to the server
        client_socket.connect((ip, port))

        # Connection successful
        # print(f"Socket to {ip}:{port} is open.")
        # client_socket.close()
        return True

    except (ConnectionRefusedError, TimeoutError):
        # Connection refused or timed out
        # print(f"Socket to {ip}:{port} is closed or unreachable.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

# Gets the port number of a user
def get_port_num(user_email):
    if os.path.exists('users.json'):
        # File exists, read the existing data
        with open('users.json', "r") as file:
            existing_data = json.load(file)
        # Find User that signed IN to Retrieve Port Number
        for user in existing_data:
            # If User is Found
            if user['email'].lower() == user_email:
                return int(user['port_number'])