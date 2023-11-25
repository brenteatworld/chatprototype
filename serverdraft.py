#!/bin/python

# import necessary modules for server to function
import socket
import threading

# create socket using IPv4 addressing (AF_INET) and TCP (SOCK_STREAM)
server = socket.socket(socket.AF_INET) (socket.SOCK_STREAM)
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

# while loop runs listen for messages from client - exits if client disconnects.
    while True:
        msg = client_socket.recv(1024).decode('utf-8')
        if msg =="EXIT":
            audit_log.append(f"{user} logged off.")
            del clients [user]
            client_socket.close()
            break
        for other_user, other_socket in clients.item():
            if other_user != user:
                other_socket.send(f"{user}: {msg}".encode('utf-8'))

    client_socket.close()

# server function accepts incoming connections. thread begins for each client. main server loop runs.
def run_server():
    while True:
        client, addr = server.accept()
        user = client.recv(1024).decode('utf-8')
        clients[user] = client
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()

run_server()