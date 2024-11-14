# secure_drop.py (run program from here for full test)

import os  # Import the os module to interact with the operating system
import threading  # Allows for creation of threads
from registration import register_user  # Import functions from the registration module
from login import user_login  # Import the user_login function from the login module
from secure_shell import init_secure_drop_shell  # Import the shell initializer for SecureDrop
from network import start_server # Import server loop from network.py


def main():
    user_registered = False  # Initialize a variable to keep track of the user's registration status

    if not os.path.exists('users.json'):  # Check if the 'users.json' file does not exist, indicating no registered users
        print("No users are registered with this client.")  # Inform the user that no users are registered
        while not user_registered:  # Loop until a user is registered
            register_new_user = input("Do you want to register a new user (y/n)? ").lower()  # Ask if the user wants to register a new user
            if register_new_user == 'y':  # If the user answers 'y'
                user_registered = register_user()  # Call the register_user function to register a new user
                if user_registered:  # If the user is successfully registered
                    print("Registration successful. Proceeding to login.")  # Inform the user that registration was successful
                else:  # If registration failed
                    print("Registration failed. Please try again.")  # Inform the user that registration failed
            else:  # If the user answers 'n' or any other response
                print("Exiting SecureDrop.")  # Print an exit message
                return  # Exit the function
    else:  # If the 'users.json' file exists
        register_new_user = input("Do you want to register a new user (y/n)? (If No, you'll be prompted to login) ").lower()  # Ask if the user wants to register a new user
        if register_new_user == 'y':  # If the user answers 'y'
            user_registered = register_user()  # Call the register_user function to register a new user
            if user_registered:  # If the user is successfully registered
                print("Registration successful. Proceeding to login.")  # Inform the user that registration was successful
            else:  # If registration failed
                print("Registration failed. Please try again.")  # Inform the user that registration failed
        user_registered = True  # Set the user's registration status to True
        print("Users are already registered with this client.")  # Inform the user that users are already registered
    
    # Attempt to log in
    login_successful, user_email = user_login()  # Attempt to login and receive login status and the user's email
    if user_registered and login_successful:  # If the user is registered and login is successful
        init_secure_drop_shell(user_email)  # Initialize the SecureDrop shell with the user's email

if __name__ == "__main__":  # If this script is executed as the main program
    server_thread = threading.Thread(target=start_server)
    server_thread.start()  # Start listening for connections on the server
    main()  # Call the main function to start the program
