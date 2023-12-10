#!/bin/python3

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import cryptography.fernet; from cryptography.fernet import Fernet
import sys

# encryption key
key = Fernet.generate_key()

# write server generated key to file
with open('secret.key', 'wb') as key_file:
    key_file.write(key)

with open('secret.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# initialise the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('0.0.0.0', 1989)
server_socket.bind(server_address)
server_socket.listen()

# store active clients - username: socket
clients = {}
# maintain audit log of messages
audit_log = []

# gui set up for server control
root = tk.Tk()
root.title("Server Control")
message_display = scrolledtext.ScrolledText(root, state='disabled', height=15, width=50)
message_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# gui window for which clients are connected
clients_window = tk.Toplevel(root)
clients_window.title("Connected Clients")
clients_list = tk.Listbox(clients_window, width=30, height=15)
clients_list.pack(padx=10, pady=10)

# function handling broadcasting of messages to all clients
def broadcast_message(message, sender_username=None):
    for username, client_socket in list(clients.items()):
        if username != sender_username:
            try:
                encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
                client_socket.send(encrypted_message)
            except Exception as e:
                print(f"Error sending message to {username}: {e}")
                client_socket.close()
                del clients[username]

# function handling each client connection
def handle_client(client_socket):
    try:
        # receive username from client and print message
        username = client_socket.recv(1024).decode('utf-8')
        clients[username] = client_socket
        audit_log.append((username, "has joined"))
        print(f"{username} has joined the chat room!")
        broadcast_message(f"{username} has joined the chat room!")

        # listen for messages from clients
        while True:
            encrypted_message = client_socket.recv(1024)
            if encrypted_message:
                # decrypt received message
                message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
                print(f"Received message from {username}: {message}")
                # broadcast to all clients
                broadcast_message(f"{username}: {message}")
            else:
                # client disconnects
                break
    except Exception as e:
        print(f"Error receiving message from {username}: {e}")
    finally:
        # clean up thread on disconnect
        client_socket.close()
        del clients[username]
        audit_log.append((username, "left the chat"))
        print(f"{username} has left the chat!")
        broadcast_message(f"{username} has left the chat!")

# main server loop function
def run_server():
    print("Server is running and listening for connections!")
    while True:
        # accept new connections
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address} has been established!")

        # begin thread to handle client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.daemon = True
        client_thread.start()

# server script entry point
if __name__ == "__main__":
    run_server()
