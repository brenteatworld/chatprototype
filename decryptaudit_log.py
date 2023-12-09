#!/bin/python3

from cryptography.fernet import Fernet

# Load the encryption key
with open('secret.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# Function to decrypt a message
def decrypt_message(encrypted_message):
    try:
        decrypted_message = cipher_suite.decrypt(encrypted_message)
        return decrypted_message.decode('utf-8')
    except Exception as e:
        print(f"Error decrypting message: {e}")
        return None

# Decrypt and display the audit log
with open('audit_log.txt', 'rb') as file:
    for line in file:
        decrypted_message = decrypt_message(line.strip())
        if decrypted_message:
            print(decrypted_message)
