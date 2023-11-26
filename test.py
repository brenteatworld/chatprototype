import socket
import threading
import sys
import tkinter as tk
from tkinter import simpledialog, scrolledtext

# Set up the client socket
HOST = '127.0.0.1'  # Replace with the server's IP address if different
PORT = 1989
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Function to handle receiving messages from the server
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                chat_text.config(state=tk.NORMAL)
                chat_text.insert(tk.END, message + "\n")
                chat_text.yview(tk.END)
                chat_text.config(state=tk.DISABLED)
            else:
                # An empty message usually means the server has closed the connection
                break
        except OSError:  # Possibly client has left the chat
            break

# Function to send messages to the server
def send_message():
    message = my_message.get()
    my_message.delete(0, tk.END)
    client_socket.sendall(message.encode('utf-8'))
    if message == "{quit}":
        client_socket.close()
        window.quit()

# Function to close the window and disconnect
def on_closing():
    my_message.set("{quit}")
    send_message()

# GUI setup
window = tk.Tk()
window.title("Chat Room")

# Ask for the user's name using a simple dialog
user_name = simpledialog.askstring("Name", "Enter your username:", parent=window)
if user_name:
    client_socket.sendall(user_name.encode('utf-8'))
else:
    window.quit()  # If no name was entered, exit the program

# Chat history text area
chat_text = scrolledtext.ScrolledText(window, state='disabled', height=15, width=50)
chat_text.pack(padx=10, pady=10)

# Message entry field
my_message = tk.Entry(window, width=48)
my_message.pack(padx=10, pady=5)

# Send button
send_button = tk.Button(window, text="Send", command=send_message)
send_button.pack()

# Start the thread for receiving messages
threading.Thread(target=receive_messages, daemon=True).start()

# Event to handle window closing
window.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI loop
window.mainloop()
