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

# GUI setup for server control
root = tk.Tk()
root.title("SecureChat Server Control")
message_display = scrolledtext.ScrolledText(root, state='disabled', height=15, width=50)
message_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# function for updating GUI display
def update_display(message):
    message_display.config(state='normal')
    message_display.insert(tk.END, message + '\n')
    message_display.yview(tk.END)
    message_display.config(state='disabled')

# function for saving audit log
def save_audit_log():
    with open('audit_log.txt', 'ab') as file:
        for log_entry in audit_log:
            encrypted_log = cipher_suite.encrypt(str(log_entry).encode('utf-8'))
            file.write(encrypted_log + b'\n')

# function handling broadcasting of messages to all clients
def broadcast_message(message, sender_username="SecureChat Administrator"):
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
        joined_message = f"{username} has joined the chat room!"
        audit_log.append((username, "joined"))
        update_display(joined_message)
        print(joined_message)
        broadcast_message(joined_message)

        # listen for messages from clients
        while True:
            encrypted_message = client_socket.recv(1024)
            if encrypted_message:
                # decrypt received message
                message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
                received_message = f"{username}: {message}"
                update_display(received_message)
                print(received_message)
                audit_log.append((username, message))
                # broadcast to all clients
                broadcast_message(received_message)
            else:
                # client disconnects
                break
    except Exception as e:
        print(f"Error receiving message from {username}: {e}")
    finally:
        # clean up thread on disconnect
        client_socket.close()
        del clients[username]
        left_message = f"{username} has left the chat!"
        audit_log.append((username, "left"))
        update_display(left_message)
        print(left_message)
        broadcast_message(left_message)

# function to handle server shutdown
def shutdown_server():
    print("\nShutdown Initiated...")
    update_display("\nShutdown Initiated...")
    save_audit_log()
    for client_socket in clients.values():
        client_socket.close()
    server_socket.close()
    sys.exit(0)

# GUI command sending function
def send_command():
    command = command_entry.get().strip()
    command_entry.delete(0, tk.END)
    if command.lower() == 'exit':
        shutdown_server()
    else:
        update_display(f"Command entered: {command}")
        print(f"Command entered: {command}")

command_entry = tk.Entry(root, width=30)
command_entry.grid(row=1, column=0, padx=10, pady=10)

send_button = tk.Button(root, text="Send Command", command=send_command)
send_button.grid(row=1, column=1, padx=10, pady=10)

# Broadcast message function
def broadcast_from_gui():
    message = broadcast_entry.get().strip()
    broadcast_entry.delete(0, tk.END)
    if message:
        broadcast_message(f"Server: {message}")
        update_display(f"Server Broadcast: {message}")

broadcast_entry = tk.Entry(root, width=30)
broadcast_entry.grid(row=2, column=0, padx=10, pady=10)

broadcast_button = tk.Button(root, text="Broadcast", command=broadcast_from_gui)
broadcast_button.grid(row=2, column=1, padx=10, pady=10)

# main server loop function
def run_server():
    server_thread = threading.Thread(target=listen_for_connections)
    server_thread.start()
    root.mainloop()

def listen_for_connections():
    print("Server is running and listening for connections!")
    while True:
        # accept new connections
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address} has been established!")
            update_display(f"Connection from {client_address} established")

            # begin thread to handle client
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
        except Exception as e:
            print("Server stopped listening for connections.")
            break

# server script entry point
if __name__ == "__main__":
    run_server()
