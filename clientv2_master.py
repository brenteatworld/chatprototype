#!/bin/python3

import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import cryptography.fernet; from cryptography.fernet import Fernet
import sys

# high contrast settings
HIGH_CONTRAST_TEXT_COLOUR = "\033[97;100m" # white text on black background
NORMAL_TEXT_COLOUR = "\033[0m" # reset to default

# ask user if they would like to use accessibility features
use_high_contrast = input("Would you like to enable high contrast mode? (yes/no): ").strip().lower() == 'yes'

if use_high_contrast:
    sys.stdout.write(HIGH_CONTRAST_TEXT_COLOUR)
    sys.stdout.flush()

# generate / load encryption key
with open('secret.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# flag for controlling receive_messages thread.
running = True

# initial GUI setup
root = tk.Tk()
root.title("Chat Client")

# NSSpeechSynthesizer added for text-to-speech (macOS only)
class MacSpeechSynthesizer:
    def __init__(self):
        self.synthesizer = AppKit.NSSpeechSynthesizer.alloc().init()

    def speak(self, text):
        self.synthesizer.startSpeakingString_(text)

mac_speech_synthesizer = MacSpeechSynthesizer()

def speak(text):
    mac_speech_synthesizer.speak(text)

# prompt for accessibility options and username
def prompt_initial_options():
    username = simpledialog.askstring("Username", "Welcome to SecureChat. Enter your username:" parent=root)
    if not username:
        root.destroy() # quit application if no username is entered.
        return None, False, False
    
    high_contrast = simpledialog.askstring("High Contrast", "Enable High Contrast Mode? (y/n):", parent=root).strip().lower() == 'yes'
    tts = simpledialog.askstring("Text-To-Speech", "Enable Text-To-Speech? (y/n)", parent=root).strip().lower() == 'yes'

    return username, high_contrast, tts



def receive_messages(sock):
    global running
    while running:
        try:
            encrypted_message = sock.recv(1024)
            if encrypted_message:
                # decrypt message
                message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
                print(message)
            else:
                # empty message means server has closed the connection.
                print("Disconnected from server!")
                running = False
        except Exception as e:
            if running:
                print(f"Error receiving message: {e}")
            running = False
            break

def send_messages(sock):
    global running
    while running:
        try:
            message = input()
            if message.lower() == 'exit':
                running = False
                break
            # encrypt message before sending
            encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
            sock.sendall(encrypted_message)
        except Exception as e:
            print(f"Error sending message: {e}")
            running = False
            break

# client set up
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 1989) # server IP set to local host - port 1989 used in server script.
client_socket.connect(server_address)

# send hardcoded username - to be used in a later version of app
username = input("Enter your username: ") # send a username addition
client_socket.sendall(username.encode('utf-8'))
print("Connected to chat!")

# listen for messages from server
receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.start()

# sending messages function in main thread
send_messages(client_socket)

# close socket when False - disable further connections.
client_socket.shutdown(socket.SHUT_RDWR)
client_socket.close()

if use_high_contrast:
    sys.stdout.write(NORMAL_TEXT_COLOUR)
    sys.stdout.flush()

# close connection
receive_thread.join()

print("Closing chat")