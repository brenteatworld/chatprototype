#!/bin/python3

import socket
import threading

# initialise the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SQL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('0.0.0.0', 1989)
server_socket.bind(server_address)
server_socket.listen()

# store active clients - username: socket
clients = {}
# maintain audit log of messages
audit_log = []

# function handling broadcasting of messages to all clients
def broadcast_message(message):
    for client_socket in clients.values():
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message! {e}")

