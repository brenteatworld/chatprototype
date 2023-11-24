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

