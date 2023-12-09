#!/bin/python3

import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import AppKit
import cryptography.fernet; from cryptography.fernet import Fernet

# generate / load encryption key
with open('secret.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# flag for controlling receive_messages thread.
running = True

# GUI setup
root = tk.Tk()
root.title("Chat Client")

# NSSpeechSynthesizer for text-to-speech
class MacSpeechSynthesizer:
    def __init__(self):
        self.synthesizer = AppKit.NSSpeechSynthesizer.alloc().init()

    def speak(self, text):
        self.synthesizer.startSpeakingString_(text)

mac_speech_synthesizer = MacSpeechSynthesizer()

def speak(text):
    mac_speech_synthesizer.speak(text)

# Prompt for accessibility options and username
def prompt_initial_options():
    username = simpledialog.askstring("Username", "Welcome to SecureChat. Enter your username:", parent=root)
    if not username:
        root.destroy()  # Quit application if no username is entered
        return None, False, False

    high_contrast = simpledialog.askstring("High Contrast", "Enable high contrast mode? (yes/no):", parent=root).strip().lower() == 'yes'
    tts = simpledialog.askstring("Text-to-Speech", "Enable text-to-speech? (yes/no):", parent=root).strip().lower() == 'yes'
    
    return username, high_contrast, tts

username, high_contrast, enable_tts = prompt_initial_options()

# If username prompt was cancelled, quit the application
if username is None:
    exit(0)

if high_contrast:
    root.configure(bg="white")
    fg_color = "black"
    bg_color = "white"
    select_bg_color = "gray"
    select_fg_color = "white"
else:
    root.configure(bg="black")
    fg_color = "white"
    bg_color = "black"
    select_bg_color = "blue"
    select_fg_color = "yellow"

# Common button text color
button_fg_color = "black"

# Chat display area
chat_display = scrolledtext.ScrolledText(root, state='disabled', fg=fg_color, bg=bg_color, selectbackground=select_bg_color, selectforeground=select_fg_color)
chat_display.grid(row=0, column=0, columnspan=3)

# Message input area
message_entry = tk.Entry(root, width=50, fg=fg_color, bg=bg_color)
message_entry.grid(row=1, column=0, padx=5, pady=5)

def send_message(event=None):
    global running
    message = message_entry.get()
    message_entry.delete(0, tk.END)
    if message.lower() == 'exit':
        running = False
        root.quit()
        return
    # encrypt message before sending
    encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
    client_socket.sendall(encrypted_message)

# Send button
send_button = tk.Button(root, text="Send", command=send_message, fg=button_fg_color, bg=bg_color)
send_button.grid(row=1, column=1, padx=5, pady=5)

# Exit button
def exit_chat():
    global running
    running = False
    root.quit()

exit_button = tk.Button(root, text="Exit Chat", command=exit_chat, fg=button_fg_color, bg=bg_color)
exit_button.grid(row=1, column=2, padx=5, pady=5)

# Bind enter key to send message
root.bind('<Return>', send_message)

def update_chat_display(message):
    chat_display.config(state='normal')
    chat_display.insert(tk.END, message + '\n')
    chat_display.yview(tk.END)
    chat_display.config(state='disabled')
    if enable_tts:
        speak(message)

def receive_messages(sock):
    global running
    while running:
        try:
            encrypted_message = sock.recv(1024)
            if encrypted_message:
                # decrypt message
                message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
                update_chat_display(message)
            else:
                # empty message means server has closed the connection.
                update_chat_display("Disconnected from server!")
                running = False
        except Exception as e:
            if running:
                update_chat_display(f"Error receiving message: {e}")
            running = False
            break

# client set up
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 1989) # server IP set to local host - port 1989 used in server script.
client_socket.connect(server_address)

# send username
client_socket.sendall(username.encode('utf-8'))
update_chat_display(f"Connected to chat as {username}!")

# listen for messages from server
receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.start()

# Start the GUI loop
root.mainloop()

# close socket when False - disable further connections.
client_socket.shutdown(socket.SHUT_RDWR)
client_socket.close()

# close connection
receive_thread.join()
