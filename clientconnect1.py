#!/bin/python3

import socket

def receive_messages(sock):
    """Handles receiving messages from the server."""
    while True:
        try:
            message = sock.recv(1024).decoe('utf-8')
            if message:
                print(message)
            else:
                # empty message means server has closed the connection.
                print("Disconnected from server!")
                break
        except Exception as e:
            print(f"Error receiving emessage: {e}")
            break

# client set up
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 1989) # server IP set to local host - port 1989 used in server script.
client_socket.connect(server_address)

# send hardcoded username - to be used in a later version of app
username = input("Enter your username: ") # send a username addition
client_socket.sendall(message.encode('utf-8'))
print("Connected to chat!")

# close connection
client_socket.close()