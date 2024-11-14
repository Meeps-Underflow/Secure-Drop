# add_contact.py
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from network import get_new_port_num
import os


def encrypt_data(data, recipient_public_key):
    public_key = serialization.load_pem_public_key(
        recipient_public_key,
        backend=default_backend()
    )
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data

def load_public_key(user_email):
    with open(f"{user_email}_public.pem", "rb") as key_file:
        return key_file.read()

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
    try:
        with open(f"{user_email}_contacts.json", "rb") as file:
            encrypted_contacts = file.read()
        user_private_key = load_private_key(user_email)
        decrypted_contacts = decrypt_data(encrypted_contacts, user_private_key)
        return json.loads(decrypted_contacts.decode('utf-8'))
    except FileNotFoundError:
        return {}

def save_contacts(contacts, user_email):
    recipient_public_key = load_public_key(user_email)
    contacts_json = json.dumps(contacts).encode('utf-8')
    encrypted_contacts = encrypt_data(contacts_json, recipient_public_key)
    with open(f"{user_email}_contacts.json", "wb") as file:
        file.write(encrypted_contacts)

def add_contact(user_email):
    full_name = ''
    email = input("Enter Email: ")
    port_number = ''

    # Check if Contact Exist as a User
    is_user_flag = False
    if os.path.exists('users.json'):
        # File exists, read the existing data
        with open('users.json', "r") as file:
            existing_data = json.load(file)
        # Search to see if email is associated to a user
        for users in existing_data:
            if users['email'].lower() == email:
                # User Found
                is_user_flag = True
                full_name = users['full_name']
                email = users['email']
                port_number = users['port_number']
    else:
        print("CASE ERROR: User.json was not found")
        exit(1)

    # Typed in Email was not associated to a Registered User
    if not is_user_flag:
        print("Email entered was not a valid user")
        return 
    
    # Load existing contacts
    existing_contacts = load_and_decrypt_contacts(user_email)
    # Add the new contact
    existing_contacts[email] = [full_name, port_number]
    # Save the updated contacts
    save_contacts(existing_contacts, user_email)
    print("Contact Added.")
