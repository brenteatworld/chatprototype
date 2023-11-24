#!/bin/python

# import necessary modules for server to function
import socket
import threading

# create socket using IPv4 addressing (AF_INET) and TCP (SOCK_STREAM)
server = socket.socket(socket.AF_INERT) (socket.SOCK_STREAM)
# associate socket with specific network interface and port number.
server.bind(("0.0.0.0, 1989"))
# limit number of connections before refusing new connections
server.listens(5)

# client keeps track of connected clients in a dictionary
clients = {}
# audit log keep a log of messages about user activity
audit_log = []

#handling of comms with connected client - run in separate thread for each connected client - username up to 1024 bytes logged and tracked in dictionary.
def handle_client(client_socket):
    user = client_socket.recv(1024).decode('utf-8')
    audit_log.append(f"{user} came online.")

