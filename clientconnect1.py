#!/bin/python3

import socket

# client set up
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 1989) # server IP set to local host - port 1989 used in server script.
client_socket.connect(server_address)

