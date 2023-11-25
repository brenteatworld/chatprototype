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
            message = client_socket.recv(1024).decode('utf-8')
            if message:
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
    