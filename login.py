# login.py

import json  # Import the json module to work with JSON data
import getpass  # Import getpass for password hiding during input
from registration import hash_password  # Import the hash_password function for password verification

def user_login(attempt=1):
    if attempt > 3:  # Limit login attempts to 3 to prevent brute force attacks
        print("Max login attempts exceeded.\nExiting SecureDrop.")  # Notify user of exceeded attempts
        return False, None  # Return False and None to indicate login failure

    user_input = input("Enter user login: ").lower()  # Prompt for user login and convert to lowercase
    with open('users.json', 'r') as file:  # Open the user data file in read mode
        user_data = json.load(file)  # Load user data from the file
    for users in user_data:
        if users["email"].lower() == user_input:  # Compare input with stored email address
            password = getpass.getpass("Enter password for " + user_input + ": ")  # Securely prompt for password
            hashed_pass, salt = hash_password(password, bytes.fromhex(users["salt"]))  # Hash the input password for comparison
            if hashed_pass.hex() == users["password"]:  # Compare the hashed input password with the stored hashed password
                print("Login for " + user_input + " successful.")  # Notify user of successful login
                return True, user_input  # Return True and the user's email to indicate successful login
            else:
                continue

    else:
        print("Email and Password Combination Invalid.")  # Notify user of invalid login details

    return user_login(attempt + 1)  # Recursively call the login function to try again, incrementing the attempt count
